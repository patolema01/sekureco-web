"""Imagen para compartir (Open Graph / Twitter): assets/og/sekureco-og.png, 1200 × 630.

El escudo y SEKURECO (con la primera E y los brazos del K en teal, como en la web) sobre el azul
de la paleta, y debajo la frase del hero en Archivo. Arma un SVG con las piezas que genera
tools/header.py (las mismas de la intro) y lo rasteriza con Chromium (Playwright), con la fuente
del propio sitio. El sitio no carga nada de esto: solo publica el PNG.

Proporciones: margen de 89 px (Fibonacci) a los lados; el bloque arranca en la línea de 38,2 %
del alto; la palabra mide la mitad del escudo, como en la intro y el header; la frase va en el
paso de 72 px de la escala del sitio, una línea por oración (sin huérfanas); si la más larga no
entra entre los márgenes, se achica lo justo.

Uso (con Playwright y fonttools: ~/.venvs/sekureco-tools):
    ~/.venvs/sekureco-tools/bin/python tools/og.py
Regenera tools/build/ con header.py antes de armar la imagen.
"""
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tools" / "build"
OUT = ROOT / "assets" / "og" / "sekureco-og.png"
ANCHO, ALTO = 1200, 630

NAVY, MIST, TEAL_L, BAJADA = "#0F2032", "#EEF3F3", "#3FB8B1", "#C4D1D6"
MARGEN = 89                      # Fibonacci
ESCUDO = 144                     # alto del escudo (Fibonacci); la palabra mide la mitad
FRASE = "Cámaras, alarmas y redes. Un solo sistema seguro."
DOMINIO = "sekureco.ar"

subprocess.run([sys.executable, str(ROOT / "tools" / "header.py")], check=True, stdout=subprocess.DEVNULL)
escudo = (BUILD / "header-shield.svg").read_text()
palabra = (BUILD / "intro-wordmark.svg").read_text()
fuente = (ROOT / "assets" / "fonts" / "archivo.woff2").as_uri()

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Archivo"; src: url("{fuente}") format("woff2"); font-weight: 100 900; font-stretch: 62% 125%; }}
html, body {{ margin: 0; width: {ANCHO}px; height: {ALTO}px; overflow: hidden; }}
body {{ background: {NAVY}; color: {MIST}; font-family: "Archivo"; position: relative; }}
.la {{ fill: {TEAL_L}; }}
.la-s {{ stroke: {TEAL_L}; }}
.lockup {{ position: absolute; left: {MARGEN}px; top: {round(ALTO * 0.382 - ESCUDO)}px;
          display: flex; align-items: center; gap: {round(ESCUDO * .3)}px; }}
.logo-shield {{ height: {ESCUDO}px; width: auto; display: block; }}
.intro-wm-svg {{ height: {ESCUDO // 2}px; width: auto; display: block; overflow: visible; }}
h1 {{ position: absolute; left: {MARGEN}px; top: {round(ALTO * 0.382) + 34}px; margin: 0;
      font-size: 72px; font-stretch: 125%; font-weight: 620; line-height: 1.1; letter-spacing: -0.01em;
      max-width: {ANCHO - 2 * MARGEN}px; }}
.dom {{ position: absolute; left: {MARGEN}px; bottom: 55px; font-size: 27.5px; font-weight: 500;
        color: {TEAL_L}; letter-spacing: .02em; }}
.raya {{ position: absolute; left: 0; right: 0; bottom: 0; height: 8px; background: {TEAL_L}; }}
</style></head><body>
<div class="lockup">{escudo}{palabra}</div>
<h1>{FRASE.replace(". ", ".<br>")}</h1>
<div class="dom">{DOMINIO}</div>
<div class="raya"></div>
</body></html>"""

OUT.parent.mkdir(parents=True, exist_ok=True)
tmp = BUILD / "og.html"
tmp.write_text(html, encoding="utf-8")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": ANCHO, "height": ALTO}, device_scale_factor=1)
    pg.goto(tmp.as_uri())
    pg.evaluate("document.fonts.ready")
    # una línea por oración: si la más larga no entra entre los márgenes a 72 px, se achica lo justo
    tam = pg.evaluate("""(max) => {
        const h = document.querySelector('h1'); h.style.whiteSpace = 'nowrap';
        const r = document.createRange(); let ancho = 0;
        for (const n of h.childNodes) if (n.nodeType === 3) { r.selectNodeContents(n); ancho = Math.max(ancho, r.getBoundingClientRect().width); }
        const t = Math.min(72, Math.floor(72 * max / ancho));
        h.style.fontSize = t + 'px'; return t; }""", ANCHO - 2 * MARGEN)
    pg.screenshot(path=str(OUT), omit_background=False)
    b.close()
print(f"{OUT.relative_to(ROOT)}: {ANCHO}×{ALTO}, frase a {tam} px")
