import re

import pandas as pd
import pytest

from edu_data.io import leer_csv_oficial
from edu_data.series import ancho_a_largo, archivos_por_periodo, leer_en_paralelo


def _crear(directorio, nombres):
    for nombre in nombres:
        (directorio / nombre).write_text("x")


def test_archivos_por_periodo_con_desfase(tmp_path):
    _crear(tmp_path, ["2021 base.csv", "2020 base.csv", "otro.csv", "2020 base.xlsx"])
    patron = re.compile(r"^(\d{4}) base\.csv$")
    assert list(archivos_por_periodo(tmp_path, patron)) == [2020, 2021]
    con_desfase = archivos_por_periodo(tmp_path, patron, desfase=1)
    assert {p: r.name for p, r in con_desfase.items()} == {
        2019: "2020 base.csv",
        2020: "2021 base.csv",
    }


def test_archivos_por_periodo_repetido(tmp_path):
    _crear(tmp_path, ["2020_a.csv", "2020_b.csv"])
    with pytest.raises(ValueError, match="repetido"):
        archivos_por_periodo(tmp_path, r"^(\d{4})_")


def test_leer_en_paralelo_conserva_el_orden(tmp_path, csv_oficial):
    rutas = []
    for i in range(3):
        ruta = tmp_path / f"copia_{i}.csv"
        texto = csv_oficial.read_bytes().replace(b"100", str(100 + i).encode())
        ruta.write_bytes(texto)
        rutas.append(ruta)
    paralelo = leer_en_paralelo(rutas, leer_csv_oficial, procesos=2)
    assert [df.loc[0, "matricula"] for df in paralelo] == [100, 101, 102]
    serie = leer_en_paralelo(rutas, leer_csv_oficial, procesos=1)
    for a, b in zip(paralelo, serie, strict=True):
        pd.testing.assert_frame_equal(a, b)


def test_ancho_a_largo():
    ancho = pd.DataFrame(
        {
            "unidad": pd.array(["02", "06"], dtype="string"),
            "_1": pd.array([10, 20], dtype="Int64"),
            "_2": pd.array([5, None], dtype="Int64"),
            "m_1": pd.array([4, 9], dtype="Int64"),
        }
    )
    largo = ancho_a_largo(
        ancho, ["unidad"], {"total": "_{}", "mujeres": "m_{}"}, ["1", "2"], col_sufijo="grado"
    )
    assert largo.columns.tolist() == ["unidad", "grado", "total", "mujeres"]
    assert largo["unidad"].dtype == "string"
    assert largo["total"].tolist()[:3] == [10, 20, 5]
    assert pd.isna(largo.loc[3, "total"])
    # m_2 no existe: NA, no 0
    assert largo.loc[largo["grado"] == "2", "mujeres"].isna().all()
    assert largo.loc[largo["grado"] == "1", "mujeres"].tolist() == [4, 9]
