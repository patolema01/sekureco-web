// sekureco — selector de tema, intro, menú ">_" y header que se esconde al bajar.
// No usa cookies, no hace pedidos de red y no carga nada de terceros.
// Lo único que guarda es la preferencia de tema, en el navegador del visitante.
(function () {
  "use strict";
  var btn = document.getElementById("theme-btn");
  if (!btn) return;
  var root = document.documentElement;
  var mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function current() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return mq && mq.matches ? "dark" : "light";
  }
  function sync() {
    var dark = current() === "dark";
    btn.setAttribute("aria-pressed", dark ? "true" : "false");
    btn.setAttribute("aria-label", dark ? "Usar modo claro" : "Usar modo oscuro");
  }
  btn.addEventListener("click", function () {
    var next = current() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("tema", next); } catch (e) {}
    sync();
  });
  if (mq && mq.addEventListener) mq.addEventListener("change", sync);
  sync();
})();

// Intro: el escudo sigue bajo fuego hasta que la página terminó de cargar (y como
// mínimo 3 balazos: el vuelo sale 3,0 s después de que arranca la animación, con el
// espiral del último impacto ya apagado). Si a los 2,2 s ya cargó, se corta el fuego
// ("cease") para que no se vea nada del 4º disparo. Los tiempos se cuentan desde el
// arranque real de las animaciones, no desde la navegación: en un celular el primer
// render puede llegar 1 s o más tarde. Al terminar, SEKURECO y el escudo se achican y
// viajan cada uno a su lugar en el header (transición FLIP con Web Animations,
// permitida por la CSP) mientras el fondo se desvanece. Se salta con un toque o una tecla.
(function () {
  "use strict";
  var ov = document.getElementById("intro");
  var root = document.documentElement;
  if (!ov || !root.classList.contains("intro")) return;
  var MIN = 3000, CEASE = 2200, FLY = 950, done = false, loaded = document.readyState === "complete";
  var EASE = "cubic-bezier(.65, 0, .25, 1)";
  // bloquea el scroll mientras dura la intro; lo pone este script, así sin JS no hay bloqueo
  root.classList.add("intro-lock");

  function headerSequence() {
    root.classList.remove("intro-lock");
    root.classList.remove("intro");
    root.classList.add("hdr-play");
    setTimeout(function () {
      root.classList.remove("hdr-play");
      root.classList.add("hdr-done");
    }, 2800);
  }

  // traslación + escala que lleva el rectángulo "a" al "b", con origen arriba a la izquierda del elemento
  function flip(el, a, b) {
    var r = el.getBoundingClientRect();
    var k = b.height / a.height;
    var tx = b.left - (r.left + (a.left - r.left) * k);
    var ty = b.top - (r.top + (a.top - r.top) * k);
    return el.animate(
      [{ transform: "none" }, { transform: "translate(" + tx + "px," + ty + "px) scale(" + k + ")" }],
      { duration: FLY, easing: EASE, fill: "forwards" }
    );
  }

  function end() {
    if (done) return;
    done = true;
    var wmI = ov.querySelector(".intro-wm-svg");
    var svgI = ov.querySelector(".intro-svg");
    var shI = ov.querySelector(".sh-in > g");
    var wmH = document.querySelector(".top .logo-wm");
    var shH = document.querySelector(".top .logo-shield > g");
    var bg = ov.querySelector(".intro-bg");

    if (!wmI || !svgI || !shI || !wmH || !shH || !bg || !svgI.animate) {
      root.classList.remove("intro-lock");
      ov.classList.add("out");
      setTimeout(headerSequence, 700);
      return;
    }

    ov.classList.add("leaving");
    void ov.offsetWidth;                       // aplica "leaving" antes de medir (frena el latido)

    flip(wmI, wmI.getBoundingClientRect(), wmH.getBoundingClientRect());
    flip(svgI, shI.getBoundingClientRect(), shH.getBoundingClientRect());
    bg.animate([{ opacity: 1 }, { opacity: 0 }],
      { duration: FLY * .8, delay: FLY * .2, easing: "ease-in-out", fill: "forwards" });

    // al aterrizar, las piezas de la intro coinciden con las del header: el cambio no se nota
    setTimeout(headerSequence, FLY + 30);
  }

  // t0: arranque real de las animaciones de la intro, en ms de document.timeline (el
  // mismo reloj que performance.now()). Respaldo: el momento en que corre este script.
  var T_JS = performance.now(), t0 = null;

  function check() {
    if (!loaded || t0 === null) return;
    var left = t0 + MIN - performance.now();
    if (left <= 0) end(); else setTimeout(check, left);
  }

  function anclar(t) {
    if (t0 !== null) return;
    t0 = t;
    // el 4º impacto caería a los 2,70 s: si ya cargó, a los 2,2 s se corta el fuego;
    // si no, sigue hasta que cargue
    setTimeout(function () {
      if (loaded && !done) ov.classList.add("cease");
    }, Math.max(0, t0 + CEASE - performance.now()));
    check();
  }

  // startTime existe recién cuando la animación arrancó de verdad (primer render): "ready"
  var b0 = ov.querySelector(".b0");
  var anim = b0 && b0.getAnimations && b0.getAnimations()[0];
  if (anim && anim.ready) {
    anim.ready.then(function (a) { anclar(a.startTime !== null ? a.startTime : T_JS); },
                    function () { anclar(T_JS); });
  } else {
    anclar(T_JS);
  }
  // si la animación nunca arranca (p. ej. pestaña en segundo plano), que la página no
  // quede bloqueada: a los 8 s, como la red de seguridad del CSS, se ancla al respaldo
  setTimeout(function () { anclar(T_JS); }, 8000);

  window.addEventListener("load", function () { loaded = true; check(); });
  ov.addEventListener("click", end);
  document.addEventListener("keydown", function onKey(e) {
    // que la tecla solo salte la intro: sin esto, la barra espaciadora además scrollea la página
    if (!done) e.preventDefault();
    document.removeEventListener("keydown", onKey);
    end();
  });
  check();
})();

// Indicador de carga reutilizable: el escudo bajo fuego (sin SEKURECO).
// Uso: var quitar = SK.cargando(contenedor);  ...  quitar();
// Clona el escudo de la intro, así comparte las mismas animaciones de styles.css.
window.SK = window.SK || {};
window.SK.cargando = (function () {
  "use strict";
  var n = 0;

  // la máscara y el clipPath del escudo tienen id: en el clon se renombran con un sufijo
  // por instancia (y sus url(#...)), así no se duplican ni apuntan a la intro ya oculta
  function renombrarIds(svg, suf) {
    var conId = svg.querySelectorAll("[id]"), nuevos = {}, i, j;
    for (i = 0; i < conId.length; i++) {
      nuevos[conId[i].id] = conId[i].id + suf;
      conId[i].id += suf;
    }
    var todos = svg.querySelectorAll("*");
    for (i = 0; i < todos.length; i++) {
      for (j = 0; j < todos[i].attributes.length; j++) {
        var at = todos[i].attributes[j];
        var v = at.value.replace(/url\(#([^)]+)\)/g, function (m, id) {
          return nuevos[id] ? "url(#" + nuevos[id] + ")" : m;
        });
        if (v.charAt(0) === "#" && nuevos[v.slice(1)]) v = "#" + nuevos[v.slice(1)];
        if (v !== at.value) at.value = v;
      }
    }
  }

  return function (contenedor) {
    var fuente = document.querySelector("#intro .intro-svg");
    var caja = document.createElement("span");
    caja.className = "sk-loader";
    caja.setAttribute("role", "status");
    caja.setAttribute("aria-label", "Cargando");
    if (fuente) {
      var copia = fuente.cloneNode(true);
      renombrarIds(copia, "-sk" + (++n));
      copia.setAttribute("class", "sk-loader-svg");
      copia.setAttribute("aria-hidden", "true");
      caja.appendChild(copia);
    } else {
      caja.textContent = "Cargando…";
    }
    contenedor.appendChild(caja);
    return function () { if (caja.parentNode) caja.parentNode.removeChild(caja); };
  };
})();

// Menú: ">_" abre y cierra. Se cierra con Esc, tocando afuera o eligiendo una sección.
(function () {
  "use strict";
  var btn = document.getElementById("menu-btn");
  var menu = document.getElementById("menu");
  if (!btn || !menu) return;
  function setOpen(open) {
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) menu.removeAttribute("hidden"); else menu.setAttribute("hidden", "");
  }
  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    var open = btn.getAttribute("aria-expanded") !== "true";
    setOpen(open);
    if (open) { var first = menu.querySelector("a"); if (first) first.focus(); }
  });
  menu.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });
  document.addEventListener("click", function (e) {
    if (!menu.hasAttribute("hidden") && !menu.contains(e.target)) setOpen(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !menu.hasAttribute("hidden")) { setOpen(false); btn.focus(); }
  });
})();

// Header: se esconde al bajar y vuelve al subir. Con scroll > 0 "flota" (sombra y cursor fijo).
// Un solo listener pasivo y el trabajo en requestAnimationFrame. No se esconde con el menú
// abierto, durante la intro ni con el foco adentro del header (teclado).
(function () {
  "use strict";
  var top = document.querySelector(".top");
  if (!top || !window.requestAnimationFrame) return;
  var root = document.documentElement;
  var btn = document.getElementById("menu-btn");
  var DELTA = 8, MIN_Y = 120;
  var last = window.scrollY, ticking = false;

  function fijo() {
    return root.classList.contains("intro") ||
      (btn && btn.getAttribute("aria-expanded") === "true") ||
      top.contains(document.activeElement);
  }

  function update() {
    ticking = false;
    var y = Math.max(0, window.scrollY);
    top.classList.toggle("top-float", y > 0);
    if (y <= MIN_Y) { top.classList.remove("top-hidden"); last = y; return; }
    var dy = y - last;
    if (Math.abs(dy) <= DELTA) return;          // los movimientos chicos se acumulan
    if (dy > 0 && !fijo()) top.classList.add("top-hidden");
    else if (dy < 0) top.classList.remove("top-hidden");
    last = y;
  }

  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  // si el foco entra al header (Shift+Tab desde el contenido), que se vea
  top.addEventListener("focusin", function () { top.classList.remove("top-hidden"); });
  update();
})();
