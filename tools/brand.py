"""Logo SEKURECO: escudo redibujado + palabra en Michroma. Genera assets/brand/*.svg y favicon.svg.
Uso: python3 tools/brand.py"""
import re, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

NAVY="#0F2032"; TEAL="#006C6E"; MIST="#EEF3F3"; TEAL_L="#3FB8B1"

# ---------- escudo (espacio 0..732 x 0..840) ----------
O="M27 120L366 15L705 120V420C705 600 560 740 366 815C172 740 27 600 27 420Z"
I="M132 195L366 122L600 195V420C600 545 500 650 366 705C232 650 132 545 132 420Z"
ARM="M27 369L356 537L408 537L474 489L132 312L27 312Z"
DIAG="M371 244L705 402L705 460L600 470L262 288Z"
Lt=lambda x:275+0.381*(x-600); Ld=lambda x:244+0.473*(x-371)
La=lambda x:355.5+0.511*x;     Lc=lambda x:447.5+0.39*x
def poly(pts): return "M"+"L".join(f"{x:.1f} {y:.1f}" for x,y in pts)+"Z"
CUT_A=poly([(342,-10),(390,-10),(390,140),(342,140)])
CUT_B=poly([(560,Lt(560)),(760,Lt(760)),(760,Ld(760)),(560,Ld(560))])
CUT_C=poly([(-10,La(-10)),(140,La(140)),(140,Lc(140)),(-10,Lc(-10))])
TEALZ=poly([(390,-10),(760,-10),(760,Lt(760)),(390,Lt(390))])

def shield(uid, navy, teal, x=0, y=0, s=1.0):
    return f'''<g transform="translate({x} {y}) scale({s})">
<defs><mask id="m{uid}" maskUnits="userSpaceOnUse" x="-20" y="-20" width="780" height="880">
<rect x="-20" y="-20" width="780" height="880" fill="#fff"/>
<path d="{CUT_A}{CUT_B}{CUT_C}{TEALZ}" fill="#000"/></mask>
<clipPath id="c{uid}"><path d="{TEALZ}"/></clipPath></defs>
<g mask="url(#m{uid})" fill="{navy}"><path fill-rule="evenodd" d="{O}{I}"/><path d="{ARM}"/><path d="{DIAG}"/></g>
<path clip-path="url(#c{uid})" fill="{teal}" fill-rule="evenodd" d="{O}{I}"/>
</g>'''

# ---------- wordmark con Michroma ----------
f=TTFont(str(ROOT / 'tools' / 'fonts' / 'michroma.woff2'))
gs=f.getGlyphSet(); cmap=f.getBestCmap()
def glyph_path(ch, x0):
    pen=SVGPathPen(gs); g=cmap[ord(ch)]
    gs[g].draw(TransformPen(pen,(1,0,0,-1,x0,0)))
    bp=BoundsPen(gs); gs[g].draw(bp)
    d=re.sub(r'-?\d+\.\d+',lambda m:f"{float(m.group()):.0f}",pen.getCommands())
    return d, gs[g].width, bp.bounds
TRACK=200
STK=38
def wordmark(uid, navy, teal):
    x=0; parts=[]; capH=None
    for ch in "SEKURECO":
        d,w,b=glyph_path(ch,x)
        capH=b[3]
        if ch=="K":
            # el K se arma en dos piezas: asta azul y brazos "<" en teal (así se pueden animar)
            stem=[(192,0),(192,1536),(384,1536),(384,0)]
            arms=[(384,864),(639,864),(1632,1536),(1920,1536),(832,784),(1952,0),(1664,0),(640,704),(384,704)]
            sd="M"+"L".join(f"{x+gx:.0f} {-y}" for gx in [x] for (x,y) in stem)+"Z"
            ad="M"+"L".join(f"{x+gx:.0f} {-y}" for gx in [x] for (x,y) in arms)+"Z"
            parts.append(f'<path fill="{navy}" stroke="{navy}" stroke-width="{STK}" d="{sd}"/>'
                         f'<path class="k-arms" fill="{teal}" stroke="{teal}" stroke-width="{STK}" stroke-linejoin="miter" d="{ad}"/>')
        else:
            parts.append(f'<path fill="{navy}" stroke="{navy}" stroke-width="{STK}" d="{d}"/>')
        x+=w+TRACK
    return "".join(parts), x-TRACK, capH

def build(navy, teal, uid):
    wm, ww, capH = wordmark(uid, navy, teal)
    # vertical: escudo arriba, palabra abajo
    sw = ww*0.38; ss = sw/732
    wscale = 1.0
    sh = 840*ss
    gap = capH*0.9
    W = ww; H = sh + gap + capH
    vert = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -40 {W+80:.0f} {H+80:.0f}" role="img" aria-label="SEKURECO"><title>SEKURECO</title>'
            + shield(uid+"v", navy, teal, (W-sw)/2, 0, ss)
            + f'<g transform="translate(0 {sh+gap+capH:.0f})">{wm}</g></svg>\n')
    # horizontal: escudo a la izquierda
    hs = capH*2.1/840; hw = 732*hs
    hgap = capH*0.7
    HW = hw + hgap + ww; HH = 840*hs
    base = HH/2 + capH/2
    horiz = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 {HW+40:.0f} {HH+40:.0f}" role="img" aria-label="SEKURECO"><title>SEKURECO</title>'
             + shield(uid+"h", navy, teal, 0, 0, hs)
             + f'<g transform="translate({hw+hgap:.0f} {base:.0f})">{wm}</g></svg>\n')
    return vert, horiz

if __name__ == '__main__':
    out=str(ROOT / 'assets' / 'brand') + '/'
    for fn in os.listdir(out): os.remove(out+fn)
    v,h=build(NAVY,TEAL,"a"); open(out+'sekureco-vertical.svg','w').write(v); open(out+'sekureco-horizontal.svg','w').write(h)
    v,h=build(MIST,TEAL_L,"b"); open(out+'sekureco-vertical-blanco.svg','w').write(v); open(out+'sekureco-horizontal-blanco.svg','w').write(h)
    v,h=build("#000","#000","c"); open(out+'sekureco-vertical-mono.svg','w').write(v); open(out+'sekureco-horizontal-mono.svg','w').write(h)
    open(out+'escudo.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 772 880" role="img" aria-label="SEKURECO"><title>SEKURECO</title>{shield("e",NAVY,TEAL)}</svg>\n')
    fav=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-130 -90 992 1000"><rect x="-130" y="-90" width="992" height="1000" rx="200" fill="{NAVY}"/>{shield("f",MIST,TEAL_L)}</svg>\n'
    open(out+'icono.svg','w').write(fav); open(str(ROOT / 'favicon.svg'),'w').write(fav)
    print('logos ok')
