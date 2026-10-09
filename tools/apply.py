"""Mete lo generado en tools/build/ dentro de index.html, 404.html y assets/styles.css.
Uso: python3 tools/apply.py (después de intro.py y header.py)"""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "tools" / "build"
intro_html = (B / "intro.html").read_text()
_wm = (B / "header-wordmark.svg").read_text()
intro_html = intro_html.replace("{{WORDMARK}}", _wm.replace('class="logo-wm"', 'class="intro-wm-svg"', 1))
intro_css = (B / "intro.css").read_text()
shield = (B / "header-shield.svg").read_text()
wm = (B / "header-wordmark.svg").read_text()

for name in ["index.html", "404.html"]:
    p = ROOT / name
    h = p.read_text()
    if name == "index.html":
        h, n = re.subn(r'<div class="intro-ov".*?<span class="intro-skip">.*?</span>\n</div>\n', lambda m: intro_html + "\n", h, count=1, flags=re.S)
        assert n == 1, "no encontré la intro en index.html"
    h, n1 = re.subn(r'<svg class="logo-shield".*?</svg>', lambda m: shield, h, count=1, flags=re.S)
    h, n2 = re.subn(r'<svg class="logo-wm".*?</svg>', lambda m: wm, h, count=1, flags=re.S)
    assert n1 == 1 and n2 == 1, f"no encontré el logo del header en {name}"
    p.write_text(h)

css = ROOT / "assets" / "styles.css"
c = css.read_text()
a = c.index("/* ---------- intro:")
b = c.index("/* va al final para ganarle")
css.write_text(c[:a] + intro_css + c[b:])
print("aplicado")
