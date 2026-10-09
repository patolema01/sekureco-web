"""Intro v3: fuego continuo en ráfagas de 3 (3 patrones en loop) hasta que termina la carga,
y SEKURECO se compacta hacia el K hasta dejar solo ">_" titilando.
Semilla fija: irregular pero reproducible."""
import random, re
import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tools" / "build"; BUILD.mkdir(exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand
shield, glyph_path, TRACK, STK = brand.shield, brand.glyph_path, brand.TRACK, brand.STK

rnd = random.Random(20261008)
CX, CY = 500, 400
s = 0.36
shx, shy = CX - 366 * s, CY - 415 * s

FLIGHT = 0.33                              # vuelo corto: el primer impacto cae en 0,37 s
T0 = 0.37                                  # primer impacto
BPM = 92
BEAT = 60 / BPM                            # 0,652 s entre tiros
PAUSE = 0.37
P = 5.0                                    # loop de 5 s: 0,37 + 2 ráfagas de 3 tiempos + pausas
# (con 92 bpm exactos la última pausa queda en 0,347 s en vez de 0,37: 23 ms, imperceptible)
# 3 patrones de ráfaga: (inicio dentro del ciclo, [(desfase, x, y) por disparo])
# de a una bala por vez: nunca hay dos en vuelo (separación mínima 0,55 s > vuelo 0,4 s)
PATTERNS = [
    (0.0,                [(0.0, -34, -46), (BEAT, 41, 8), (2 * BEAT, -12, 52)]),
    (3 * BEAT + PAUSE,   [(0.0, 20, -30), (BEAT, -42, 28), (2 * BEAT, 36, 44)]),
]
T_BEAT = T0 + 3 * BEAT                     # el latido arranca en la primera pausa
T_COMP = T0 + 2 * BEAT                     # SEKURECO queda entera hasta el tiro 3...
COMP = (3 * BEAT + PAUSE) - 2 * BEAT       # ...y las puertas terminan de cerrarse justo con el tiro 4
T_FLIP = T_COMP + COMP + .1
T_SHIFT = T_COMP + COMP
T_CUR = T_FLIP + .55
T_MIN = 2.2                                # como mínimo hasta el 3er balazo (T0 + 2·BEAT ≈ 1,67 s) y medio segundo de su impacto; después, hasta que cargue

css, shots = [], []
for gstart, pat in PATTERNS:
    for off, hx, hy in pat:
        shots.append((T0 + gstart + off, hx, hy))
shots.sort()

pct = lambda sec: f"{sec / P * 100:.2f}%"
imp = FLIGHT / P * 100                       # % del ciclo en que impacta

# ---------- disparos en loop ----------
bullets, debris, shakes_open, shakes_close = [], [], [], []
for k, (t, hx, hy) in enumerate(shots):
    delay = t - FLIGHT
    bullets.append(
        f'<g transform="translate({hx} {hy})"><g class="bl b{k}"><circle r="14" class="bl-body"/>'
        f'<g class="bl-rif"><circle r="10" class="bl-ring"/><circle r="4" class="bl-core"/></g></g>'
        f'</g>')
    css.append(f'.b{k}{{animation:bullet {P}s linear {delay:.2f}s infinite}}'
               f'.sk{k}{{animation:shake {P}s linear {delay:.2f}s infinite}}')
    shakes_open.append(f'<g class="sk{k}">'); shakes_close.append('</g>')
    for j in range(rnd.randint(4, 7)):
        a = rnd.uniform(0, 360); d = rnd.uniform(150, 300); dur = rnd.uniform(.5, 1.0)
        nm = f'dd{k}_{j}'
        debris.append(f'<g transform="translate({hx} {hy}) rotate({a:.0f})"><line class="db {nm}" x1="0" y1="0" x2="7" y2="0"/></g>')
        e = imp + dur / P * 100
        css.append(f'.{nm}{{animation:{nm} {P}s linear {delay:.2f}s infinite}}'
                   f'@keyframes {nm}{{0%,{imp:.2f}%{{opacity:0;transform:translateX(10px) scaleX(2.5)}}'
                   f'{imp + .4:.2f}%{{opacity:1}}{e:.2f}%{{opacity:0;transform:translateX({d:.0f}px) scaleX(.4)}}100%{{opacity:0}}}}')

css.append(f'''@keyframes bullet{{0%{{opacity:0;transform:scale(2.2)}}{imp * .3:.2f}%{{opacity:.85}}
{imp - .05:.2f}%{{opacity:1;transform:scale(.25)}}{imp:.2f}%,100%{{opacity:0;transform:scale(.25)}}}}
@keyframes shake{{0%,{imp:.2f}%{{transform:none}}{imp + 1.5:.2f}%{{transform:translate(-4px,2.5px)}}
{imp + 4:.2f}%{{transform:translate(2.5px,-1.5px)}}{imp + 8:.2f}%{{transform:translate(-1px,.5px)}}{imp + 14:.2f}%,100%{{transform:none}}}}''')

# ---------- impacto a 90° de una bala que gira ----------
# Una bala con estría que pega de frente contra una superficie plana se abre en un
# disco de fragmentos: salen en todas direcciones (radial) y, por el giro que traía,
# todo el disco rota mientras se expande. Resultado: un espiral que se agranda,
# se frena y se apaga. Nada queda orbitando.
import math
LIFE = 1.35                                   # vida de los fragmentos de un impacto (s)
SPIN = 1                                      # todas las balas giran para el mismo lado
bursts = []
nfr = 0
for k, (t_imp, hx, hy) in enumerate(shots):
    delay = t_imp - FLIGHT
    e = imp + LIFE / P * 100
    rot = rnd.uniform(150, 230) * SPIN        # cuánto gira el disco antes de apagarse
    css.append(f'.sw{k}{{animation:sw{k} {P}s linear {delay:.2f}s infinite}}'
               f'@keyframes sw{k}{{0%,{imp:.2f}%{{transform:rotate(0deg);animation-timing-function:cubic-bezier(.15,.7,.3,1)}}'
               f'{e:.2f}%,100%{{transform:rotate({rot:.0f}deg)}}}}')
    count = rnd.randint(14, 18); base = rnd.uniform(0, 360)
    frs = []
    for i in range(count):
        a = base + i * 360 / count + rnd.uniform(-7, 7)
        r = rnd.uniform(200, 320)                     # hasta dónde llega antes de apagarse
        life = LIFE * rnd.uniform(.75, 1.0); e1 = imp + life / P * 100
        tilt = rnd.uniform(18, 34) * SPIN             # el trazo se inclina en la dirección del giro
        nm = f'fr{nfr}'
        if rnd.random() < .62:
            L = rnd.uniform(10, 24); sw = rnd.uniform(2.5, 5)
            el = f'<line class="fr {nm}" x1="{-L / 2:.1f}" y1="0" x2="{L / 2:.1f}" y2="0" stroke-width="{sw:.1f}"/>'
            css.append(
                f'.{nm}{{animation:{nm} {P}s linear {delay:.2f}s infinite}}'
                f'@keyframes {nm}{{0%,{imp - .01:.2f}%{{opacity:0;transform:translateX(0) rotate(0) scaleX(.2)}}'
                f'{imp:.2f}%{{opacity:1;transform:translateX(4px) rotate({tilt:.0f}deg) scaleX(.6);stroke:#FFF3D6;animation-timing-function:cubic-bezier(.1,.75,.3,1)}}'
                f'{imp + (e1 - imp) * .25:.2f}%{{opacity:1;stroke:#FFD48A}}'
                f'{imp + (e1 - imp) * .65:.2f}%{{opacity:.6;stroke:#9BDCD6}}'
                f'{e1:.2f}%,100%{{opacity:0;transform:translateX({r:.0f}px) rotate({tilt:.0f}deg) scaleX(1);stroke:var(--teal-light)}}}}')
        else:
            nv = rnd.choice([3, 4, 4, 5]); pts = []
            for v in range(nv):
                ang = v * 2 * math.pi / nv + rnd.uniform(-.5, .5); rr = rnd.uniform(2.5, 6)
                pts.append(f"{rr * math.cos(ang):.1f},{rr * math.sin(ang):.1f}")
            w0 = rnd.uniform(900, 1600) * rnd.choice([1, -1]); f0 = rnd.uniform(4, 7); tau = rnd.uniform(.35, .6)
            steps = []
            for j in range(25):
                tt = (j / 24) ** 1.5 * life
                th = w0 * tau * (1 - math.exp(-tt / tau)); ph = 2 * math.pi * f0 * tau * (1 - math.exp(-tt / tau))
                sy = .2 + .8 * abs(math.cos(ph)); lum = .55 + .45 * abs(math.cos(ph))
                col = '#FFD9A0' if tt < .18 else f'#{int((110 + 120 * lum) * .82):02X}{int(110 + 120 * lum):02X}{min(int((110 + 120 * lum) * 1.03), 255):02X}'
                steps.append(f'{imp + tt / P * 100:.2f}%{{transform:rotate({th:.0f}deg) scaleY({sy:.2f});fill:{col}}}')
            css.append(f'.tb{nfr}{{animation:tb{nfr} {P}s linear {delay:.2f}s infinite}}'
                       f'@keyframes tb{nfr}{{0%,{imp - .01:.2f}%{{transform:rotate(0) scaleY(1);fill:#C3CDD4}}{"".join(steps)}}}')
            css.append(
                f'.{nm}{{animation:{nm} {P}s linear {delay:.2f}s infinite}}'
                f'@keyframes {nm}{{0%,{imp - .01:.2f}%{{opacity:0;transform:translateX(0)}}'
                f'{imp:.2f}%{{opacity:1;transform:translateX(4px);animation-timing-function:cubic-bezier(.1,.75,.3,1)}}'
                f'{imp + (e1 - imp) * .6:.2f}%{{opacity:.8}}'
                f'{e1:.2f}%,100%{{opacity:0;transform:translateX({r * .85:.0f}px)}}}}')
            el = f'<g class="sh {nm}"><g class="tb{nfr}"><polygon points="{" ".join(pts)}"/></g></g>'
        frs.append(f'<g transform="rotate({a:.1f})">{el}</g>')
        nfr += 1
    bursts.append(f'<g transform="translate({hx} {hy})"><g class="sw{k}">{"".join(frs)}</g></g>')
n = nfr

# ---------- SEKURECO, letra por letra, para compactarla hacia el K ----------
letters = []; letters_bb = [('stem', None, None, None)]; x = 0; capH = 1536; kx = None
for i, ch in enumerate("SEKURECO"):
    d, w, b = glyph_path(ch, x)
    cx = x + (b[0] + b[2]) / 2
    if ch == "K":
        kx = x
        stem = [(192, 0), (192, 1536), (384, 1536), (384, 0)]
        arms = [(384, 864), (639, 864), (1632, 1536), (1920, 1536), (832, 784), (1952, 0), (1664, 0), (640, 704), (384, 704)]
        sd = "M" + "L".join(f"{px + x:.0f} {-py}" for px, py in stem) + "Z"
        ad = "M" + "L".join(f"{px + x:.0f} {-py}" for px, py in arms) + "Z"
        letters.append(('stem', f'<path class="wl kstem" fill="currentColor" stroke="currentColor" stroke-width="{STK}" d="{sd}"/>', x + 288))
        letters.append(('arms', f'<path class="k-arms la la-s" stroke-width="{STK}" stroke-linejoin="miter" d="{ad}"/>', None))
    else:
        letters.append((f'l{i}', f'<path class="wl l{i}" fill="currentColor" stroke="currentColor" stroke-width="{STK}" d="{d}"/>', cx))
        letters_bb.append((f'l{i}', None, cx, (x + b[0] - STK / 2, x + b[2] + STK / 2)))
    x += w + TRACK
ww = x - TRACK
target = kx + 1168                                 # centro de los brazos del K
cur_x0 = kx + 1952 + 260; cur_w, cur_h = 980, 200
prompt_center = (kx + 384 + cur_x0 + cur_w) / 2
shift = ww / 2 - prompt_center                    # ">_" termina centrado bajo el escudo
# SEKURECO está desde el principio. Al final, dos puertas del mismo color del fondo
# se cierran desde los extremos hacia el K y van cortando las letras: la izquierda
# tapa S, E y el asta del K; la derecha tapa U, R, E, C, O. Quedan los brazos del K,
# que se dan vuelta en ">" y el cursor "_" titila al lado.
k_stem_right = kx + 384 + STK / 2 + 20
k_arms_right = kx + 1952 + STK / 2 + 20
pad = 120
door_y, door_h = -capH - 220, capH + 440
doorL = (-pad, k_stem_right + pad)                 # x, ancho
doorR = (k_arms_right, ww + pad - k_arms_right)
doors = (f'<rect class="door door-l" x="{doorL[0]:.0f}" y="{door_y}" width="{doorL[1]:.0f}" height="{door_h}"/>'
         f'<rect class="door door-r" x="{doorR[0]:.0f}" y="{door_y}" width="{doorR[1]:.0f}" height="{door_h}"/>')

wm_letters = ''.join(p for n_, p, _ in letters if n_ != 'arms')
wm_arms = ''.join(p for n_, p, _ in letters if n_ == 'arms')
ws = 520 / ww; wx = CX - 270; base = 770 + capH * ws

sh_inner = shield("ld", "currentColor", "var(--acc)", shx, shy, s).replace('fill="var(--acc)"', 'class="la"')

# viewBox ajustado al escudo (los fragmentos desbordan con overflow visible): así el
# escudo mide exactamente lo que mide el <svg> y se alinea con SEKURECO.
# {{WORDMARK}} lo reemplaza apply.py con el mismo SEKURECO del header, para que la
# transición al header calce al píxel.
vb = f"{shx - 6:.0f} {shy - 6:.0f} {732 * s + 12:.0f} {840 * s + 12:.0f}"
svg = f'''<div class="intro-ov" id="intro" aria-hidden="true">
  <div class="intro-bg"></div>
  <div class="intro-lockup">
    {{{{WORDMARK}}}}
    <svg class="intro-svg" viewBox="{vb}" focusable="false">
      <g class="beat">{''.join(shakes_open)}<g class="sh-in">{sh_inner}</g>{''.join(shakes_close)}</g>
      <g class="ib-frag" transform="translate({CX} {CY})"><g class="beat-r">{''.join(bursts)}</g></g>
      <g class="ib-bul" transform="translate({CX} {CY})">{''.join(debris)}{''.join(bullets)}</g>
    </svg>
  </div>
  <span class="intro-skip">Tocá o presioná una tecla para saltar</span>
</div>'''

static_css = f'''/* ---------- intro: el escudo bajo fuego mientras carga ---------- */
/* Disparos en ráfagas de 3 con 3 patrones en loop; chispas con semilla fija (ver README). */

.intro-ov {{ display: none; }}
.intro .intro-ov {{
  display: grid;
  place-items: center;
  position: fixed;
  inset: 0;
  z-index: 100;
  color: var(--mist);
  cursor: pointer;
  animation: ovOut .7s ease 8s forwards;    /* red de seguridad si el JS no corre */
}}
/* mientras dura la intro la página no scrollea: el visitante arranca siempre arriba.
   "intro-lock" la pone y la saca main.js: si el JS no corre, no hay bloqueo */
html.intro-lock {{ overflow: hidden; }}
/* el fondo es una capa aparte: en la transición se desvanece mientras el logo viaja al header */
.intro-bg {{ position: absolute; inset: 0; background: var(--hero); }}
.intro .intro-ov.out {{ animation: ovOut .7s ease forwards; }}
@keyframes ovOut {{ to {{ opacity: 0; visibility: hidden; }} }}

/* SEKURECO al lado del escudo, con la misma proporción que en el header (palabra = ½ escudo),
   así la transición escala las dos piezas igual. Centro óptico: un poco arriba del centro. */
.intro-lockup {{
  --is: min(150px, calc((100vw - 48px) / 6.6));
  position: relative;
  display: flex;
  align-items: center;
  gap: calc(var(--is) * .3);
  margin-top: -8vh;
}}
.intro-svg {{ height: var(--is); width: auto; overflow: visible; transform-origin: 0 0; }}
.intro-wm-svg {{ height: calc(var(--is) / 2); width: auto; overflow: visible; transform-origin: 0 0; }}
/* durante la intro el logo del header no se ve: lo reemplaza el que viaja desde el centro */
.intro .top .logo-wm, .intro .top .logo-shield {{ visibility: hidden; }}
/* salida: se apagan balas y fragmentos y se frena el latido para medir sin movimiento */
.leaving .ib-frag, .leaving .ib-bul, .leaving .intro-skip {{ opacity: 0; transition: opacity .25s ease; }}
.leaving .beat, .leaving .beat g, .leaving .beat-r {{ animation: none !important; }}
.intro-skip {{
  position: absolute;
  left: 0; right: 0; bottom: var(--sp4);
  text-align: center;
  font-size: .8125rem;
  color: #6F8496;
}}

.sh-in {{
  transform-box: fill-box;
  transform-origin: center;
  animation: shIn .9s cubic-bezier(.2, .8, .2, 1) both;
}}
@keyframes shIn {{ from {{ opacity: 0; transform: scale(.9); }} }}

.bl {{ opacity: 0; }}
.bl-body {{ fill: #C3CDD4; }}
.bl-ring {{ fill: none; stroke: #5E6E7C; stroke-width: 2.5; stroke-dasharray: 4 3; }}
.bl-core {{ fill: #8A99A6; }}
.bl-rif {{ animation: spin .5s linear infinite; }}
.db {{ stroke: #FFD98A; stroke-width: 3; stroke-linecap: round; opacity: 0; }}

/* cada impacto abre un disco de fragmentos que se expande girando y se apaga */
.fr {{ stroke-linecap: round; opacity: 0; }}
.sh {{ opacity: 0; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}

/* palpitación tranquila: un latido doble suave cada 1,7 s */
.beat {{
  transform-box: view-box;
  transform-origin: {CX}px {CY}px;
  animation: beat 1.7s ease-in-out {T_BEAT}s infinite;
}}
.beat-r {{ animation: beat 1.7s ease-in-out {T_BEAT + .06:.2f}s infinite; }}
@keyframes beat {{
  0%   {{ transform: scale(1); }}
  9%   {{ transform: scale(1.022); }}
  20%  {{ transform: scale(1); }}
  30%  {{ transform: scale(1.012); }}
  44%  {{ transform: scale(1); }}
  100% {{ transform: scale(1); }}
}}
/* la intro es solo el escudo bajo fuego: la marca vive en el header */

'''
open(BUILD / 'intro.html', 'w').write(svg)
open(BUILD / 'intro.css', 'w').write(static_css + '\n'.join(css) + '\n\n')
print('intro ok:', len(shots), 'disparos por loop,', n, 'fragmentos')
