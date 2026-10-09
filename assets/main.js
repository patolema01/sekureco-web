// sekureco — reloj del visor de cámara y selector de tema.
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

(function () {
  "use strict";
  var el = document.getElementById("feed-clock");
  if (!el) return;

  var fmt;
  try {
    fmt = new Intl.DateTimeFormat("es-AR", {
      timeZone: "America/Argentina/Buenos_Aires",
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
      hour12: false
    });
  } catch (e) {
    return;
  }

  function tick() {
    el.textContent = fmt.format(new Date()).replace(",", "");
  }
  tick();
  setInterval(tick, 1000);
})();

// Intro: el escudo sigue bajo fuego hasta que la página terminó de cargar
// (y como mínimo hasta el 3er balazo, ~2,2 s). Al terminar, SEKURECO y el escudo se achican
// y viajan cada uno a su lugar en el header (transición FLIP con Web Animations,
// permitida por la CSP) mientras el fondo se desvanece. Se salta con un toque o una tecla.
(function () {
  "use strict";
  var ov = document.getElementById("intro");
  var root = document.documentElement;
  if (!ov || !root.classList.contains("intro")) return;
  var MIN = 2200, FLY = 950, done = false, loaded = document.readyState === "complete";
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

  function check() {
    if (!loaded) return;
    var left = MIN - performance.now();
    if (left <= 0) end(); else setTimeout(check, left);
  }
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
