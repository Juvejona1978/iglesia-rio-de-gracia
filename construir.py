#!/usr/bin/env python3
"""Genera el sitio estático en publico/ a partir de plantillas/ y contenido/<idioma>.json.

Uso: python3 construir.py

- Español en la raíz (/), inglés en /en/.
- En las plantillas, {{ clave.anidada }} se reemplaza por el texto del JSON del idioma.
- {{ @ruta }} da la ruta relativa a la raíz del sitio ("" en ES, "../" en EN).
- {{ @idioma }}, {{ @otro_idioma }}, {{ @url_otro_idioma }} y {{ @url_canonica }} ayudan al selector y al SEO.
"""
import json
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PLANTILLAS = RAIZ / "plantillas"
CONTENIDO = RAIZ / "contenido"
ESTATICOS = RAIZ / "estaticos"
SALIDA = RAIZ / "publico"

DOMINIO = "https://riodegraciacr.org"
IDIOMAS = {"es": "", "en": "en/"}  # idioma -> carpeta de salida
PAGINAS = ["index.html", "asociacion.html"]

MARCA = re.compile(r"\{\{\s*([@\w.\-]+)\s*\}\}")
INCLUIR = re.compile(r"<!--\s*incluir\s+([\w.\-]+)\s*-->")


def leer_plantilla(nombre):
    """Lee una plantilla y reemplaza <!-- incluir parcial.html --> por plantillas/parciales/parcial.html."""
    html = (PLANTILLAS / nombre).read_text("utf-8")
    return INCLUIR.sub(lambda m: (PLANTILLAS / "parciales" / m.group(1)).read_text("utf-8"), html)


def aplanar(datos, prefijo=""):
    plano = {}
    for clave, valor in datos.items():
        nombre = f"{prefijo}{clave}"
        if isinstance(valor, dict):
            plano.update(aplanar(valor, nombre + "."))
        else:
            plano[nombre] = valor
    return plano


def construir():
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    shutil.copytree(ESTATICOS, SALIDA)

    textos = {i: aplanar(json.loads((CONTENIDO / f"{i}.json").read_text("utf-8"))) for i in IDIOMAS}
    faltan = set(textos["es"]) ^ set(textos["en"])
    if faltan:
        raise SystemExit(f"Claves que no están en ambos idiomas: {sorted(faltan)}")

    for idioma, carpeta in IDIOMAS.items():
        otro = "en" if idioma == "es" else "es"
        for pagina in PAGINAS:
            nombre_url = "" if pagina == "index.html" else pagina
            extras = {
                "@ruta": "../" if carpeta else "",
                "@idioma": idioma,
                "@otro_idioma": otro,
                "@url_canonica": f"{DOMINIO}/{carpeta}{nombre_url}",
                "@url_es": f"{DOMINIO}/{nombre_url}",
                "@url_en": f"{DOMINIO}/en/{nombre_url}",
                "@url_otro_idioma": ("../" if carpeta else "en/") + (nombre_url or ""),
            }

            def reemplazar(m):
                clave = m.group(1)
                if clave in extras:
                    return extras[clave]
                if clave not in textos[idioma]:
                    raise SystemExit(f"{pagina}: falta la clave '{clave}' en {idioma}.json")
                return textos[idioma][clave]

            html = MARCA.sub(reemplazar, leer_plantilla(pagina))
            destino = SALIDA / carpeta / pagina
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(html, "utf-8")

    urls = [f"{DOMINIO}/{c}{'' if p == 'index.html' else p}" for c in IDIOMAS.values() for p in PAGINAS]
    (SALIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n",
        "utf-8",
    )
    print(f"Sitio generado en {SALIDA} ({len(urls)} páginas)")


if __name__ == "__main__":
    construir()
