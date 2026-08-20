#!/usr/bin/env python3
"""
Build a Flipper .nfc dump that holds an NDEF URL record.

Takes a known-good .nfc off the Flipper as a template and rewrites only the
user-memory pages. Header, UID, signature, and config tail are left alone,
which is what keeps the NFC app from rejecting the file.

  usage: make_nfc.py <template.nfc> <url> <out.nfc>
"""
import re, sys

# NDEF URI prefix codes, so the URL costs one byte instead of eight
PREFIX = {"https://www.": 0x02, "http://www.": 0x01, "https://": 0x04, "http://": 0x03}


def ndef_url(url):
    code, rest = 0x00, url
    for p, c in PREFIX.items():
        if url.startswith(p):
            code, rest = c, url[len(p):]
            break
    payload = bytes([code]) + rest.encode()
    record = bytes([0xD1, 0x01, len(payload), 0x55]) + payload   # MB|ME|SR, well-known, 'U'
    tlv = bytes([0x03, len(record)]) + record + bytes([0xFE])    # NDEF TLV + terminator
    return tlv


def build(template, url, out):
    src = open(template).read()
    pages = {int(m.group(1)): m.group(2)
             for m in re.finditer(r"^Page (\d+): (.+)$", src, re.M)}
    total = max(pages) + 1
    if total < 45:
        raise SystemExit(f"template has only {total} pages, too small for a URL")

    tlv = ndef_url(url)
    user_first, user_last = 4, min(129, total - 6)   # leave the config tail alone
    capacity = (user_last - user_first + 1) * 4
    if len(tlv) > capacity:
        raise SystemExit(f"URL needs {len(tlv)} bytes, card holds {capacity}")

    data = tlv + bytes(capacity - len(tlv))
    for i in range(user_first, user_last + 1):
        chunk = data[(i - user_first) * 4:(i - user_first) * 4 + 4]
        pages[i] = " ".join(f"{b:02X}" for b in chunk)

    result = re.sub(r"^Page (\d+): .+$",
                    lambda m: f"Page {m.group(1)}: {pages[int(m.group(1))]}",
                    src, flags=re.M)
    open(out, "w").write(result)

    dev = re.search(r"^Device type: (.+)$", src, re.M)
    model = re.search(r"^NTAG/Ultralight type: (.+)$", src, re.M)
    print(f"  device type   {dev.group(1) if dev else '?'}")
    print(f"  model         {model.group(1) if model else '?'}")
    print(f"  pages         {total}, rewrote {user_first}..{user_last}")
    print(f"  ndef          {len(tlv)} bytes for {url}")
    print(f"  wrote         {out}")
    return result


def verify(path, expect):
    """Parse the file back the way a reader would, to prove the URL survived."""
    src = open(path).read()
    raw = bytearray()
    for m in re.finditer(r"^Page (\d+): (.+)$", src, re.M):
        if int(m.group(1)) >= 4:
            raw += bytes(int(b, 16) for b in m.group(2).split())
    if raw[0] != 0x03:
        return print("  VERIFY FAILED: no NDEF TLV at page 4")
    rec = raw[2:2 + raw[1]]
    plen = rec[2]
    payload = rec[4:4 + plen]
    inv = {v: k for k, v in PREFIX.items()}
    url = inv.get(payload[0], "") + payload[1:].decode()
    print(f"  decoded back  {url}")
    print("  VERIFIED" if url == expect else f"  MISMATCH, expected {expect}")


if __name__ == "__main__":
    t, url, out = sys.argv[1], sys.argv[2], sys.argv[3]
    build(t, url, out)
    verify(out, url)
