// Corre antes de pintar la página:
// 1) aplica el tema guardado (evita el parpadeo claro/oscuro);
// 2) decide si mostrar la intro: solo la primera vez por sesión y nunca
//    si el visitante pidió reducir el movimiento;
// 3) si no hay intro, el header arranca ya cerrado en ">_".
(function () {
  "use strict";
  var root = document.documentElement;
  try {
    var t = localStorage.getItem("tema");
    if (t === "dark" || t === "light") root.setAttribute("data-theme", t);
  } catch (e) {}
  try {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduce && !sessionStorage.getItem("intro")) {
      root.classList.add("intro");          // el header se cierra cuando termina la intro
      sessionStorage.setItem("intro", "1");
    } else {
      root.classList.add("hdr-done");       // ya se vio: ">_" fijo desde el primer cuadro
    }
  } catch (e) {
    root.classList.add("hdr-done");
  }
})();
