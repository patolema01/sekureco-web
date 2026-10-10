"""Header: escudo (link al inicio) + SEKURECO que se cierra en ">≡", el botón del menú.

Genera:
  build/header-shield.svg     escudo
  build/header-wordmark.svg   SEKURECO dentro de una "ventana" (clipPath) que se cierra, y el "≡"
  build/intro-wordmark.svg    SEKURECO solo (con sus acentos teal), para la intro: sin ventana ni "≡"
  build/header.css            la coreografía del cierre, el parpadeo del "≡", la interacción del
                              menú y el alto del logo (apply.py lo mete en styles.css)

El cierre ("ventana"): toda la palabra se desplaza a la izquierda como un bloque hasta que los
brazos del K quedan donde va el ">". Se ve a través de una ventana: el borde izquierdo está fijo
en el borde izquierdo del ">" final (S, E y el palo del K salen por ahí) y el derecho es un telón
que avanza de derecha a izquierda tapando U, R, E, C, O y frena antes que el bloque. El "<" viaja
con el bloque y rueda 180° (antihorario) en el último 60 % del viaje hasta ser ">". En la web la
primera E lleva sus barras en teal: al cerrar, se funden en un "_" que viaja por detrás del ">"
hasta ser el cursor; el cursor parpadea a 92 bpm y en el tercer encendido queda fijo, y el "≡" se
completa a 216 bpm (las barras del medio y de arriba aparecen fundiéndose).
(Los archivos de marca, assets/brand, los hace brand.py y no cambian.)
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
    elif ch == "E" and i == 1:
        # la primera E (la de SEK) en piezas, como rectángulos ya con el trazo (19 u de cada lado):
        # palo blanco y tres barras teal que arrancan donde termina el palo. Juntas cubren lo mismo
        # que la letra original. La de abajo es la que se convierte en el cursor.
        h = STK / 2
        # cada barra es su segmento de la letra con el mismo trazo (19 u de cada lado): abajo 384→1728,
        # medio 384→1645, arriba 384→1700. El palo va encima y tapa el arranque (sin costura de
        # antialiasing entre el blanco y el teal); sueltas, en el "≡", se ven enteras.
        e_palo = (x + 192 - h, -1536 - h, 192 + 2 * h, 1536 + 2 * h)              # x, y, ancho, alto
        e_barras = [(x + 384 - h, -160 - h, 1728 - 384 + 2 * h, 160 + 2 * h),               # abajo
                    (x + 384 - h, -864 - h, 1645 - 384 + 2 * h, 864 - 704 + 2 * h),          # medio
                    (x + 384 - h, -1536 - h, 1700 - 384 + 2 * h, 1536 - 1376 + 2 * h)]       # arriba
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
GT_ARRIBA, GT_ABAJO = -capH - STK / 2, STK / 2                 # tope y base del ">" en pantalla
BX = TIP + ESPACIO_U                                          # borde izquierdo del "≡"
EQ_DX = BX - e_barras[0][0]                                   # traslado de las barras de la E al "≡"
EQ = [(bx + EQ_DX, by, bw, bh) for bx, by, bw, bh in e_barras]   # abajo, medio, arriba
assert abs(EQ[2][1] - GT_ARRIBA) < .01 and abs(EQ[0][1] + EQ[0][3] - GT_ABAJO) < .01, "el ≡ tiene el alto del >"
OPAC = [1, .6, .2]                                             # degradé

# ---------- la E: sus barras se funden en un "_" que viaja hasta ser el cursor ----------
E_FUNDE = 0.38                  # las barras de arriba y del medio bajan y se funden en la de abajo
EASE_E = ".4, 0, .2, 1"
VIAJA_DESDE = 0.35              # el "_" va con el bloque el primer 35 % y después viaja a la derecha
EASE_VIAJE = ".15, .3, .25, 1"  # arranca ya hacia la derecha: nunca retrocede ni se acerca al borde fijo
VIAJE_DX = BX - T - e_barras[0][0]             # en el marco del bloque: termina en la barra de abajo del "≡"
                                                # (el "_" no cambia de tamaño: llega tal cual y es el cursor)

# parpadeo de terminal (530 / 530 ms, corte seco) desde el asiento del ">":
# 1 barra · apagado · 2 barras · apagado · 3 barras fijas
# el cursor que llegó parpadea a 92 bpm (un parpadeo por negra, corte seco): encendido · apagado ·
# encendido · apagado · tercer encendido, y desde ahí no se apaga más
PARPADEO = 60 / 92 / 2          # 326 ms encendido / 326 apagado
TERCERO = ASIENTA + 4 * PARPADEO
# en el tercer encendido el "≡" se completa a 216 bpm, de abajo hacia arriba, fundiéndose (nunca se apagan)
T216 = 60 / 216                 # 277,8 ms
SUBE = 1.6 * T216               # cada barra tarda 1,6 T en llegar a su opacidad
EASE_SUBE = ".25, .1, .25, 1"
MEDIO_DESDE, ARRIBA_DESDE = TERCERO + T216, TERCERO + 2 * T216
FIJAS = ARRIBA_DESDE + SUBE
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
    f".hdr-play .top .k-join, .hdr-play .top .k-stem, .hdr-play .top .e-stem {{ animation: hfunde {ms(FUNDIDO)} linear {ms(S0)} both; }}",
    '/* la E: las barras de arriba y del medio bajan y se funden en la de abajo; esa queda como un "_" que',
    f'   va con el bloque el primer {round(VIAJA_DESDE * 100)} % y después viaja (por detrás del ">") hasta ser el cursor */',
    f".hdr-play .top .e-bar2 {{ animation: hfundeE2 {ms(E_FUNDE)} cubic-bezier({EASE_E}) {ms(S0)} both; }}",
    f".hdr-play .top .e-bar3 {{ animation: hfundeE3 {ms(E_FUNDE)} cubic-bezier({EASE_E}) {ms(S0)} both; }}",
    f"@keyframes hfundeE2 {{ 90% {{ opacity: 0; }} 100% {{ opacity: 0; transform: translateY({e_barras[0][1] - e_barras[1][1]:.1f}px); }} }}",
    f"@keyframes hfundeE3 {{ 90% {{ opacity: 0; }} 100% {{ opacity: 0; transform: translateY({e_barras[0][1] - e_barras[2][1]:.1f}px); }} }}",
    f".hdr-play .top .cur-move {{ animation: hbloque {ms(DUR)} cubic-bezier({EASE_BLOQUE}) {ms(S0)} both; }}",
    f".hdr-play .top .e-cur {{ animation: hviaja {ms(DUR * (1 - VIAJA_DESDE))} cubic-bezier({EASE_VIAJE}) {ms(S0 + DUR * VIAJA_DESDE)} both, "
    f"hentrega .01s steps(1, jump-start) {ms(ASIENTA)} forwards; }}",
    f"@keyframes hviaja {{ to {{ transform: translateX({VIAJE_DX:.1f}px); }} }}",
    '/* al llegar, el "_" le deja el lugar a la barra de abajo del "≡" (la misma barra, en el mismo lugar): es el cursor */',
    "@keyframes hentrega { to { opacity: 0; } }",
    f"@keyframes hbloque {{ to {{ transform: translateX({T:.0f}px); }} }}",
    f"@keyframes htelon {{ from {{ width: {W0:.1f}px; }} to {{ width: {W1:.1f}px; }} }}",
    f"@keyframes hrueda {{ from {{ transform: translateX(0) rotate(0deg); }} to {{ transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }} }}",
    "@keyframes hfunde { to { opacity: 0; } }",
    f'/* el cursor que llegó parpadea a 92 bpm: {ms(ASIENTA)} encendido · {ms(ASIENTA + PARPADEO)} apagado · '
    f'{ms(ASIENTA + 2 * PARPADEO)} encendido · {ms(ASIENTA + 3 * PARPADEO)} apagado · {ms(TERCERO)} encendido para siempre;',
    f'   el "≡" se completa a 216 bpm: medio desde {ms(MEDIO_DESDE)}, arriba desde {ms(ARRIBA_DESDE)}, {ms(SUBE)} cada una */',
    f".hdr-play .top .bar1 {{ animation: hbar1 {ms(4 * PARPADEO)} steps(1) {ms(ASIENTA)} forwards; }}",
    f".hdr-play .top .bar2 {{ animation: hbar2 {ms(SUBE)} cubic-bezier({EASE_SUBE}) {ms(MEDIO_DESDE)} both; }}",
    f".hdr-play .top .bar3 {{ animation: hbar3 {ms(SUBE)} cubic-bezier({EASE_SUBE}) {ms(ARRIBA_DESDE)} both; }}",
    f"@keyframes hbar1 {{ {k1([(0, 1), (25, 0), (50, 1), (75, 0), (100, 1)])} }}",
    f"@keyframes hbar2 {{ from {{ opacity: 0; }} to {{ opacity: {OPAC[1]}; }} }}",
    f"@keyframes hbar3 {{ from {{ opacity: 0; }} to {{ opacity: {OPAC[2]}; }} }}",
    "",
    '/* estado final (y el de cualquier otra página vista en la sesión): ">≡" fijo, con su degradé */',
    f".hdr-done .top .wm-move {{ transform: translateX({T:.0f}px); }}",
    f".hdr-done .top .win {{ width: {W1:.1f}px; }}",
    f".hdr-done .top .k-arms {{ transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }}",
    ".hdr-done .top .k-join, .hdr-done .top .k-stem, .hdr-done .top .e-stem, .hdr-done .top .e-bar, .hdr-done .top .e-cur { opacity: 0; }",
    ".hdr-done .top .bar { transition: opacity .15s ease-out, transform .15s ease-out; }",
] + [f".hdr-done .top .bar{i + 1} {{ opacity: {o}; }}" for i, o in enumerate(OPAC)] + [
    "/* hover con mouse: las tres barras al 100 % */",
    "@media (hover: hover) and (pointer: fine) {",
    "  .hdr-done .top .menu-btn:hover .bar { opacity: 1; }",
    "}",
    '/* menú abierto: el ">" apunta abajo (mismo centro que antes); las dos barras de arriba bajan (sin cambiar de largo) y se',
    '   funden en la de abajo, que queda como un "_" titilando (530 / 530 ms) */',
    f"{abierto} .k-arms {{ transform: translate({-ROT_DX}px, {-ROT_DX}px) rotate(-90deg); }}",
    f"{abierto} .bar2 {{ transform: translateY({EQ[0][1] - EQ[1][1]:.1f}px); opacity: 0; }}",
    f"{abierto} .bar3 {{ transform: translateY({EQ[0][1] - EQ[2][1]:.1f}px); opacity: 0; }}",
    f"{abierto} .bar1 {{ opacity: 1; animation: hblink {ms(2 * PARPADEO)} steps(1) infinite; }}",
    "",
    "@media (prefers-reduced-motion: reduce) {",
    f"  .hdr-play .top .wm-move {{ animation: none; transform: translateX({T:.0f}px); }}",
    f"  .hdr-play .top .win {{ animation: none; width: {W1:.1f}px; }}",
    f"  .hdr-play .top .k-arms {{ animation: none; transform: translateX({-2 * ROT_DX}px) rotate(-180deg); }}",
    "  .hdr-play .top .k-join, .hdr-play .top .k-stem, .hdr-play .top .e-stem, .hdr-play .top .e-bar, .hdr-play .top .e-cur { animation: none; opacity: 0; }",
    "  .hdr-play .top .cur-move { animation: none; }",
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
r = lambda c, v: f'<rect class="{c}" x="{v[0]:.1f}" y="{v[1]:.1f}" width="{v[2]:.1f}" height="{v[3]:.1f}"/>'
e_palo_svg = r("e-stem", e_palo).replace('<rect ', '<rect fill="currentColor" ', 1)
k_svg = (f'<path class="k-stem" fill="currentColor" stroke="currentColor" stroke-width="{STK}" d="{stem_d}"/>'
         f'<path class="k-join la la-s" stroke-width="{STK}" d="{join_d}"/>'
         f'<path class="k-arms la la-s" stroke-width="{STK}" stroke-linejoin="miter" d="{arms_d}"/>')
letras_svg = f'<g class="wm-letters" fill="currentColor" stroke="currentColor" stroke-width="{STK}">{paths}</g>'
# para la intro: solo SEKURECO con sus acentos teal (E y K), sin ventana, sin "≡" y sin cursor
intro_svg = (f'<svg class="intro-wm-svg" viewBox="{vb_x} {vb_y} {vb_w:.0f} {vb_h}" aria-hidden="true" focusable="false">'
             f'{letras_svg}' + ''.join(r("la", v) for v in e_barras) + f'{e_palo_svg}{k_svg}</svg>')
barras = ''.join(r(f"bar bar{i + 1} la", v) for i, v in enumerate(EQ))
k_arms_svg = f'<path class="k-arms la la-s" stroke-width="{STK}" stroke-linejoin="miter" d="{arms_d}"/>'
k_resto_svg = k_svg.replace(k_arms_svg, "")
wm_svg = (f'<svg class="logo-wm" viewBox="{vb_x} {vb_y} {vb_w:.0f} {vb_h}" aria-hidden="true" focusable="false">'
          f'<defs><clipPath id="wmwin" clipPathUnits="userSpaceOnUse">'
          f'<rect class="win" x="{WIN_L:.1f}" y="{vb_y - 2000}" width="{W0:.1f}" height="{vb_h + 4000}"/></clipPath>'
          f'<clipPath id="wmizq" clipPathUnits="userSpaceOnUse">'
          f'<rect x="{WIN_L:.1f}" y="{vb_y - 2000}" width="{vb_w * 2:.0f}" height="{vb_h + 4000}"/></clipPath></defs>'
          # tres capas que se mueven juntas (misma animación de bloque):
          # 1) letras blancas (y las barras de la E que se funden), recortadas por la ventana
          f'<g clip-path="url(#wmwin)"><g class="wm-move">{letras_svg}'
          f'{r("e-bar e-bar2 la", e_barras[1])}{r("e-bar e-bar3 la", e_barras[2])}{k_resto_svg}</g></g>'
          # 2) el "_" que viaja: por delante de las letras (nunca queda tapado) y recortado solo por
          #    el borde izquierdo, porque termina donde va el cursor, más allá del telón. El palo de la
          #    E va acá, encima del "_" (tapa el empalme), y se desvanece antes de que el "_" se mueva
          f'<g clip-path="url(#wmizq)"><g class="cur-move">{r("e-cur la", e_barras[0])}{e_palo_svg}</g></g>'
          # 3) el ">", por delante del "_", recortado por la ventana
          f'<g clip-path="url(#wmwin)"><g class="wm-move">{k_arms_svg}</g></g>'
          f'<g class="bars">{barras}</g></svg>')

open(BUILD / 'header-shield.svg', 'w').write(shield_svg)
open(BUILD / 'header-wordmark.svg', 'w').write(wm_svg)
open(BUILD / 'intro-wordmark.svg', 'w').write(intro_svg)
open(BUILD / 'header.css', 'w').write(css)

print(f'header ok · ">" final: borde izq {WIN_L:.1f} u, punta {TIP:.1f} u · bloque {T:.0f} u · telón {W0:.0f} → {W1:.0f} u')
print(f'   alto del ">": {GT_ESC:.2f} px escritorio / {GT_CEL:.0f} px celular (logo {WM_ESC:.3f} / {WM_CEL:.3f} px)')
print(f'   "≡": las barras de la E ({", ".join(f"{w:.0f}" for _, _, w, _ in EQ)} × {EQ[0][3]:.0f} u, con el trazo) a {ESPACIO_U:.0f} u del ">" · opacidades {OPAC}')
print('   línea de tiempo (ms desde hdr-play):')
for t, ev in sorted((t, ev) for ev, t in [("arranca el bloque, el telón y el fundido de unión y palo", S0),
              ("unión y palo del K ya no se ven", S0 + FUNDIDO),
              ('el "<" empieza a rodar', S0 + DUR * ROT_DESDE),
              ("el telón se detiene", S0 + DUR - TELON_ANTES),
              ("las barras de la E ya se fundieron en un _", S0 + E_FUNDE),
              ('el "_" empieza a viajar', S0 + DUR * VIAJA_DESDE),
              ('se asienta el ">" y llega el "_": es el cursor (encendido: 1 barra)', ASIENTA),
              ("apagado", ASIENTA + PARPADEO), ("encendido", ASIENTA + 2 * PARPADEO),
              ("apagado", ASIENTA + 3 * PARPADEO), ("tercer encendido: el cursor queda fijo", TERCERO),
              ("la barra del medio empieza a aparecer (→ 60 %)", MEDIO_DESDE), ("la de arriba empieza a aparecer (→ 20 %)", ARRIBA_DESDE),
              ("la del medio llega al 60 %", MEDIO_DESDE + SUBE), ("la de arriba llega al 20 %: ≡ fijo", FIJAS), ("hdr-done", FIN)]):
    print(f'     {round(t * 1000):5d}  {ev}')
