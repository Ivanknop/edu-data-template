"""Links de descarga de la página de datos abiertos de la Secretaría de Educación.

La página arma su tabla con una planilla de Google (leíble como CSV); cada fila apunta a un link
público de SharePoint del Ministerio. SharePoint pide una cookie de sesión: se visita el link y
después se pide el archivo con `download=1`. Planilla y forma de los links vigentes al
2026-11-08: si la página cambia, revisar `ID_PLANILLA` y las columnas.
"""

import csv
import http.cookiejar
import io
import re
import urllib.request
from pathlib import Path

from edu_data.descarga import abrir, descargar

PAGINA = (
    "https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/"
    "datos-abiertos-de-la-secretaria-de-educacion"
)
ID_PLANILLA = "1XaSz7AJ-EkpLqj_qjx3TPdBfJaQvqEZwg3sOYagtOsI"
URL_PLANILLA = (
    f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/gviz/tq?tqx=out:csv&sheet=Hoja%201"
)
# Columnas de la planilla: año, nombre del archivo, descripción, link
COL_NOMBRE, COL_LINK = 1, 3


def leer_planilla() -> str:
    """Texto CSV de la planilla que alimenta la página."""
    return abrir(URL_PLANILLA).decode("utf-8")


def links(texto_planilla: str, patron: str | re.Pattern) -> dict[str, str]:
    """{nombre de archivo: link} de las filas cuyo nombre cumple `patron`.

    Los documentos agrupados en la fila de encabezado (diccionarios, notas metodológicas) no
    salen acá: sus links se copian de la página y se fijan en el script de descarga.
    """
    patron = re.compile(patron)
    filas = list(csv.reader(io.StringIO(texto_planilla)))[1:]
    return {
        f[COL_NOMBRE].strip(): f[COL_LINK].strip()
        for f in filas
        if len(f) > COL_LINK and patron.search(f[COL_NOMBRE].strip())
    }


def _obtener_sharepoint(url: str) -> bytes:
    # Una cookie nueva por intento: la de un intento fallido puede quedar inválida
    abridor = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )
    abrir(url, abridor)
    return abrir(url + ("&" if "?" in url else "?") + "download=1", abridor)


def descargar_sharepoint(url: str, destino: str | Path, reintentos: int = 3) -> bool:
    """Baja un link público de SharePoint a `destino` si no existe (nunca pisa)."""
    return descargar(
        url, destino, reintentos=reintentos, obtener=_obtener_sharepoint, rechazar_html=True
    )
