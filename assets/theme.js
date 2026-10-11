// Corre antes de pintar la página:
// 1) aplica el tema guardado (evita el parpadeo claro/oscuro);
// 2) decide si mostrar la intro: solo la primera vez por sesión y nunca
//    si el visitante pidió reducir el movimiento;
// 3) si no hay intro, el header arranca ya cerrado en ">_";
// 4) marca "js": lo que solo funciona con JS (los botones "copiar") se muestra desde el primer cuadro.
// 5) audiencia (Empresa | Hogar) en data-audiencia: ?para= en la URL manda sobre lo guardado;
//    sin ninguno, Empresa. El CSS muestra solo los textos de esa audiencia.
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");
  try {
    var t = localStorage.getItem("tema");
    if (t === "dark" || t === "light") root.setAttribute("data-theme", t);
  } catch (e) {}
  var aud = null;
  try {
    var para = new URLSearchParams(location.search).get("para");
    if (para === "empresa" || para === "hogar") aud = para;
  } catch (e) {}
  if (!aud) {
    try {
      var g = localStorage.getItem("audiencia");
      if (g === "empresa" || g === "hogar") aud = g;
    } catch (e) {}
  }
  root.setAttribute("data-audiencia", aud || "empresa");
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
