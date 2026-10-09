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
// (y como mínimo 5 s: un loop completo).
// Se puede saltar con un toque o cualquier tecla.
(function () {
  "use strict";
  var ov = document.getElementById("intro");
  var root = document.documentElement;
  if (!ov || !root.classList.contains("intro")) return;
  var MIN = 5000, done = false, loaded = document.readyState === "complete";
  function end() {
    if (done) return;
    done = true;
    ov.classList.add("out");
    setTimeout(function () {
      root.classList.remove("intro");
      // el header hace su cierre de puertas y queda en ">_"
      root.classList.add("hdr-play");
      setTimeout(function () {
        root.classList.remove("hdr-play");
        root.classList.add("hdr-done");
      }, 2800);
    }, 700);
    document.removeEventListener("keydown", end);
  }
  function check() {
    if (!loaded) return;
    var left = MIN - performance.now();
    if (left <= 0) end(); else setTimeout(check, left);
  }
  window.addEventListener("load", function () { loaded = true; check(); });
  ov.addEventListener("click", end);
  document.addEventListener("keydown", end);
  check();
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
