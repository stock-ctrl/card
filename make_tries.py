#!/usr/bin/env python3
"""Build try/a.html and try/b.html: two ways to handle the operator credential."""
import base64, pathlib

d = pathlib.Path(__file__).parent
base = (d / "index.template.html").read_text()

# both options drop the "I also own and operate" afterthought framing
NOTE_OLD = '''    <p>I also own and operate a Crumbl Cookies franchise here locally.</p>
    <p>So I am not selling software from the outside. I run a business day to day, with the same payroll, scheduling, and inventory headaches you have.</p>
    <p>And the systems I sell are the same ones my store runs on. They get beat on every day in a real business, and they hold up.</p>'''
NOTE_NEW = '''    <p>I am not selling software from the outside. I run a business day to day, with the same payroll, scheduling, and inventory headaches you have.</p>
    <p>The systems I sell are the same ones my store runs on. They get beat on every day in a real business, and they hold up.</p>'''

# ---------- A: credential sits in the hero, right under the name ----------
a = base.replace(NOTE_OLD, NOTE_NEW)
a = a.replace('<p class="role">Founder</p>',
              '<p class="role">Founder</p>\n    <p class="role cred">Crumbl Cookies franchise owner</p>')
a = a.replace('''.tagline{''', '''.cred{color:var(--on-forest-muted); margin-top:7px;}

.tagline{''')
a = a.replace("<title>Stock Curtis, Stockwell Media Co</title>",
              "<title>Option A, credential up top</title>")

# ---------- B: a dedicated credentials strip under the buttons ----------
b = base.replace(NOTE_OLD, NOTE_NEW)
b = b.replace('''  <p class="eyebrow">What I build</p>''', '''  <div class="creds">
    <div class="cred-row"><span>Operator</span><p>Crumbl Cookies franchise owner</p></div>
    <div class="cred-row"><span>Studio</span><p>Stockwell Media Co, founder</p></div>
    <div class="cred-row"><span>Based</span><p>Springfield, Missouri</p></div>
  </div>

  <p class="eyebrow">What I build</p>''')
b = b.replace('''.eyebrow{''', '''.creds{
  margin:34px 0 0; border:1px solid var(--border);
  border-radius:14px; background:var(--cream-warm); overflow:hidden;
}
.cred-row{display:flex; gap:14px; align-items:baseline; padding:13px 17px; border-top:1px solid var(--border);}
.cred-row:first-child{border-top:none;}
.cred-row span{
  font-family:'JBMono',monospace; font-size:10px; font-weight:500;
  letter-spacing:0.15em; text-transform:uppercase; color:var(--sage);
  flex:none; width:74px;
}
.cred-row p{margin:0; font-size:15.5px; color:var(--ink);}

.eyebrow{''')
b = b.replace("<title>Stock Curtis, Stockwell Media Co</title>",
              "<title>Option B, credentials block</title>")

jost = base64.b64encode((d / "fonts/jost.woff2").read_bytes()).decode()
mono = base64.b64encode((d / "fonts/mono.woff2").read_bytes()).decode()
for name, html in (("a", a), ("b", b)):
    html = html.replace("__JOST_B64__", jost).replace("__MONO_B64__", mono)
    (d / "try" / f"{name}.html").write_text(html)
    print(f"built try/{name}.html, {len(html.encode()) // 1024} KB")
