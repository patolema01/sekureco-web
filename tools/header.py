"""Header: escudo (link al inicio) + SEKURECO que se cierra en ">≡", el botón del menú.

Genera:
  build/header-shield.svg     escudo
  build/header-wordmark.svg   SEKURECO dentro de una "ventana" (clipPath) que se cierra, y el "≡"
  build/header.css            la coreografía del cierre, el parpadeo del "≡", la interacción del
                              menú y el alto del logo (apply.py lo mete en styles.css)

El cierre ("ventana"): toda la palabra se desplaza a la izquierda como un bloque hasta que los
brazos del K quedan donde va el ">". Se ve a través de una ventana: el borde izquierdo está fijo
en el borde izquierdo del ">" final (S, E y el palo del K salen por ahí) y el derecho es un telón
que avanza de derecha a izquierda tapando U, R, E, C, O y frena antes que el bloque. El "<" viaja
con el bloque y rueda 180° (antihorario) en el último 60 % del viaje hasta ser ">". Al asentarse,
el cursor arma el "≡" titilando: 1 barra, apagado, 2 barras, apagado, 3 barras fijas.
"""
import math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tools" / "build"; BUILD.mkdir(exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
shield, glyph_path, TRACK, STK = brand.shield, brand.glyph_path, brand.TRACK, brand.STK

# ---------- SEKURECO ----------
capH = 1536
letters, arms_d = [], None
x = 0; kx = None
for i, ch in enumerate("SEKURECO"):
    d, w, b = glyph_path(ch, x)
    if ch == "K":
        kx = x
        stem = [(192, 0), (192, 1536), (384, 1536), (384, 0)]
        # brazos del K como chevron limpio: las dos diagonales se extienden hasta juntarse
        # en punta (522, 784). El tramo horizontal que une los brazos con el asta va
        # aparte (join): se desvanece al empezar el cierre, así el ">" final no arrastra un "-".
        arms = [(522, 784), (1632, 1536), (1920, 1536), (832, 784), (1952, 0), (1664, 0)]
        join = [(384, 704), (640, 704), (640, 864), (384, 864)]
        stem_d = "M" + "L".join(f"{px + x:.0f} {-py}" for px, py in stem) + "Z"
        arms_d = "M" + "L".join(f"{px + x:.0f} {-py}" for px, py in arms) + "Z"
        join_d = "M" + "L".join(f"{px + x:.0f} {-py}" for px, py in join) + "Z"
    else:
        letters.append(d)
    x += w + TRACK
ww = x - TRACK
pad = 90
vb_y, vb_h = -capH - pad, capH + 2 * pad
vb_x, vb_w = -pad, ww + 2 * pad


def contorno(pts, w, limite=4):
    """Contorno de un polígono con trazo de ancho w y uniones en inglete (como stroke-linejoin:
    miter, stroke-miterlimit 4 de SVG). Sirve para saber hasta dónde se dibuja de verdad."""
    n = len(pts)
    def dentro(px, py):
        c = False
        for i in range(n):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1): c = not c
        return c
    def uni(ax, ay):
        l = math.hypot(ax, ay); return ax / l, ay / l
    (x1, y1), (x2, y2) = pts[0], pts[1]
    ex, ey = uni(x2 - x1, y2 - y1)
    s = -1 if dentro((x1 + x2) / 2 + ey, (y1 + y2) / 2 - ex) else 1      # hacia afuera
    h, out = w / 2, []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        e1, e2 = uni(p1[0] - p0[0], p1[1] - p0[1]), uni(p2[0] - p1[0], p2[1] - p1[1])
        n1, n2 = (s * e1[1], -s * e1[0]), (s * e2[1], -s * e2[0])
        a = (p1[0] + n1[0] * h, p1[1] + n1[1] * h); b = (p1[0] + n2[0] * h, p1[1] + n2[1] * h)
        cr = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(cr) < 1e-9: out.append(a); continue
        t = ((b[0] - a[0]) * e2[1] - (b[1] - a[1]) * e2[0]) / cr
        m = (a[0] + e1[0] * t, a[1] + e1[1] * t)
        out += [m] if math.hypot(m[0] - p1[0], m[1] - p1[1]) / h <= limite else [a, b]
    return out


# ---------- dónde termina el ">" ----------
arms_svg = [(px + kx, -py) for px, py in arms]
cx, cy = kx + (522 + 1952) / 2, -capH / 2       # centro del fill-box de los brazos
T = -(kx + 522 - vb_x)                          # traslación del bloque: el ">" queda donde estaba
fin = [(2 * cx - px + T, 2 * cy - py) for px, py in contorno(arms_svg, STK)]   # girado 180°
WIN_L = min(p[0] for p in fin)                  # borde izquierdo fijo de la ventana
TIP = max(p[0] for p in fin)                    # punta del ">" (con inglete)

# ---------- coreografía (segundos desde hdr-play) ----------
S0 = 0.30                       # pausa después de que el logo aterriza de la intro
DUR = 1.00                      # bloque: un solo movimiento
EASE_BLOQUE = ".45, 0, .25, 1"  # ease-in-out suave
ROT_DESDE = 0.40                # el "<" rueda en el último 60 % del viaje y termina con el bloque
EASE_ROT = ".2, .4, .2, 1"      # más rápido al principio: así ninguna punta se sale de la ventana
ROT_DX = 60                     # giro alrededor de un punto 60 u a la derecha del centro (y un corrimiento
                                # que lo compensa): con el centro exacto, una punta rozaba la U un instante
TELON_ANTES = 0.15              # el telón termina 150 ms antes que el bloque…
EASE_TELON = ".5, 0, .75, .9"   # …con un corte seco (llega con velocidad, sin cola ni rebote): a 0,05 px
                                # se lo ve quieto ~115 ms antes de que se asiente el ">"
TELON_MARGEN = 85               # u después de la punta del ">": cubre lo que el ">" se mueve al final
FUNDIDO = DUR / 3               # unión y palo del K se desvanecen en el primer tercio: al rodar, el "<"
                                # barre 2209 u y entre el palo y la U hay 1930 u
W0 = ww + STK + 200 - WIN_L     # ventana abierta: toda la palabra
W1 = TIP + TELON_MARGEN - WIN_L # ventana cerrada: hasta justo después del ">"
ASIENTA = S0 + DUR              # el ">" quedó en su lugar

# ---------- "≡": tres barras a un espacio del ">" ----------
# Medidas heredadas del cursor de la v2 (salían de Archivo a un tamaño con altura de x = alto del
# ">"): ancho = letra promedio, grosor = trazo del ">", separación = un espacio. La de abajo apoya
# donde apoya el ">" (es el cursor); la de arriba, en su tope; la del medio, centrada.
PESO = 275
fuente = instantiateVariableFont(TTFont(ROOT / "assets" / "fonts" / "archivo.woff2"), {"wght": PESO, "wdth": 100})
upm = fuente["head"].unitsPerEm
XH = fuente["OS/2"].sxHeight / upm
cmap, hmtx = fuente.getBestCmap(), fuente["hmtx"]
F_U = (capH + STK) / XH                                       # "tamaño de letra" en u del viewBox
ESPACIO_U = hmtx[cmap[ord(" ")]][0] / upm * F_U
BARRA_W = sum(hmtx[cmap[ord(c)]][0] for c in "menú") / 4 / upm * F_U
nx, ny = -752 / math.hypot(1110, 752), 1110 / math.hypot(1110, 752)
BARRA_H = (abs((832 - 522) * nx) + abs((1920 - 522) * nx + (1536 - 784) * ny)) / 2 + STK   # trazo del ">"
GT_ARRIBA, GT_ABAJO = -capH - STK / 2, STK / 2                 # tope y base del ">" en pantalla
BX = TIP + ESPACIO_U
BARRAS = [GT_ABAJO - BARRA_H, (GT_ARRIBA + GT_ABAJO) / 2 - BARRA_H / 2, GT_ARRIBA]   # y de abajo, medio, arriba
OPAC = [1, .6, .2]                                             # degradé

# parpadeo de terminal (530 / 530 ms, corte seco) desde el asiento del ">":
# 1 barra · apagado · 2 barras · apagado · 3 barras fijas
PARPADEO = 0.53
FIJAS = ASIENTA + 4 * PARPADEO
FIN = FIJAS + 0.05             # main.js pasa a hdr-done con las tres barras ya fijas (no cambia nada)

# ---------- tamaño: el alto del ">" sigue la escala tipográfica del sitio (pasos de √φ) ----------
GT_CEL = 17.0                                  # ≤ 600 px: 17 px, el texto base (en 320 entra SEKURECO)
GT_ESC = 17.0 * math.sqrt((1 + 5 ** .5) / 2)   # escritorio: el paso siguiente, 21,62 px
GT_EN_LOGO = (capH + STK) / vb_h               # alto del ">" / alto del SVG del logo
WM_CEL, WM_ESC = GT_CEL / GT_EN_LOGO, GT_ESC / GT_EN_LOGO

ms = lambda s: f"{s:.3f}".rstrip("0").rstrip(".") + "s"
k1 = lambda pares: " ".join(f"{p}% {{ opacity: {o}; }}" for p, o in pares)
abierto = '.hdr-done .top .menu-btn[aria-expanded="true"]'
reglas = [
    "/* ---------- header (generado por tools/header.py: no editar a mano) ---------- */",
    "/* duración de la secuencia hasta hdr-done (main.js la lee) */",
    f":root {{ --hdr-total: {round(FIN * 1000)}; }}",
    "",
    f'/* alto del logo: el ">" (y el "≡") mide {GT_ESC:.2f} px en escritorio y {GT_CEL:.0f} px en celular */',
    f".top .logo-wm {{ height: {WM_ESC:.3f}px; }}",
    f"@media (max-width: 600px) {{ .top .logo-wm {{ height: {WM_CEL:.3f}px; }} }}",
    "",
    f'/* el "<" rueda alrededor de un punto {ROT_DX} u a la derecha de su centro (y se corre {2 * ROT_DX} u para compensar) */',
    f".top .k-arms {{ transform-origin: calc(50% + {ROT_DX}px) 50%; }}",
    ".top .bar { opacity: 0; }",
    "",
    "/* primera vez en la sesión (hdr-play) */",
    f".hdr-play .top .wm-move {{ animation: hbloque {ms(DUR)} cubic-bezier({EASE_BLOQUE}) {ms(S0)} both; }}",
    f".hdr-play .top .win {{ animation: htelon {ms(DUR - TELON_ANTES)} cubic-bezier({EASE_TELON}) {ms(S0)} both; }}",
    f".hdr-play .top .k-arms {{ animation: hrueda {ms(DUR * (1 - ROT_DESDE))} cubic-bezier({EASE_ROT}) {ms(S0 + DUR * ROT_DESDE)} both; }}",
    f".hdr-play .top .k-join, .hdr-play .top .k-stem {{ animation: hfunde {ms(FUNDIDO)} linear {ms(S0)} both; }}",
    f"@keyframes hbloque {{ to {{ transform: translateX({T:.0f}px); }} }}",
    f"@keyframes htelon {{ from {{ width: {W0:.1f}px; }} to {{ width: {W1:.1f}px; }} }}",
    f"@keyframes hrueda {{ from {{ transform: translateX(0) rotate(0deg); }} to {{ transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }} }}",
    "@keyframes hfunde { to { opacity: 0; } }",
    f'/* "≡" con el parpadeo del cursor: {ms(ASIENTA)} 1 barra · {ms(ASIENTA + PARPADEO)} nada · '
    f'{ms(ASIENTA + 2 * PARPADEO)} 2 barras · {ms(ASIENTA + 3 * PARPADEO)} nada · {ms(FIJAS)} 3 barras, fijas */',
] + [f".hdr-play .top .bar{i} {{ animation: hbar{i} {ms(4 * PARPADEO)} steps(1) {ms(ASIENTA)} forwards; }}" for i in (1, 2, 3)] + [
    f"@keyframes hbar1 {{ {k1([(0, 1), (25, 0), (50, 1), (75, 0), (100, 1)])} }}",
    f"@keyframes hbar2 {{ {k1([(0, 0), (50, OPAC[1]), (75, 0), (100, OPAC[1])])} }}",
    f"@keyframes hbar3 {{ {k1([(0, 0), (100, OPAC[2])])} }}",
    "",
    '/* estado final (y el de cualquier otra página vista en la sesión): ">≡" fijo, con su degradé */',
    f".hdr-done .top .wm-move {{ transform: translateX({T:.0f}px); }}",
    f".hdr-done .top .win {{ width: {W1:.1f}px; }}",
    f".hdr-done .top .k-arms {{ transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }}",
    ".hdr-done .top .k-join, .hdr-done .top .k-stem { opacity: 0; }",
    ".hdr-done .top .bar { transition: opacity .15s ease-out, transform .15s ease-out; }",
] + [f".hdr-done .top .bar{i + 1} {{ opacity: {o}; }}" for i, o in enumerate(OPAC)] + [
    "/* hover con mouse: las tres barras al 100 % */",
    "@media (hover: hover) and (pointer: fine) {",
    "  .hdr-done .top .menu-btn:hover .bar { opacity: 1; }",
    "}",
    '/* menú abierto: el ">" apunta abajo (mismo centro que antes); las dos barras de arriba bajan y se',
    '   funden en la de abajo, que queda como un "_" titilando (530 / 530 ms) */',
    f"{abierto} .k-arms {{ transform: translate({-ROT_DX}px, {-ROT_DX}px) rotate(-90deg); }}",
    f"{abierto} .bar2 {{ transform: translateY({BARRAS[0] - BARRAS[1]:.1f}px); opacity: 0; }}",
    f"{abierto} .bar3 {{ transform: translateY({BARRAS[0] - BARRAS[2]:.1f}px); opacity: 0; }}",
    f"{abierto} .bar1 {{ opacity: 1; animation: hblink {ms(2 * PARPADEO)} steps(1) infinite; }}",
    "",
    "@media (prefers-reduced-motion: reduce) {",
    f"  .hdr-play .top .wm-move {{ animation: none; transform: translateX({T:.0f}px); }}",
    f"  .hdr-play .top .win {{ animation: none; width: {W1:.1f}px; }}",
    f"  .hdr-play .top .k-arms {{ animation: none; transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }}",
    "  .hdr-play .top .k-join, .hdr-play .top .k-stem { animation: none; opacity: 0; }",
    "  .hdr-play .top .bar { animation: none; }",
] + [f"  .hdr-play .top .bar{i + 1} {{ opacity: {o}; }}" for i, o in enumerate(OPAC)] + [
    "  .hdr-done .top .bar { transition: none; }",
    f"  {abierto} .bar1 {{ animation: none; }}",
    "}",
    "",
    "",
]
css = "\n".join(reglas)

# ---------- SVG ----------
sh = shield("hdr", "currentColor", "var(--acc)").replace('fill="var(--acc)"', 'class="la"')
shield_svg = f'<svg class="logo-shield" viewBox="-20 -20 772 880" aria-hidden="true" focusable="false">{sh}</svg>'

paths = ''.join(f'<path d="{d}"/>' for d in letters)
barras = ''.join(f'<rect class="bar bar{i + 1} la" x="{BX:.1f}" y="{y:.1f}" width="{BARRA_W:.1f}" height="{BARRA_H:.1f}"/>'
                 for i, y in enumerate(BARRAS))
wm_svg = (f'<svg class="logo-wm" viewBox="{vb_x} {vb_y} {vb_w:.0f} {vb_h}" aria-hidden="true" focusable="false">'
          f'<defs><clipPath id="wmwin" clipPathUnits="userSpaceOnUse">'
          f'<rect class="win" x="{WIN_L:.1f}" y="{vb_y - 2000}" width="{W0:.1f}" height="{vb_h + 4000}"/></clipPath></defs>'
          f'<g clip-path="url(#wmwin)"><g class="wm-move">'
          f'<g class="wm-letters" fill="currentColor" stroke="currentColor" stroke-width="{STK}">{paths}</g>'
          f'<path class="k-stem" fill="currentColor" stroke="currentColor" stroke-width="{STK}" d="{stem_d}"/>'
          f'<path class="k-join la la-s" stroke-width="{STK}" d="{join_d}"/>'
          f'<path class="k-arms la la-s" stroke-width="{STK}" stroke-linejoin="miter" d="{arms_d}"/>'
          f'</g></g>'
          f'<g class="bars">{barras}</g></svg>')

open(BUILD / 'header-shield.svg', 'w').write(shield_svg)
open(BUILD / 'header-wordmark.svg', 'w').write(wm_svg)
open(BUILD / 'header.css', 'w').write(css)

print(f'header ok · ">" final: borde izq {WIN_L:.1f} u, punta {TIP:.1f} u · bloque {T:.0f} u · telón {W0:.0f} → {W1:.0f} u')
print(f'   alto del ">": {GT_ESC:.2f} px escritorio / {GT_CEL:.0f} px celular (logo {WM_ESC:.3f} / {WM_CEL:.3f} px)')
print(f'   "≡": barras de {BARRA_W:.0f} × {BARRA_H:.1f} u a {ESPACIO_U:.0f} u del ">" · opacidades {OPAC}')
print('   línea de tiempo (ms desde hdr-play):')
for ev, t in [("arranca el bloque, el telón y el fundido de unión y palo", S0),
              ("unión y palo del K ya no se ven", S0 + FUNDIDO),
              ('el "<" empieza a rodar', S0 + DUR * ROT_DESDE),
              ("el telón se detiene", S0 + DUR - TELON_ANTES),
              ('se asienta el ">"; encendido: 1 barra', ASIENTA),
              ("apagado", ASIENTA + PARPADEO), ("encendido: 2 barras", ASIENTA + 2 * PARPADEO),
              ("apagado", ASIENTA + 3 * PARPADEO), ("encendido: 3 barras, fijas", FIJAS), ("hdr-done", FIN)]:
    print(f'     {round(t * 1000):5d}  {ev}')
