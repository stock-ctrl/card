#!/usr/bin/env python3
"""
Flipper Zero CLI over serial. Pull, push, verify.

Hard-won rules baked in:
  - qFlipper holds the port exclusively, so quit it first.
  - Open with dtr/rts False, then assert them, or the CLI stays silent.
  - `storage write_chunk` MUST end with \\r alone. A trailing \\n becomes the
    first byte of the payload and silently corrupts the file.
"""
import hashlib, re, subprocess, sys, time
import serial

PORT = "/dev/cu.usbmodemflip_Yubila1"
PROMPT = b">: "


def free_port():
    subprocess.run(["osascript", "-e", 'quit app "qFlipper"'],
                   capture_output=True)
    time.sleep(1)


def connect():
    s = serial.Serial()
    s.port, s.baudrate, s.timeout = PORT, 115200, 3
    s.dtr = False
    s.rts = False
    s.open()
    s.dtr = True
    s.rts = True
    time.sleep(0.4)
    s.reset_input_buffer()
    s.write(b"\r")
    s.read_until(PROMPT)
    return s


def cmd(s, line, wait=PROMPT, delay=0.1):
    s.write(line.encode() + b"\r")
    time.sleep(delay)
    return s.read_until(wait).decode(errors="replace")


def read_file(s, path):
    out = cmd(s, f'storage read "{path}"', delay=0.5)
    m = re.search(r"Size: (\d+)\r?\n", out)
    if not m:
        raise RuntimeError(f"could not read {path}:\n{out}")
    body = out[m.end():]
    return body.rsplit(">:", 1)[0].rstrip("\r\n").encode()


def write_file(s, path, data):
    cmd(s, f'storage remove "{path}"')
    # the one command that must not carry a newline
    s.write(f'storage write_chunk "{path}" {len(data)}'.encode() + b"\r")
    s.read_until(b"Ready")
    time.sleep(0.2)
    s.write(data)
    time.sleep(0.6)
    s.read_until(PROMPT)
    out = cmd(s, f'storage md5 "{path}"', delay=0.4)
    remote = re.search(r"([0-9a-f]{32})", out)
    local = hashlib.md5(data).hexdigest()
    ok = bool(remote) and remote.group(1) == local
    print(f"  local  md5 {local}")
    print(f"  remote md5 {remote.group(1) if remote else 'NONE'}")
    print("  VERIFIED" if ok else "  MISMATCH, do not trust this file")
    return ok


if __name__ == "__main__":
    free_port()
    s = connect()
    try:
        action = sys.argv[1]
        if action == "ls":
            print(cmd(s, 'storage list /ext/nfc', delay=0.5))
        elif action == "pull":
            data = read_file(s, sys.argv[2])
            open(sys.argv[3], "wb").write(data)
            print(f"pulled {len(data)} bytes -> {sys.argv[3]}")
        elif action == "push":
            data = open(sys.argv[2], "rb").read()
            print(f"pushing {len(data)} bytes -> {sys.argv[3]}")
            sys.exit(0 if write_file(s, sys.argv[3], data) else 1)
    finally:
        s.close()
