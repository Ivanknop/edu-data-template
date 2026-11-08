import json
import re

import pandas as pd
import pytest

from edu_data.visor import a_lista, renderizar

PLANTILLA = """<!DOCTYPE html>
<html><body><script>const DATOS = __DATOS__;</script></body></html>
"""


def _leer_datos(html):
    return json.loads(re.search(r"const DATOS = (.*);</script>", html).group(1))


def test_renderizar(tmp_path):
    plantilla = tmp_path / "visor.html"
    plantilla.write_text(PLANTILLA, encoding="utf-8")
    datos = {"texto": "</script><b>ñ</b>", "serie": [1, None, 2.5]}
    destino = renderizar(plantilla, datos, tmp_path / "out" / "v.html", "GENERADO por x.py")
    html = destino.read_text(encoding="utf-8")
    assert html.startswith("<!DOCTYPE html>\n<!-- GENERADO por x.py -->")
    assert html.count("</script>") == 1
    assert _leer_datos(html) == datos


def test_renderizar_sin_doctype(tmp_path):
    plantilla = tmp_path / "v.html"
    plantilla.write_text("<script>__DATOS__</script>", encoding="utf-8")
    html = renderizar(plantilla, [1], tmp_path / "o.html", "m").read_text(encoding="utf-8")
    assert html.startswith("<!-- m -->\n<script>[1]")


@pytest.mark.parametrize("texto", ["sin marcador", "__DATOS__ __DATOS__"])
def test_renderizar_marcador_unico(tmp_path, texto):
    plantilla = tmp_path / "v.html"
    plantilla.write_text(texto, encoding="utf-8")
    with pytest.raises(ValueError, match="marcador"):
        renderizar(plantilla, {}, tmp_path / "o.html", "m")


def test_renderizar_rechaza_nan(tmp_path):
    plantilla = tmp_path / "v.html"
    plantilla.write_text(PLANTILLA, encoding="utf-8")
    with pytest.raises(ValueError):
        renderizar(plantilla, {"x": float("nan")}, tmp_path / "o.html", "m")


def test_a_lista():
    assert a_lista(pd.Series([1, None, 3], dtype="Int64")) == [1, None, 3]
    assert a_lista(pd.Series([1.0, 2.5, float("nan")])) == [1, 2.5, None]
    assert a_lista(pd.Series(["a", None], dtype="string")) == ["a", None]
