# tools/

Scripts que generan lo que no conviene editar a mano: el logo, la intro y el logo del header.
Están acá para que cualquiera (o Claude) pueda cambiar una animación y regenerar todo igual.

## Requisitos (una sola vez)

```bash
pip install fonttools brotli
```

## Regenerar

```bash
python3 tools/brand.py    # assets/brand/*.svg y favicon.svg
python3 tools/intro.py    # intro: escudo bajo fuego (HTML + CSS en tools/build/)
python3 tools/header.py   # header: escudo + SEKURECO que se cierra en ">_"
python3 tools/apply.py    # mete lo generado en index.html, 404.html y assets/styles.css
```

Con los parámetros actuales el resultado es idéntico byte a byte al que está publicado.

## Dónde se toca cada cosa

| Qué querés cambiar | Archivo | Variables |
|---|---|---|
| Ritmo de los tiros | `intro.py` | `BPM`, `PAUSE`, `T0`, `P`, `PATTERNS` |
| Duración mínima de la intro | `intro.py` (`T_MIN`) y `assets/main.js` (`MIN`) | tienen que coincidir |
| Fragmentos del impacto | `intro.py` | `LIFE`, cantidad por bala, radios, mezcla chispas/esquirlas |
| Latido | `intro.py` | `T_BEAT` y `@keyframes beat` |
| Geometría del escudo | `brand.py` | `O`, `I`, `ARM`, `DIAG` y los cortes |
| Peso y espaciado de la palabra | `brand.py` | `STK`, `TRACK` |
| Cierre de puertas del header | `assets/styles.css` | bloque "header: escudo + SEKURECO" |

`tools/fonts/michroma.woff2` (licencia OFL) se usa solo para generar los trazos del logo;
el sitio no la carga.
