import pandas as pd

from edu_data.perfil import (
    buscar_shock,
    cruzar_diccionario,
    perfil_columnas,
    vacios_con_denominador,
    verificar_identidades,
)


def _base():
    return pd.DataFrame(
        {
            "total": pd.array([10, 5, 8, None], dtype="Int64"),
            "mujeres": pd.array([4, 2, 3, 1], dtype="Int64"),
            "varones": pd.array([6, 2, None, 2], dtype="Int64"),
            "cod": pd.array(["01", "02", "03", "04"], dtype="string"),
        }
    )


def test_perfil_columnas():
    df = _base()
    df.attrs["columnas_ausentes"] = ["varones"]
    perfil = perfil_columnas(df)
    assert perfil.loc["total", "vacios"] == 1
    assert perfil.loc["total", "suma"] == 23
    assert perfil.loc["mujeres", "ceros"] == 0
    assert pd.isna(perfil.loc["cod", "ceros"])
    assert not perfil.loc["varones", "existe_en_origen"]


def test_verificar_identidades_separa_falla_de_no_evaluable():
    resultado = verificar_identidades(_base(), {"sexo": "total - mujeres - varones"})
    assert resultado.attrs["resumen"]["sexo"] == {"ok": 1, "falla": 1, "no_evaluable": 2}
    fallas = resultado[resultado["estado"] == "falla"]
    assert fallas["fila"].tolist() == [1]
    assert fallas["residuo"].tolist() == [1.0]
    no_evaluables = resultado[resultado["estado"] == "no_evaluable"]
    assert no_evaluables["fila"].tolist() == [2, 3]
    assert no_evaluables["residuo"].isna().all()


def test_verificar_identidades_con_tolerancia():
    df = pd.DataFrame({"a": [1.0, 2.0], "b": [1.0005, 2.5]})
    resultado = verificar_identidades(df, {"igual": "a - b"}, tolerancia=0.001)
    assert resultado["fila"].tolist() == [1]


def test_vacios_con_denominador():
    df = pd.DataFrame(
        {
            "total": pd.array([10, None, 8, 5], dtype="Int64"),
            "sin_oferta": pd.array([1, None, 2, 3], dtype="Int64"),
            "no_escrito": pd.array([1, None, None, 3], dtype="Int64"),
            "perdido": pd.array([0, None, None, 3], dtype="Int64"),
            "completa": pd.array([0, 1, 2, 3], dtype="Int64"),
        }
    )
    pares = {c: "total" for c in ["sin_oferta", "no_escrito", "perdido", "completa"]}
    resultado = vacios_con_denominador(df, pares)
    assert resultado["lectura"].to_dict() == {
        "sin_oferta": "no aplica / sin oferta",
        "no_escrito": "probable cero no escrito",
        "perdido": "dato perdido",
        "completa": "sin vacíos",
    }
    assert resultado.loc["no_escrito", "vacios_con_denominador"] == 1


def test_cruzar_diccionario():
    df = pd.DataFrame(columns=["Cod", "total", "extra"])
    dicc = pd.DataFrame({"variable": ["cod", " TOTAL ", "sobrante", None]})
    assert cruzar_diccionario(df, dicc) == {
        "sin_definicion": ["extra"],
        "sin_variable": ["sobrante"],
    }
    assert cruzar_diccionario(df, ["cod", "total", "extra"]) == {
        "sin_definicion": [],
        "sin_variable": [],
    }


def test_buscar_shock():
    t = pd.DataFrame(
        {
            "unidad": ["A"] * 4 + ["B"] * 4,
            "periodo": [2019, 2020, 2021, 2022] * 2,
            "tasa": [5.0, 5.1, 0.5, 4.9, 3.0, 0.4, 3.1, 3.2],
        }
    )
    por_unidad = buscar_shock(t, "tasa", esperado=2020, grupo="unidad").set_index("unidad")
    assert por_unidad["periodo_extremo"].to_dict() == {"A": 2021, "B": 2020}
    assert por_unidad["desfase"].to_dict() == {"A": 1, "B": 0}
    assert por_unidad.loc["A", "mediana_resto"] == 5.0
    total = buscar_shock(t[t.unidad == "A"], "tasa", esperado=2020, sentido="max")
    assert total.loc[0, "periodo_extremo"] == 2020
