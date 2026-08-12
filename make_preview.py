#!/usr/bin/env python3
"""Build preview.html: the live card plus a toggle bar for candidate color treatments."""
import base64, pathlib

d = pathlib.Path(__file__).parent
html = (d / "index.template.html").read_text()
for token, font in (("__JOST_B64__", "jost.woff2"), ("__MONO_B64__", "mono.woff2")):
    html = html.replace(token, base64.b64encode((d / "fonts" / font).read_bytes()).decode())

VARIANT_CSS = """
/* ============ candidate treatments, toggled from the bar ============ */

/* B. crumbl block on a forest ground */
html.vB .note{background:var(--forest); border-color:var(--forest); border-left-color:var(--sage-light);}
html.vB .note p{color:var(--cream);}
html.vB .note p + p{color:var(--on-forest-muted);}

/* D. sage rule under each heading */
html.vD .eyebrow{position:relative; margin-bottom:24px;}
html.vD .eyebrow::after{
  content:""; position:absolute; left:0; bottom:-9px;
  width:32px; height:2px; background:var(--sage);
}
html.vD .item:first-of-type, html.vD .proof:first-of-type{border-top-color:transparent;}

/* ============ the toggle bar itself, not part of the card ============ */
#vbar{
  position:fixed; left:0; right:0; bottom:0; z-index:99;
  background:rgba(13,20,16,0.94); backdrop-filter:blur(8px);
  padding:11px 12px calc(11px + env(safe-area-inset-bottom));
  display:flex; gap:7px; flex-wrap:wrap; justify-content:center;
}
#vbar button{
  font-family:'JBMono',monospace; font-size:10.5px; font-weight:500;
  letter-spacing:0.11em; text-transform:uppercase;
  color:var(--on-forest-muted); background:transparent;
  border:1px solid rgba(244,239,228,0.26); border-radius:999px;
  padding:9px 13px; cursor:pointer; -webkit-tap-highlight-color:transparent;
}
#vbar button[aria-pressed="true"]{
  background:var(--sage-light); border-color:var(--sage-light); color:var(--forest);
}
#vbar button.reset{border-style:dashed;}
.wrap{padding-bottom:110px !important;}
"""

BAR = """
<div id="vbar">
  <button data-v="vB" aria-pressed="false">Crumbl panel</button>
  <button data-v="vD" aria-pressed="false">Sage rules</button>
  <button class="reset" aria-pressed="false">Reset</button>
</div>
<script>
(function(){
  var root = document.documentElement;
  document.querySelectorAll('#vbar button').forEach(function(b){
    b.addEventListener('click', function(){
      if (b.classList.contains('reset')){
        ['vB','vD'].forEach(function(v){ root.classList.remove(v); });
        document.querySelectorAll('#vbar button').forEach(function(o){ o.setAttribute('aria-pressed','false'); });
        return;
      }
      var on = root.classList.toggle(b.dataset.v);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  });
})();
</script>
"""

html = html.replace("</style>", VARIANT_CSS + "\n</style>", 1)
html = html.replace("<title>Stock Curtis, Stockwell Media Co</title>",
                    "<title>Card color options</title>", 1)
html = html.rstrip() + "\n" + BAR
(d / "preview.html").write_text(html)
print(f"built preview.html, {len(html.encode()) // 1024} KB")
