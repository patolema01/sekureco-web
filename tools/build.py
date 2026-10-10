"""Build de Cloudflare Pages: copia el sitio a dist/ y le pone una huella de contenido a los
archivos que cambian con cada versión (styles.css, main.js, theme.js → styles.<hash8>.css, …),
reescribiendo las referencias en index.html y 404.html.

Así un navegador que guardó el CSS o el JS de una versión anterior nunca lo mezcla con el HTML
nuevo: el HTML nuevo pide otro nombre. En el repo los archivos siguen con su nombre normal.
También agrega a dist/_headers la caché de un año (immutable) para esos nombres, y solo para esos.

Uso (es el comando de build de Pages; directorio de salida: dist):
    python3 tools/build.py
Sin dependencias: solo la biblioteca estándar.
"""
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

# lo que se publica (nada más: ni tools/, ni CLAUDE.md, ni README.md)
SITIO = ["index.html", "404.html", "_headers", "favicon.svg", "robots.txt", ".well-known", "assets"]
# los que llevan huella de contenido
CON_HUELLA = ["assets/styles.css", "assets/main.js", "assets/theme.js"]
PAGINAS = ["index.html", "404.html"]


def huella(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for nombre in SITIO:
        src = ROOT / nombre
        if src.is_dir():
            shutil.copytree(src, DIST / nombre)
        else:
            shutil.copy2(src, DIST / nombre)

    renombres = {}
    for rel in CON_HUELLA:
        src = DIST / rel
        nuevo = src.with_name(f"{src.stem}.{huella(src)}{src.suffix}")
        src.rename(nuevo)        # sin la copia sin huella: un HTML viejo no puede mezclarse con el CSS nuevo
        renombres["/" + rel] = "/" + nuevo.relative_to(DIST).as_posix()

    # un año, immutable: solo para los nombres con huella (en _headers del repo no está, a propósito)
    with open(DIST / "_headers", "a", encoding="utf-8") as h:
        h.write("\n# (agregado por tools/build.py) CSS y JS con huella de contenido\n")
        for nuevo in renombres.values():
            h.write(f"{nuevo}\n  Cache-Control: public, max-age=31536000, immutable\n\n")

    for pagina in PAGINAS:
        p = DIST / pagina
        html = p.read_text(encoding="utf-8")
        for viejo, nuevo in renombres.items():
            referencias = html.count(f'"{viejo}"')
            assert referencias == 1, f"{pagina}: esperaba 1 referencia a {viejo} y hay {referencias}"
            html = html.replace(f'"{viejo}"', f'"{nuevo}"')
        p.write_text(html, encoding="utf-8")

    for viejo, nuevo in renombres.items():
        print(f"{viejo} → {nuevo}")
    print(f"dist listo: {sum(1 for f in DIST.rglob('*') if f.is_file())} archivos")


if __name__ == "__main__":
    main()
