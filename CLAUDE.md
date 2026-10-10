# CLAUDE.md — sitio de SEKURECO (sekureco.ar)

Contexto para Claude (Claude Code en la VM `agentes` o un proyecto de claude.ai) y para
cualquier persona que se sume. Leelo entero antes de tocar algo.

## Qué es

Sitio institucional de **SEKURECO S.A.**, empresa de seguridad electrónica y ciberseguridad
de Buenos Aires: videovigilancia con análisis por IA monitoreada por un equipo chico,
alarmas cableadas (DSC PowerSeries Neo), cámaras TP-Link VIGI, instalación con Cat6, y
servicios de ciberseguridad (diagnóstico, redes segmentadas y SSID, firewall y VPN,
respaldos, capacitación).

- Responsable técnico: Pato (Patricio Lema). Aprueba todo lo que entra a `main`.
- También editan, por Pull Request: Leandro y Gonzalo.
- Idioma del sitio y de la comunicación: español rioplatense, con voseo.

## Reglas duras (no negociables)

1. **Sin recursos externos.** Nada de Google Fonts, CDNs, analytics, embeds ni scripts de terceros. Todo se sirve desde sekureco.ar.
2. **Sin JS ni CSS inline.** Nada de `<script>…</script>`, `style="…"` ni `onclick=`. La CSP de `_headers` los bloquea y el sitio se rompe.
3. **Sin secretos en el repo.** Es público. Los tokens de Cloudflare viven solo en `~/.config/sekureco/` en `agentes`.
4. **`main` protegida.** Todo entra por Pull Request con aprobación de Pato.
5. **Movimiento con respeto.** Toda animación tiene que respetar `prefers-reduced-motion`.
6. **No tocar DNS ni MX.** El correo @sekureco.ar funciona con Cloudflare Email Routing; un cambio de DNS lo puede cortar.
7. **Nada sin probar.** Antes de proponer un cambio, verificarlo (abrir la página, mirar consola, probar en celular).
8. **Lo generado no se edita a mano.** Logo, intro y logo del header salen de `tools/`. Si hay que cambiarlos, se cambia el script y se regenera (ver `tools/README.md`).

## Infraestructura

| Pieza | Dónde |
|---|---|
| Hosting | Cloudflare Pages conectado al repo `patolema01/sekureco-web`; push a `main` publica, cada rama genera un preview. Build: `python3 tools/build.py` → `dist/` (copia solo el sitio y les pone huella de contenido a styles.css, main.js y theme.js: `styles.<hash8>.css`, etc.). HTML con `no-cache` y fuentes y marca una semana (en `_headers`); CSS/JS con huella, un año `immutable` (esa regla la agrega build.py en `dist/_headers`, solo para los nombres con huella). Así un navegador nunca mezcla el HTML nuevo con un CSS o JS viejo en caché |
| DNS y correo | Cloudflare (zona sekureco.ar). Email Routing: pato@, leandro@, gjlema@ (Gonzalo) y administracion@ (también a Gonzalo); catch-all en Drop. El sitio usa contacto@ y seguridad@ |
| Dominio | sekureco.ar, a nombre de Gonzalo en NIC Argentina, delegado a Cloudflare |
| Repo | `patolema01/sekureco-web` en la cuenta personal de Pato, repo público; Leandro y Gonzalo editan como colaboradores del repo (permiso de escritura, no hay organización). CODEOWNERS `* @patolema01`, ruleset sobre `main`. Más adelante se puede transferir a una organización `sekureco` |
| Desarrollo | Claude Code en la VM `agentes` del homelab de Pato, en `~/proyectos/sekureco-web` |

Configuración de Cloudflare que el sitio necesita: Email Address Obfuscation, Rocket Loader
y la inyección automática de Web Analytics **apagados** (inyectan scripts que la CSP bloquea);
SSL Full (strict) y Always Use HTTPS.

## Estructura

```
index.html  404.html  favicon.svg  _headers  robots.txt  .well-known/security.txt
assets/styles.css     todo el CSS
assets/theme.js       corre antes de pintar: tema guardado, si hay intro, estado del header
assets/main.js        selector de tema, intro, menú ">_", header que se esconde al bajar
assets/fonts/         Archivo (OFL), servida desde el propio dominio
assets/brand/         logo en SVG (vertical, horizontal, blanco, mono, escudo, icono)
tools/                generadores de logo, intro y header; build.py arma dist/ para Pages
```

## Sistema de diseño

**Paleta (sacada del logo original):**

| Token | Hex | Uso |
|---|---|---|
| azul | `#0F2032` | fondos oscuros, texto en modo claro |
| teal | `#006C6E` | acentos y botones sobre fondo claro |
| teal claro | `#3FB8B1` | acentos sobre fondo oscuro |
| niebla | `#EEF3F3` | texto sobre fondo oscuro, fondos alternos |

**Tipografía:** Archivo variable (ancho 125 % en títulos, 100 % en texto). Escala en pasos
de √φ: 17 → 21,6 → 27,5 → 44,5 → 72 px.

**Proporciones:** títulos en la columna de 38,2 % y contenido en la de 61,8 %; todo el
contenido arranca sobre la misma línea áurea. Espaciado Fibonacci (13, 21, 34, 55, 89,
144 px). Paddings asimétricos a propósito: más aire arriba que abajo.

**Modo oscuro:** sigue al sistema; botón luna/sol en el header; la elección se guarda en
`localStorage` ("tema").

**Logo:** el escudo con la S fue redibujado en vector a partir del original hecho con IA;
la palabra va en Michroma engrosada, con los brazos del K en teal. El "<" de esos brazos,
invertido, es el ">" de terminal que aparece en el sitio.

## Animaciones (decididas con Pato; no cambiar sin consultarle)

**Intro (SEKURECO + escudo bajo fuego):**
- Loop de 5 s. El primer impacto cae a los 0,37 s. Dos ráfagas de 3 tiros a 92 bpm (0,652 s entre tiros), separadas por una pausa de 0,37 s (la última queda en 0,347 s para cerrar justo en 5 s).
- Balas chicas, de a una, que llegan de frente girando (vuelo 0,33 s). Sin fogonazo ni halos.
- Cada bala pega a 90° y se abre en un disco de chispas y esquirlas metálicas que se expande rotando en espiral (por el giro de la bala), se frena y se apaga. Nada queda orbitando. Todas giran para el mismo lado. Las esquirlas giran sobre su eje y dan vueltas de campana, frenándose.
- Latido suave (doble, cada 1,7 s) desde la primera pausa.
- Al centro, SEKURECO al lado del escudo (la palabra mide la mitad del alto del escudo). En la web, la primera E (la de SEK) lleva sus tres barras en teal, como los brazos del K; el palo queda blanco y la segunda E es toda blanca. Los archivos de marca (assets/brand, favicon) no cambian. La copia de la palabra que usa la intro la genera `tools/header.py` aparte: solo las letras, sin la ventana, el "≡" ni el cursor del header. Al terminar, las dos piezas se achican y viajan cada una a su lugar en el header (SEKURECO a la izquierda, escudo a la derecha) mientras el fondo se desvanece; cada una se escala a su tamaño del header y aterrizan exactamente sobre el logo; ahí arranca el cierre.
- Dura como mínimo 3 balazos: el vuelo sale 3,0 s después de que arranca la animación, con el espiral del último impacto ya apagado (los tiempos se cuentan desde el primer render, no desde la navegación). Del 4º disparo no se ve nada. Si la página no cargó, sigue el fuego hasta que cargue. Mientras dura, la página no scrollea. Una vez por sesión, se salta con un toque o una tecla, no aparece con "reducir movimiento" ni sin JS.

**Header:**
- A la izquierda SEKURECO; a la derecha el botón de tema y el escudo (link al inicio). Al terminar la intro, el cierre "ventana" (≈1 s, un solo movimiento): toda la palabra se desplaza a la izquierda como un bloque y se ve a través de una ventana (clipPath). Su borde izquierdo está fijo en el borde izquierdo del ">" final (S, E y el palo del K salen por ahí) y el derecho es un telón que avanza tapando U, R, E, C, O y frena con un corte seco 150 ms antes que el bloque (a la vista, quieto ~115 ms antes de que se asiente el ">"). El "<" viaja con el bloque y rueda 180° antihorario en el último 60 % del viaje hasta ser ">" (sin "-" en la punta). En el primer tercio se desvanecen la unión y el palo del K, y el palo de la E; las barras de arriba y del medio de la E bajan y se funden en la de abajo (380 ms) y queda un "_" teal. Ese "_" va con el bloque el primer 35 % del movimiento y después viaja por la línea de base, por delante de las letras y por detrás del ">", sin cambiar de tamaño: llega a su lugar (a un espacio del ">") en el mismo instante en que se asienta el ">", y ahí es el cursor (la barra de abajo del "≡"). El palo del K se desvanece porque el "<" al rodar barre un círculo de 2209 u y entre el palo y la U hay 1930 u, así que con el palo visible se superponían. Todo lo genera `tools/header.py` (SVG + bloque de CSS).
- Queda ">≡": el botón del menú desplegable (Seguridad electrónica, Ciberseguridad, Cómo trabajamos, Cómo elegimos, Contacto). El "≡" son exactamente las barras de la primera E, en la misma escala, proporción y trazo (abajo 1344, medio 1261, arriba 1316 u de largo, más el trazo de 19 u en cada punta), alineadas a la izquierda como en la E y con su borde izquierdo a un espacio del ">". La de abajo es el cursor. El ícono ocupa exactamente el alto del ">", igual que la E. Degradé en el teal de acento: abajo 100 %, medio 60 %, arriba 20 % (la de 20 % se ve tenue: contraste 1,44:1 sobre el fondo del header). El ">" mide 17 px en celular (texto base) y 21,6 px en escritorio (17 × √φ, el paso siguiente de la escala); SEKURECO crece en proporción y en 320 px, sin JS, entra completa al lado del botón de tema.
- Al llegar, el cursor (el "_" que viajó) parpadea a 92 bpm, un parpadeo por negra, corte seco: encendido 326 ms · apagado 326 · encendido 326 · apagado 326 · tercer encendido, y no se apaga más. En el tercer encendido el "≡" se completa a 216 bpm (T = 277,8 ms), de abajo hacia arriba y fundiéndose (nunca se apagan): la barra del medio de 0 a 60 % desde 1·T, la de arriba de 0 a 20 % desde 2·T, 1,6·T cada una, `cubic-bezier(.25, .1, .25, 1)`; a los 3,6 s de empezar el cierre queda fijo. El "_" que viaja va por delante de las letras blancas (nunca queda tapado) y por detrás del ">": el SVG tiene tres capas que se mueven juntas (letras con la ventana · "_" recortado solo por el borde izquierdo · ">" con la ventana).
- Al abrir el menú, el ">" gira y apunta hacia abajo y las dos barras de arriba bajan sin cambiar de largo y se funden en la de abajo (150 ms), que queda como un "_" titilando (326 / 326). Al cerrar suben a su lugar. Al cerrar, todo vuelve en 150 ms y el "≡" queda fijo. Con mouse, el hover pone las tres barras al 100 %. El botón tiene aria-label "Menú de SEKURECO", aria-expanded y title "Menú", y un área táctil invisible de 44 px como mínimo. Se cierra con Esc, tocando afuera o eligiendo una sección. Abrirlo durante la secuencia la completa de una.
- **Menú (índice, no copia del contenido):** con mouse se abre con el puntero 120 ms sobre el ">≡" visible y se cierra 300 ms después de salir de botón + menú; un click lo deja fijado. Al abrir se ven solo los 5 ítems, ningún árbol. Cada ítem abre su árbol estilo terminal (`raíz/` + ramas ├ └, línea por línea a ~30 ms), uno solo a la vez: con mouse y lugar, a la derecha en su propia capa (hover 150 ms o click; la lista no se mueve; cruzar otro ítem < 150 ms no cambia el árbol; fuera del ítem y su árbol 300 ms, se cierra); sin hover o sin lugar, acordeón debajo (el tap en el ítem no navega, navega la raíz). Teclado: ↑↓, → / Enter entra, ← vuelve, Esc cierra y devuelve el foco. Contacto lleva contacto@ y seguridad@ con un botón "copiar" (también en la sección), que sin JS ni portapapeles no se muestra.
- El cierre se ve una vez por sesión; después (y con "reducir movimiento") el header arranca ya en ">≡", fijo. Sin JS se ve SEKURECO completo.
- Es sticky: se esconde al bajar (más de 8 px, a más de 120 px del tope) y vuelve al subir. Con mouse también vuelve dejando el puntero 120 ms en la franja de 21 px de arriba; se queda mientras el puntero esté encima y, al salir, a los 600 ms se esconde si la página sigue scrolleada. No se esconde con el menú abierto, durante la intro ni con el foco de teclado adentro. Con scroll lleva una sombra sutil; el ">≡" queda fijo. Los títulos sticky de sección bajan mientras el header está visible.

**Indicador de carga:** `SK.cargando(contenedor)` (en `assets/main.js`) inserta el escudo bajo fuego, solo, sin SEKURECO, y devuelve una función para quitarlo. Usarlo para cualquier cosa que cargue (por ejemplo, el envío de un formulario). Tamaño con `--sk-size` en el contenedor.

**Hero:** título, bajada y botones en la columna áurea (61,8 %); la derecha queda libre a la espera de fotos reales del banco de pruebas o de instalaciones (hay un comentario en `index.html` marcando el lugar). El visor de cámara animado se sacó por poco serio.

## Pendientes y decisiones abiertas

- **Marca:** SECUREKO está registrada en INPI (clase 45) por un tercero, que también tiene sekureco.com.ar. Hay que consultar con un agente de marcas antes de invertir más en la identidad.
- **Contenido que falta:** número de WhatsApp, sección "Para quién", "Nosotros", preguntas frecuentes, fotos reales del banco de pruebas o instalaciones.
- **Material de capacitación:** el sitio promete una presentación para que el equipo cliente se quede; todavía no existe.
- **Mejoras propuestas y no implementadas:** header compacto al scrollear, respuesta inmediata al tocar, intro corta para quien vuelve. Cuando haya más páginas: View Transitions y precarga con Speculation Rules (por header, para respetar la CSP).
- **No hacer:** fade-in al scrollear, parallax, contadores animados sin datos reales, cursor personalizado, testimonios o logos de clientes que no existan.
