"""Header: escudo (link al inicio) + SEKURECO que se cierra en ">_ menú", el botón del menú.

Genera:
  build/header-shield.svg     escudo
  build/header-wordmark.svg   SEKURECO dentro de una "ventana" (clipPath) que se cierra
  build/header.css            la coreografía del cierre, el tipeo de "menú" y la geometría de
                              la etiqueta y el cursor (apply.py lo mete en styles.css)

El cierre ("ventana"): toda la palabra se desplaza a la izquierda como un bloque hasta que los
brazos del K quedan donde va el ">". Se ve a través de una ventana: el borde izquierdo está fijo
en el borde izquierdo del ">" final (S, E y el palo del K salen por ahí) y el derecho es un telón
que avanza de derecha a izquierda tapando U, R, E, C, O y frena un poco antes que el bloque. El "<"
viaja con el bloque y rueda 180° (antihorario) en el último 60 % del viaje hasta ser ">".
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
HS = vb_h * 2                       # unidades del viewBox por cada --hs (el logo mide --hs / 2 de alto)


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
TELON_ANTES = 0.10              # el telón frena 100 ms antes que el bloque
EASE_TELON = ".55, 0, .45, 1"
TELON_MARGEN = 50               # u después de la punta del ">": cubre lo que el ">" se mueve al final
FUNDIDO = DUR / 3               # unión y palo del K se desvanecen en el primer tercio
W0 = ww + STK + 200 - WIN_L     # ventana abierta: toda la palabra
W1 = TIP + TELON_MARGEN - WIN_L # ventana cerrada: hasta justo después del ">"

ASIENTA = S0 + DUR              # el ">" quedó en su lugar
LETRAS = [0.15, 0.15, 0.125, 0.18]   # "m" a 150 ms del asiento; después ~163 ms con variación humana
T_LETRA = [ASIENTA + sum(LETRAS[:i + 1]) for i in range(4)]
TITILA = T_LETRA[-1] + 0.53     # después de escribir, el cursor queda fijo medio ciclo y titila
FIN = TITILA + 0.10             # main.js pasa a hdr-done en la fase encendida del titileo

# ---------- etiqueta "menú": proporcional al ">" ----------
PESO = 275    # Archivo variable: a 275 la pata de la "n" mide 68,5/1000 de em, el trazo del ">" 68,7
# los anchos de una fuente variable cambian con el peso: se miden en la instancia que se usa
fuente = instantiateVariableFont(TTFont(ROOT / "assets" / "fonts" / "archivo.woff2"), {"wght": PESO, "wdth": 100})
upm = fuente["head"].unitsPerEm
ASC, DESC = fuente["hhea"].ascent / upm, -fuente["hhea"].descent / upm
XH = fuente["OS/2"].sxHeight / upm
cmap, hmtx = fuente.getBestCmap(), fuente["hmtx"]
ESPACIO = hmtx[cmap[ord(" ")]][0] / upm
PROMEDIO = sum(hmtx[cmap[ord(c)]][0] for c in "menú") / 4 / upm
GT_ALTO = (capH + STK) / HS                     # alto del ">" en pantalla, en --hs
K_FS = GT_ALTO / XH                             # tamaño de letra: altura de x = alto del ">"
# grosor perpendicular del trazo del ">" (el brazo es apenas cónico: promedio) + el trazo SVG
nx, ny = -752 / math.hypot(1110, 752), 1110 / math.hypot(1110, 752)
TRAZO = (abs((832 - 522) * nx) + abs((1920 - 522) * nx + (1536 - 784) * ny)) / 2 + STK
Y_BASE = (STK / 2 - vb_y) / HS                  # borde inferior del ">" desde arriba del logo
X_TIP = (TIP - vb_x) / HS                       # punta del ">" desde el borde izquierdo del logo

f = lambda v: f"{v:.5f}".rstrip("0")
ms = lambda s: f"{s:.3f}".rstrip("0").rstrip(".") + "s"
css = f'''/* ---------- header (generado por tools/header.py: no editar a mano) ---------- */
/* duración de la secuencia hasta hdr-done (main.js la lee) */
:root {{ --hdr-total: {round(FIN * 1000)}; }}

/* el "<" rueda alrededor de un punto {ROT_DX} u a la derecha de su centro (y se corre {2 * ROT_DX} u para compensar) */
.top .k-arms {{ transform-origin: calc(50% + {ROT_DX}px) 50%; }}

/* etiqueta: altura de x = alto del ">" ({f(GT_ALTO)} hs), línea de base en el borde inferior del ">",
   Archivo {PESO}; arranca en la punta del ">" y la "m" va un espacio ({ESPACIO:.3f} em) más allá */
.menu-label {{
  --cw: calc(var(--hs) * {f(K_FS * PROMEDIO)});          /* cursor: ancho promedio de letra de "menú" */
  --ct: calc(var(--hs) * {f(TRAZO / HS)});          /* cursor: grosor del trazo del ">" */
  left: calc(4px + var(--hs) * {f(X_TIP)});
  top: calc(6px + var(--hs) * {f(Y_BASE - ASC * K_FS)});
  font-size: calc(var(--hs) * {f(K_FS)});
  font-weight: {PESO};
  line-height: {f(ASC + DESC)};                       /* = ascendente + descendente: la base queda a {f(ASC)} em */
}}
.mgap {{ width: calc(var(--hs) * {f(K_FS * ESPACIO)}); }}
.mcur {{ top: calc(var(--hs) * {f(K_FS * ASC)} - var(--ct)); height: var(--ct); }}

/* primera vez en la sesión (hdr-play) */
.hdr-play .top .wm-move {{ animation: hbloque {ms(DUR)} cubic-bezier({EASE_BLOQUE}) {ms(S0)} both; }}
.hdr-play .top .win {{ animation: htelon {ms(DUR - TELON_ANTES)} cubic-bezier({EASE_TELON}) {ms(S0)} both; }}
.hdr-play .top .k-arms {{ animation: hrueda {ms(DUR * (1 - ROT_DESDE))} cubic-bezier({EASE_ROT}) {ms(S0 + DUR * ROT_DESDE)} both; }}
.hdr-play .top .k-join, .hdr-play .top .k-stem {{ animation: hfunde {ms(FUNDIDO)} linear {ms(S0)} both; }}
@keyframes hbloque {{ to {{ transform: translateX({T:.0f}px); }} }}
@keyframes htelon {{ from {{ width: {W0:.1f}px; }} to {{ width: {W1:.1f}px; }} }}
@keyframes hrueda {{ from {{ transform: translateX(0) rotate(0deg); }} to {{ transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }} }}
@keyframes hfunde {{ to {{ opacity: 0; }} }}
/* "menú" letra por letra; una sola barra de cursor visible por vez, cada una en su lugar */
.hdr-play .mc0 .mcur {{ animation: mon {ms(T_LETRA[0] - ASIENTA)} {ms(ASIENTA)}; }}
''' + "".join(
    f'.hdr-play .ml{i + 1} {{ animation: mtype .01s steps(1, jump-start) {ms(T_LETRA[i])} both; }}\n' +
    (f'.hdr-play .mc{i + 1} .mcur {{ animation: mon {ms(T_LETRA[i + 1] - T_LETRA[i])} {ms(T_LETRA[i])}; }}\n' if i < 3 else
     f'.hdr-play .mc4 .mcur {{ animation: mon .01s {ms(T_LETRA[3])} forwards, htitila 1.06s steps(1) {ms(TITILA)} infinite; }}\n')
    for i in range(4)) + f'''@keyframes mtype {{ from {{ max-width: 0; }} to {{ max-width: 2em; }} }}
@keyframes mon {{ from, to {{ width: var(--cw); }} }}
/* igual que hblink, con otro nombre: al pasar a hdr-done el titileo arranca de nuevo (encendido);
   con el mismo nombre el navegador lo continuaría con el delay nuevo y la fase saltaría */
@keyframes htitila {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}

/* estado final (y el de cualquier otra página vista en la sesión) */
.hdr-done .top .wm-move {{ transform: translateX({T:.0f}px); }}
.hdr-done .top .win {{ width: {W1:.1f}px; }}
.hdr-done .top .k-arms {{ transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }}
.hdr-done .top .k-join, .hdr-done .top .k-stem {{ opacity: 0; }}
.hdr-done .ml {{ max-width: 2em; }}
.hdr-done .mc4 .mcur {{ width: var(--cw); animation: hblink 1.06s steps(1) infinite; }}
/* menú abierto: el ">" gira 90° y apunta hacia abajo (mismo centro que antes) */
.hdr-done .top .menu-btn[aria-expanded="true"] .k-arms {{ transform: translate({-ROT_DX}px, {-ROT_DX}px) rotate(-90deg); }}

@media (prefers-reduced-motion: reduce) {{
  .hdr-play .top .wm-move {{ animation: none; transform: translateX({T:.0f}px); }}
  .hdr-play .top .win {{ animation: none; width: {W1:.1f}px; }}
  .hdr-play .top .k-arms {{ animation: none; transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }}
  .hdr-play .top .k-join, .hdr-play .top .k-stem {{ animation: none; opacity: 0; }}
  .hdr-play .ml {{ animation: none; max-width: 2em; }}
  .hdr-play .mcur {{ animation: none; }}
  .hdr-play .mc4 .mcur, .hdr-done .mc4 .mcur {{ animation: none; width: var(--cw); opacity: 1; }}
}}

'''

# ---------- SVG ----------
sh = shield("hdr", "currentColor", "var(--acc)").replace('fill="var(--acc)"', 'class="la"')
shield_svg = f'<svg class="logo-shield" viewBox="-20 -20 772 880" aria-hidden="true" focusable="false">{sh}</svg>'

paths = ''.join(f'<path d="{d}"/>' for d in letters)
wm_svg = (f'<svg class="logo-wm" viewBox="{vb_x} {vb_y} {vb_w:.0f} {vb_h}" aria-hidden="true" focusable="false">'
          f'<defs><clipPath id="wmwin" clipPathUnits="userSpaceOnUse">'
          f'<rect class="win" x="{WIN_L:.1f}" y="{vb_y - 2000}" width="{W0:.1f}" height="{vb_h + 4000}"/></clipPath></defs>'
          f'<g clip-path="url(#wmwin)"><g class="wm-move">'
          f'<g class="wm-letters" fill="currentColor" stroke="currentColor" stroke-width="{STK}">{paths}</g>'
          f'<path class="k-stem" fill="currentColor" stroke="currentColor" stroke-width="{STK}" d="{stem_d}"/>'
          f'<path class="k-join la la-s" stroke-width="{STK}" d="{join_d}"/>'
          f'<path class="k-arms la la-s" stroke-width="{STK}" stroke-linejoin="miter" d="{arms_d}"/>'
          f'</g></g></svg>')

open(BUILD / 'header-shield.svg', 'w').write(shield_svg)
open(BUILD / 'header-wordmark.svg', 'w').write(wm_svg)
open(BUILD / 'header.css', 'w').write(css)

print(f'header ok · ">" final: borde izq {WIN_L:.1f} u, punta {TIP:.1f} u · bloque {T:.0f} u · telón {W0:.0f} → {W1:.0f} u')
print(f'   etiqueta: {K_FS:.5f} hs de letra (Archivo {PESO}), espacio {K_FS * ESPACIO:.5f} hs, '
      f'cursor {K_FS * PROMEDIO:.5f} × {TRAZO / HS:.5f} hs')
print('   línea de tiempo (ms desde hdr-play):')
for ev, t in [("arranca el bloque, el telón y el fundido de unión y palo", S0),
              ("unión y palo del K ya no se ven", S0 + FUNDIDO),
              ('el "<" empieza a rodar', S0 + DUR * ROT_DESDE),
              ("el telón se detiene", S0 + DUR - TELON_ANTES),
              ('se asienta el ">" (bloque y giro terminan); aparece el cursor', ASIENTA),
              ("m", T_LETRA[0]), ("e", T_LETRA[1]), ("n", T_LETRA[2]), ("ú", T_LETRA[3]),
              ("el cursor vuelve a titilar", TITILA), ("hdr-done", FIN)]:
    print(f'     {round(t * 1000):5d}  {ev}')
