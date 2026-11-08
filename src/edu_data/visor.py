"""Visores HTML autocontenidos: plantilla de diseño + datos precalculados en JSON + marca."""

import json
from pathlib import Path

import pandas as pd


def a_lista(serie: pd.Series) -> list:
    """Valores para JSON: NA → None (punto vacío en el gráfico, no 0); enteros sin ".0"."""
    salida = []
    for valor in serie.tolist():
        if pd.isna(valor):
            salida.append(None)
        elif isinstance(valor, float) and valor.is_integer():
            salida.append(int(valor))
        else:
            salida.append(valor.item() if hasattr(valor, "item") else valor)
    return salida


def _json_para_script(datos) -> str:
    # allow_nan=False: un NaN suelto rompe el JSON en el navegador; los NA se pasan como None
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    # "</" cerraría el <script> antes de tiempo; U+2028/2029 son saltos de línea en JS viejo
    return texto.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def renderizar(
    plantilla: str | Path,
    datos,
    destino: str | Path,
    marca: str,
    marcador: str = "__DATOS__",
) -> Path:
    """Reemplaza `marcador` de la plantilla por el JSON de `datos` y agrega la marca GENERADO.

    El marcador debe aparecer una sola vez (p. ej. `<script>const DATOS = __DATOS__;</script>`).
    La marca va como comentario después del `<!doctype>`, para no sacar al navegador del modo
    estándar.
    """
    html = Path(plantilla).read_text(encoding="utf-8")
    apariciones = html.count(marcador)
    if apariciones != 1:
        raise ValueError(f"El marcador {marcador!r} aparece {apariciones} veces (se espera 1)")
    if "--" in marca:
        raise ValueError("La marca no puede contener '--' (cerraría el comentario HTML)")
    html = html.replace(marcador, _json_para_script(datos))
    comentario = f"<!-- {marca} -->"
    inicio = html.lower().find("<!doctype")
    if inicio == -1:
        html = f"{comentario}\n{html}"
    else:
        fin = html.index(">", inicio) + 1
        html = f"{html[:fin]}\n{comentario}{html[fin:]}"
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    return destino
