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
| Hosting | Cloudflare Pages conectado al repo `patolema01/sekureco-web`; push a `main` publica, cada rama genera un preview |
| DNS y correo | Cloudflare (zona sekureco.ar). Email Routing: pato@, leandro@ y una para Gonzalo; catch-all en Drop. El sitio usa contacto@ y seguridad@ |
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
assets/main.js        reloj del visor, selector de tema, intro, menú ">_"
assets/fonts/         Archivo (OFL), servida desde el propio dominio
assets/brand/         logo en SVG (vertical, horizontal, blanco, mono, escudo, icono)
tools/                generadores de logo, intro y header
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
- Al centro, SEKURECO al lado del escudo (misma proporción que en el header). Al terminar, las dos piezas se achican y viajan cada una a su lugar en el header (SEKURECO a la izquierda, escudo a la derecha) mientras el fondo se desvanece; aterrizan exactamente sobre el logo del header y ahí arranca el cierre de puertas.
- Dura como mínimo un loop y sigue mientras la página no terminó de cargar. Mientras dura, la página no scrollea. Una vez por sesión, se salta con un toque o una tecla, no aparece con "reducir movimiento" ni sin JS.

**Header:**
- A la izquierda SEKURECO; a la derecha el botón de tema y el escudo (link al inicio). Al terminar la intro, dos puertas del color del fondo se cierran desde los extremos hacia el K cortando las letras; la unión horizontal del K se desvanece, el "<" se da vuelta en un ">" limpio (sin "-" en la punta), se desliza hasta el borde izquierdo y queda ">_" con el cursor titilando.
- ">_" es el botón del menú desplegable (Servicios, Cómo trabajamos, Cómo elegimos, Contacto). Al abrir, el ">" gira y apunta hacia abajo. Se cierra con Esc, tocando afuera o eligiendo una sección.
- El cierre se ve una vez por sesión; después el header arranca ya en ">_". Sin JS se ve SEKURECO completo.

**Indicador de carga:** `SK.cargando(contenedor)` (en `assets/main.js`) inserta el escudo bajo fuego, solo, sin SEKURECO, y devuelve una función para quitarlo. Usarlo para cualquier cosa que cargue (por ejemplo, el envío de un formulario). Tamaño con `--sk-size` en el contenedor.

**Hero:** visor de cámara animado (una persona cruza, entra a la zona 1 y se dispara el aviso) con reloj en vivo de Buenos Aires.

## Pendientes y decisiones abiertas

- **Marca:** SECUREKO está registrada en INPI (clase 45) por un tercero, que también tiene sekureco.com.ar. Hay que consultar con un agente de marcas antes de invertir más en la identidad.
- **Contenido que falta:** número de WhatsApp, sección "Para quién", "Nosotros", preguntas frecuentes, fotos reales del banco de pruebas o instalaciones.
- **Material de capacitación:** el sitio promete una presentación para que el equipo cliente se quede; todavía no existe.
- **Mejoras propuestas y no implementadas:** copiar el mail con un toque, header compacto al scrollear, respuesta inmediata al tocar, intro corta para quien vuelve. Cuando haya más páginas: View Transitions y precarga con Speculation Rules (por header, para respetar la CSP).
- **No hacer:** fade-in al scrollear, parallax, contadores animados sin datos reales, cursor personalizado, testimonios o logos de clientes que no existan.
