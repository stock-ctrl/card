# stock-card

Tap-to-open digital business card for Stock Curtis, Stockwell Media Co.
Written to NFC cards as a URL record and opened on the other person's phone.

- `index.template.html` is the source. `index.html` is the build with fonts inlined.
- Rebuild after editing the template:

      python3 build.py

- `contact.vcf` is what the "Save my contact" button hands to their phone.
- Phone number is not in the served HTML. The Call and Text links are assembled
  at runtime and the number itself only ships inside `contact.vcf`.
