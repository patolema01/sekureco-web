"""Header: escudo (link al inicio) + SEKURECO que se cierra con puerta doble hasta dejar
">_", que queda fijo como botón del menú desplegable."""
import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tools" / "build"; BUILD.mkdir(exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand
shield, glyph_path, TRACK, STK = brand.shield, brand.glyph_path, brand.TRACK, brand.STK

capH = 1536
letters, arms_d = [], None
x = 0; kx = None
for i, ch in enumerate("SEKURECO"):
    d, w, b = glyph_path(ch, x)
    if ch == "K":
        kx = x
        stem = [(192, 0), (192, 1536), (384, 1536), (384, 0)]
        arms = [(384, 864), (639, 864), (1632, 1536), (1920, 1536), (832, 784), (1952, 0), (1664, 0), (640, 704), (384, 704)]
        letters.append("M" + "L".join(f"{px + x:.0f} {-py}" for px, py in stem) + "Z")
        arms_d = "M" + "L".join(f"{px + x:.0f} {-py}" for px, py in arms) + "Z"
    else:
        letters.append(d)
    x += w + TRACK
ww = x - TRACK
cur_x0 = kx + 1952 + 260; cur_w, cur_h = 980, 200
k_stem_right = kx + 384 + STK / 2 + 20
k_arms_right = kx + 1952 + STK / 2 + 20
pad = 90
vb_y, vb_h = -capH - pad, capH + 2 * pad
vb_x, vb_w = -pad, cur_x0 + cur_w + pad if cur_x0 + cur_w > ww else ww + 2 * pad

# escudo solo (link al inicio)
sh = shield("hdr", "currentColor", "var(--acc)").replace('fill="var(--acc)"', 'class="la"')
shield_svg = f'<svg class="logo-shield" viewBox="-20 -20 772 880" aria-hidden="true" focusable="false">{sh}</svg>'

paths = ''.join(f'<path d="{d}"/>' for d in letters)
wm_svg = (f'<svg class="logo-wm" viewBox="{vb_x} {vb_y} {vb_w + pad:.0f} {vb_h}" aria-hidden="true" focusable="false">'
          f'<g class="wm-letters" fill="currentColor" stroke="currentColor" stroke-width="{STK}">{paths}</g>'
          f'<rect class="door door-l" x="{-pad - 20}" y="{vb_y}" width="{k_stem_right + pad + 20:.0f}" height="{vb_h}"/>'
          f'<rect class="door door-r" x="{k_arms_right:.0f}" y="{vb_y}" width="{ww + pad + 20 - k_arms_right:.0f}" height="{vb_h}"/>'
          f'<path class="k-arms la la-s" stroke-width="{STK}" stroke-linejoin="miter" d="{arms_d}"/>'
          f'<rect class="hcur" x="{cur_x0:.0f}" y="{-cur_h}" width="{cur_w}" height="{cur_h}"/></svg>')

open(BUILD / 'header-shield.svg', 'w').write(shield_svg)
open(BUILD / 'header-wordmark.svg', 'w').write(wm_svg)
print('header ok')
