import pandas as pd
import pytest

from edu_data.metricas import pct, sumar_excluyendo, sumar_por


def _tabla():
    return pd.DataFrame(
        {
            "unidad": ["A", "A", "B", "C", "C"],
            "periodo": [2020, 2021, 2020, 2020, 2021],
            "valor": pd.array([10, 20, 5, None, 7], dtype="Int64"),
            "parte": pd.array([1, 2, 1, None, None], dtype="Int64"),
        }
    )


def test_pct_sin_redondear_y_na():
    parte = pd.Series([1, 1, 1, None], dtype="Int64")
    total = pd.Series([3, 0, None, 4], dtype="Int64")
    resultado = pct(parte, total)
    assert resultado[0] == pytest.approx(100 / 3)
    assert resultado[1:].isna().all()


def test_sumar_por_deja_na_los_grupos_sin_datos():
    t = _tabla()
    resultado = sumar_por(t, ["unidad"], ["valor", "parte"]).set_index("unidad")
    assert resultado.loc["A", "valor"] == 30
    assert pd.isna(resultado.loc["C", "parte"])
    assert resultado.loc["C", "valor"] == 7


def test_sumar_por_sin_claves():
    resultado = sumar_por(_tabla(), [], ["valor"])
    assert len(resultado) == 1
    assert resultado.loc[0, "valor"] == 42


def test_sumar_excluyendo():
    resultado = sumar_excluyendo(_tabla(), "unidad", ["A"], ["periodo"], ["valor"], "Total sin A")
    assert resultado.columns.tolist() == ["unidad", "periodo", "valor"]
    assert resultado["unidad"].unique().tolist() == ["Total sin A"]
    assert resultado.set_index("periodo")["valor"].to_dict() == {2020: 5, 2021: 7}
    total = sumar_excluyendo(_tabla(), "unidad", [], ["periodo"], ["valor"], "Total")
    assert total.set_index("periodo")["valor"].to_dict() == {2020: 15, 2021: 27}


def test_sumar_excluyendo_unidad_inexistente():
    with pytest.raises(ValueError, match="Z"):
        sumar_excluyendo(_tabla(), "unidad", ["Z"], ["periodo"], ["valor"], "x")
