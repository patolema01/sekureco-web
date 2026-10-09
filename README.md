# sekureco-web

Sitio estático de SEKURECO S.A., publicado en https://sekureco.ar con Cloudflare Pages.
Sin framework, sin build, sin dependencias: lo que está en el repo es lo que se sirve.

## Estructura

```
index.html            página principal
404.html              página de error
favicon.svg
_headers              headers de seguridad (CSP, HSTS, etc.) que aplica Cloudflare Pages
robots.txt
.well-known/security.txt
assets/
  styles.css          único CSS
  theme.js            corre antes de pintar: tema guardado y si se muestra la intro
  main.js             reloj del visor, selector de tema y salto de la intro
  fonts/archivo.woff2 tipografía Archivo (OFL), servida desde el propio dominio
  brand/              logo SEKURECO en SVG: vertical, horizontal, blanco, mono, escudo, icono
tools/                scripts que generan logo, intro y header (ver tools/README.md)
CLAUDE.md             contexto completo del proyecto para Claude (y para cualquier persona nueva)
```

## Reglas del proyecto (no negociables)

1. Nada de recursos externos: ni fuentes de Google, ni CDNs, ni analytics, ni embeds. Todo se sirve desde sekureco.ar.
2. Nada de JS ni CSS inline (`<script>…</script>`, `style="…"`, `onclick=`). La CSP los bloquea y el sitio se rompe.
3. Nunca secretos en el repo (tokens, claves, `.env`). El repo es público.
4. `main` está protegida: los cambios entran por Pull Request y los aprueba Pato.
5. Toda animación tiene que respetar `prefers-reduced-motion`.
6. Paleta oficial (sacada del logo): azul `#0F2032`, teal `#006C6E`, teal claro para fondos oscuros `#3FB8B1`, niebla `#EEF3F3`.

## Diseño

- **Proporciones:** el contenido arranca siempre sobre la línea áurea (títulos en la columna de 38,2 %, contenido en la de 61,8 %). Tipografía en pasos de √φ y espaciado en la serie de Fibonacci (13, 21, 34, 55, 89, 144). Los paddings de sección son asimétricos a propósito.
- **Intro:** el escudo recibe fuego continuo, en un loop de 5 s: el primer impacto cae a los 0,37 s y llegan dos ráfagas de 3 tiros a 92 bpm separadas por una pausa de 0,37 s; se repite hasta que termina la carga (mínimo un loop); cada bala pega de frente (90°) y, por el giro que trae, se abre en un disco de chispas y esquirlas que se expande rotando en espiral, se frena y se apaga; nada queda orbitando (semilla fija); el conjunto late suave como un pulso en reposo. La intro es solo el escudo: la marca vive en el header. se ve una vez por sesión, se salta con un toque o una tecla y no aparece si el visitante tiene activado "reducir movimiento" o si el JS no carga.
- **Header:** escudo (link al inicio) + SEKURECO. Cuando termina la intro, dos puertas del color del fondo se cierran hacia el K cortando las letras, el "<" se da vuelta y queda ">_" con el cursor titilando. Ese ">_" es el botón del menú: al abrirlo, el ">" gira y apunta hacia abajo. El cierre se ve una vez por sesión; en el resto de las páginas el header ya arranca en ">_". Sin JS se ve SEKURECO completo.
- **Prompt:** el ">" que aparece en la web (menú, título de Ciberseguridad) son los brazos del K invertidos.

## Cómo proponer un cambio (Leandro, Gonzalo)

Desde github.com: abrí el archivo, tocá el lápiz, editá, y en "Commit changes" elegí
"Create a new branch". GitHub abre el Pull Request solo. Cloudflare genera una URL de
vista previa para esa rama; cuando Pato lo aprueba, se publica en sekureco.ar.

## Configuración de Cloudflare que el sitio necesita

- Desactivar **Email Address Obfuscation** (Scrape Shield): reescribe los `mailto:` e inyecta un script que la CSP bloquea.
- Desactivar **Rocket Loader** y la inyección automática de **Web Analytics** por el mismo motivo.
- Email Routing: crear las direcciones `contacto@` y `seguridad@` (las usa el sitio).
- SSL/TLS: modo Full (strict), "Always Use HTTPS" activado.
