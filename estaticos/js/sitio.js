// Menú del teléfono e idioma recordado.
(function () {
  var CLAVE = "rdg-idioma";

  function leer() { try { return localStorage.getItem(CLAVE); } catch (e) { return null; } }
  function guardar(v) { try { localStorage.setItem(CLAVE, v); } catch (e) {} }

  // Primera visita a la versión en español con el navegador en inglés: pasar a /en/.
  var idioma = document.documentElement.lang;
  var enlaceIdioma = document.querySelector(".idioma");
  if (idioma === "es" && !leer() && enlaceIdioma) {
    var preferido = (navigator.languages && navigator.languages[0]) || navigator.language || "";
    if (/^en\b/i.test(preferido)) {
      guardar("en");
      location.replace(enlaceIdioma.getAttribute("href") + location.hash);
      return;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (enlaceIdioma) {
      enlaceIdioma.addEventListener("click", function () { guardar(enlaceIdioma.dataset.idioma); });
    }

    var boton = document.querySelector(".menu-boton");
    var menu = document.getElementById("menu");
    if (!boton || !menu) return;
    var texto = boton.querySelector(".menu-boton__texto");

    function poner(abierto) {
      boton.setAttribute("aria-expanded", String(abierto));
      menu.classList.toggle("abierto", abierto);
      texto.textContent = abierto ? boton.dataset.cerrar : boton.dataset.abrir;
    }
    boton.addEventListener("click", function () { poner(boton.getAttribute("aria-expanded") !== "true"); });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) poner(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") poner(false); });
  });
})();
