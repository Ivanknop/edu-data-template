import os

import pandas as pd
import pytest

# CSV como los oficiales: cp1252, ";", CRLF, vacíos como " " y códigos con ceros a la izquierda
CSV_OFICIAL = (
    "Cod_Unidad;Nombre;CUE;Matricula;Mujeres;Tasa\r\n"
    "02;Región Ñandú ;123;100;50;1.5\r\n"
    "14;Córdoba; 456; ;30;2.0\r\n"
    "06; Otra;789; 0;0;\r\n"
)


@pytest.fixture
def csv_oficial(tmp_path):
    ruta = tmp_path / "base_2020.csv"
    ruta.write_bytes(CSV_OFICIAL.encode("cp1252"))
    return ruta


@pytest.fixture
def serie():
    """Serie sintética: la unidad B tiene un salto y un valor atípico en 2022."""
    filas = []
    for unidad, valores in {"A": [100, 102, 101, 103, 104], "B": [100, 101, 160, 102, 100]}.items():
        for periodo, valor in zip(range(2019, 2024), valores, strict=True):
            filas.append({"unidad": unidad, "periodo": periodo, "valor": valor})
    return pd.DataFrame(filas)


@pytest.fixture(scope="session")
def requiere_crudos():
    """Para fixtures de datos reales: `requiere_crudos(condicion, motivo)`.

    Si no se cumple la condición (faltan crudos en data/raw/): skip en local, fail en la CI
    (variable `CI` definida), donde los crudos deberían estar.
    """

    def verificar(condicion: bool, motivo: str) -> None:
        if condicion:
            return
        if os.environ.get("CI"):
            pytest.fail(motivo)
        pytest.skip(motivo)

    return verificar
