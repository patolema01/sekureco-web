// sekureco — selector de tema, intro, menú ">≡" con sus árboles, header que se esconde al bajar y "copiar".
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
  if (!root.classList.contains("intro")) return;
  // páginas sin intro (404): theme.js no lo sabe y marca "intro" en la primera visita; sin esto el
  // logo del header quedaba oculto. Va directo al estado final.
  if (!ov) {
    root.classList.remove("intro");
    root.classList.add("hdr-done");
    return;
  }
  var MIN = 3000, CEASE = 2200, FLY = 950, done = false, loaded = document.readyState === "complete";
  var EASE = "cubic-bezier(.65, 0, .25, 1)";
  // bloquea el scroll mientras dura la intro; lo pone este script, así sin JS no hay bloqueo
  root.classList.add("intro-lock");

  function headerSequence() {
    root.classList.remove("intro-lock");
    root.classList.remove("intro");
    root.classList.add("hdr-play");
    // cierre "ventana" + el "≡" que se arma con el parpadeo del cursor: la duración la calcula
    // tools/header.py y la deja en --hdr-total; al terminar queda el estado final (">≡" fijo)
    var total = parseFloat(getComputedStyle(root).getPropertyValue("--hdr-total")) || 2600;
    setTimeout(function () {
      root.classList.remove("hdr-play");
      root.classList.add("hdr-done");
    }, total);
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

// Header y menú, juntos porque se condicionan: con el menú abierto o el mouse encima, el header no se esconde.
//
// Header: sticky, se esconde al bajar y vuelve al subir; con scroll > 0 "flota" (sombra). Con mouse,
// si está oculto, dejar el puntero 120 ms en la franja de arriba (.top-peek) lo trae de vuelta; se
// queda mientras el puntero esté encima (o sobre el menú) y, al salir, a los 600 ms se vuelve a
// esconder si la página sigue scrolleada. Un solo estado (hidden) y un solo lugar que lo cambia.
// No se esconde durante la intro, con el menú abierto ni con el foco de teclado adentro.
//
// Menú: ">≡" abre el índice (5 ítems, ningún árbol abierto). Con mouse se abre al dejar el puntero
// 120 ms y se cierra 300 ms después de salir de botón + menú; un click lo deja fijado. Cada ítem abre
// su árbol (uno solo a la vez): con mouse y lugar, a la derecha en su propia capa (hover 150 ms o
// click); si no, debajo, como acordeón. Se cierra todo con Esc, tocando afuera o eligiendo un destino.
(function () {
  "use strict";
  var top = document.querySelector(".top");
  if (!top || !window.requestAnimationFrame) return;
  var root = document.documentElement;
  var btn = document.getElementById("menu-btn");
  var menu = document.getElementById("menu");
  var mqHover = window.matchMedia ? window.matchMedia("(hover: hover) and (pointer: fine)") : null;
  var DELTA = 8, MIN_Y = 120;
  var T_PEEK = 120, T_SALIR = 600, T_ABRIR = 120, T_CERRAR = 300, T_ARBOL = 150, T_ARBOL_CERRAR = 300;

  function conMouse(e) { return !!(mqHover && mqHover.matches) && e.pointerType === "mouse"; }
  function menuAbierto() { return !!menu && !menu.hasAttribute("hidden"); }
  function focoTeclado() {
    var a = document.activeElement;
    if (!a || !top.contains(a)) return false;
    try { return a.matches(":focus-visible"); } catch (e) { return true; }
  }

  // ---------- visibilidad del header ----------
  var hidden = false, porPeek = false, sobreTop = false, salirT = 0, peekT = 0;
  function setHidden(v) {
    if (v === hidden) return;
    hidden = v;
    if (!v) porPeek = false;
    top.classList.toggle("top-hidden", v);
  }
  function fijo() {
    return root.classList.contains("intro") || menuAbierto() || sobreTop || focoTeclado();
  }

  var last = window.scrollY, ticking = false;
  function update() {
    ticking = false;
    var y = Math.max(0, window.scrollY);
    top.classList.toggle("top-float", y > 0);
    if (y <= MIN_Y) { setHidden(false); last = y; return; }
    var dy = y - last;
    if (Math.abs(dy) <= DELTA) return;          // los movimientos chicos se acumulan
    if (dy > 0 && !fijo()) setHidden(true);
    else if (dy < 0) setHidden(false);
    last = y;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  // si el foco entra al header (Tab o Shift+Tab desde el contenido), que se vea
  top.addEventListener("focusin", function () { setHidden(false); });

  // franja de 21 px: solo existe (CSS) con el header oculto y en dispositivos con mouse
  var peek = document.createElement("div");
  peek.className = "top-peek";
  peek.setAttribute("aria-hidden", "true");
  top.parentNode.insertBefore(peek, top.nextSibling);
  peek.addEventListener("pointerenter", function (e) {
    if (!conMouse(e)) return;
    clearTimeout(peekT);
    peekT = setTimeout(function () {
      setHidden(false);
      porPeek = true;
      sobreTop = true;                          // el puntero queda encima del header que bajó
    }, T_PEEK);
  });
  // si sale antes (o se va de la ventana por arriba, rumbo a las pestañas), no aparece
  peek.addEventListener("pointerleave", function () { clearTimeout(peekT); });

  // dónde está el mouse: sobre el header (el menú y sus árboles están adentro) o afuera
  function puntero(dentro) {
    if (dentro === sobreTop) return;
    sobreTop = dentro;
    clearTimeout(salirT);
    if (!dentro && porPeek) {
      salirT = setTimeout(function () {
        if (porPeek && !sobreTop && window.scrollY > MIN_Y && !fijo()) setHidden(true);
      }, T_SALIR);
    }
  }
  document.addEventListener("pointermove", function (e) {
    if (e.pointerType === "mouse") puntero(top.contains(e.target));
  }, { passive: true });
  // el header que baja (o sube) bajo un puntero quieto no dispara pointermove, sí mouseover
  document.addEventListener("mouseover", function (e) {
    if (mqHover && mqHover.matches) puntero(top.contains(e.target));
  }, { passive: true });
  document.addEventListener("mouseout", function (e) {
    if (!e.relatedTarget) { clearTimeout(peekT); puntero(false); }   // salió de la ventana
  });

  update();
  if (!btn || !menu) return;

  // ---------- menú ----------
  var items = Array.prototype.slice.call(menu.querySelectorAll(".mi"));
  var fijado = false, abrirT = 0, cerrarT = 0;
  var arbol = null, arbolFijo = false, pendiente = null, arbolT = 0, arbolCerrarT = 0;

  function boton(li) { return li.querySelector(".mi-btn"); }
  function rama(li) { return li.querySelector(".mt"); }
  function enfocables(ul) { return Array.prototype.slice.call(ul.querySelectorAll("a, button")); }
  function aLado() { return menu.classList.contains("menu-side"); }

  // a la derecha solo con mouse y si todos los árboles entran en la ventana; si no, debajo
  function decidirLado() {
    menu.classList.remove("menu-side");
    if (!mqHover || !mqHover.matches) return;
    menu.classList.add("menu-side");
    var limite = document.documentElement.clientWidth - 8;
    for (var i = 0; i < items.length; i++) {
      if (rama(items[i]).getBoundingClientRect().right > limite) { menu.classList.remove("menu-side"); return; }
    }
  }

  // en el acordeón, si el árbol queda fuera de la vista, el menú scrollea lo justo para mostrarlo
  function mostrar(li) {
    var m = menu.getBoundingClientRect(), r = li.getBoundingClientRect(), pad = 9;
    var falta = r.bottom - (m.bottom - pad);
    if (falta > 0) menu.scrollTop += Math.min(falta, r.top - (m.top + pad));
  }

  function setArbol(li, fijar) {
    clearTimeout(arbolT); clearTimeout(arbolCerrarT);
    pendiente = null;
    if (li === arbol) { if (li && fijar) arbolFijo = true; return; }
    // el anterior se cierra en el mismo frame en que se abre el nuevo: nunca dos a la vez
    if (arbol) { rama(arbol).setAttribute("hidden", ""); boton(arbol).setAttribute("aria-expanded", "false"); }
    arbol = li;
    arbolFijo = !!fijar;
    if (li) {
      rama(li).removeAttribute("hidden");
      boton(li).setAttribute("aria-expanded", "true");
      if (!aLado()) mostrar(li);
    }
  }

  function setOpen(open, fijar) {
    clearTimeout(abrirT); clearTimeout(cerrarT);
    // si se abre mientras el header todavía se está cerrando o armando el "≡", se completa
    // de una: así el ">" gira y las barras se funden como siempre
    if (open && root.classList.contains("hdr-play")) {
      root.classList.remove("hdr-play");
      root.classList.add("hdr-done");
    }
    if (open === menuAbierto()) { if (open && fijar) fijado = true; return; }
    setArbol(null);
    fijado = open && !!fijar;
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      menu.removeAttribute("hidden");
      menu.scrollTop = 0;
      decidirLado();
      setHidden(false);
    } else {
      menu.setAttribute("hidden", "");
    }
  }
  function programarCierre() {
    clearTimeout(cerrarT);
    if (menuAbierto() && !fijado) cerrarT = setTimeout(function () { if (!fijado) setOpen(false); }, T_CERRAR);
  }

  // ">≡": hover 120 ms abre; click abre fijado (o fija el que abrió el hover); con fijado, cierra
  // el botón mide lo que la palabra entera (recortada por la ventana): para el hover cuenta solo lo
  // que se ve, el ">≡", con 8 px de margen
  var gt = btn.querySelector(".k-arms"), barra = btn.querySelector(".bar1"), sobreBtn = false;
  function enGlifo(e) {
    if (!gt || !barra) return true;
    var a = gt.getBoundingClientRect(), z = barra.getBoundingClientRect(), m = 8;
    return e.clientX >= a.left - m && e.clientX <= Math.max(a.right, z.right) + m &&
      e.clientY >= a.top - m && e.clientY <= Math.max(a.bottom, z.bottom) + m;
  }
  function hoverBtn(dentro) {
    if (dentro === sobreBtn) return;
    sobreBtn = dentro;
    clearTimeout(abrirT);
    if (dentro) {
      clearTimeout(cerrarT);
      if (!menuAbierto()) abrirT = setTimeout(function () { setOpen(true, false); }, T_ABRIR);
    } else {
      programarCierre();
    }
  }
  btn.addEventListener("pointermove", function (e) { if (conMouse(e)) hoverBtn(enGlifo(e)); });
  btn.addEventListener("pointerleave", function (e) { if (conMouse(e)) hoverBtn(false); });
  menu.addEventListener("pointerenter", function (e) { if (conMouse(e)) clearTimeout(cerrarT); });
  menu.addEventListener("pointerleave", function (e) { if (conMouse(e)) programarCierre(); });

  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    var teclado = e.detail === 0;
    if (!menuAbierto()) {
      setOpen(true, true);
      if (teclado) boton(items[0]).focus();
    } else if (!fijado && !teclado) {
      fijado = true;
      clearTimeout(cerrarT);
    } else {
      setOpen(false);
    }
  });

  items.forEach(function (li) {
    var b = boton(li);
    b.addEventListener("click", function (e) {
      if (e.detail === 0) {                     // Enter o espacio: abre y entra
        setArbol(li, true);
        enfocables(rama(li))[0].focus();
      } else if (li === arbol && !arbolFijo) {  // lo abrió el hover: el click lo fija
        arbolFijo = true;
      } else {
        setArbol(li === arbol ? null : li, true);
      }
    });
    // hover (solo con el árbol a la derecha: en el acordeón la lista se movería bajo el puntero)
    li.addEventListener("pointerenter", function (e) {
      if (!conMouse(e) || !aLado()) return;
      if (li === arbol) { clearTimeout(arbolCerrarT); return; }
      clearTimeout(arbolT);
      pendiente = li;
      arbolT = setTimeout(function () { if (pendiente === li) setArbol(li, false); }, T_ARBOL);
    });
    li.addEventListener("pointerleave", function (e) {
      if (!conMouse(e)) return;
      // cruzar otro ítem por menos de 150 ms (en diagonal, rumbo al árbol) no cambia nada
      if (pendiente === li) { clearTimeout(arbolT); pendiente = null; }
      if (li === arbol && !arbolFijo) {
        clearTimeout(arbolCerrarT);
        arbolCerrarT = setTimeout(function () { if (li === arbol && !arbolFijo) setArbol(null); }, T_ARBOL_CERRAR);
      }
    });
  });

  // elegir un destino cierra todo
  menu.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });
  document.addEventListener("click", function (e) {
    if (menuAbierto() && !menu.contains(e.target)) setOpen(false);
  });

  // teclado: ↑↓ recorren la lista donde está el foco; → entra al árbol; ← vuelve al ítem; Esc cierra todo
  menu.addEventListener("keydown", function (e) {
    var li = e.target.closest(".mi");
    if (!li) return;
    var enArbol = !!e.target.closest(".mt");
    var lista, i;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      lista = enArbol ? enfocables(rama(li)) : items.map(boton);
      i = lista.indexOf(e.target);
      i = (i + (e.key === "ArrowDown" ? 1 : lista.length - 1)) % lista.length;
      lista[i].focus();
      e.preventDefault();
    } else if (e.key === "ArrowRight" && !enArbol) {
      setArbol(li, true);
      enfocables(rama(li))[0].focus();
      e.preventDefault();
    } else if (e.key === "ArrowLeft" && enArbol) {
      boton(li).focus();
      setArbol(null);
      e.preventDefault();
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && menuAbierto()) { setOpen(false); btn.focus(); }
  });

  // si cambia el ancho (o se conecta un mouse) con el menú abierto, se recalcula dónde van los árboles
  window.addEventListener("resize", function () {
    if (!menuAbierto()) return;
    var antes = aLado();
    decidirLado();
    if (aLado() !== antes) setArbol(null);
  });
})();

// "copiar" al lado de cada mail (menú y Contacto): copia la dirección y muestra "copiado" 1,5 s.
// Sin portapapeles no se muestra; si falla, queda como estaba.
(function () {
  "use strict";
  var botones = document.querySelectorAll(".copy[data-copy]");
  var ok = !!(navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext);
  Array.prototype.forEach.call(botones, function (b) {
    if (!ok) { b.classList.add("copy-off"); return; }
    var texto = b.firstChild, t = 0;
    b.addEventListener("click", function () {
      navigator.clipboard.writeText(b.getAttribute("data-copy")).then(function () {
        texto.nodeValue = "copiado";
        b.classList.add("copied");
        clearTimeout(t);
        t = setTimeout(function () { texto.nodeValue = "copiar"; b.classList.remove("copied"); }, 1500);
      }, function () {});
    });
  });
})();
