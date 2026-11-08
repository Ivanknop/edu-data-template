import pytest

from edu_data.cifras import formatear, verificar_cifras


@pytest.mark.parametrize(
    ("valor", "decimales", "esperado"),
    [
        (2.25, 1, "2,3"),
        (2.675, 2, "2,68"),
        (3.0, 1, "3"),
        (3.04, 1, "3"),
        (1234567.891, 1, "1.234.567,9"),
        (-0.04, 1, "0"),
        (12.5, 0, "13"),
        (12.5, 2, "12,50"),
        (-1500, 1, "-1.500"),
    ],
)
def test_formatear(valor, decimales, esperado):
    assert formatear(valor, decimales) == esperado


def test_formatear_sin_miles():
    assert formatear(1234.5, miles=False) == "1234,5"


def test_formatear_na():
    with pytest.raises(ValueError):
        formatear(float("nan"))


def test_verificar_cifras():
    texto = "La tasa pasa de 12,3 % a 2,35 % en 1.500 escuelas (21 de 24)."
    assert verificar_cifras(texto, [12.31, 1500, 21, 24]) == []
    # "2,3" no se confunde con "12,3" ni con "2,35"
    assert verificar_cifras(texto, [2.3]) == ["2,3"]
    assert verificar_cifras(texto, [2.35], decimales=2) == []
