"""Cifras para textos (alertas, portadas, README): un solo redondeo y verificación en tests."""

import re
from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd


def formatear(valor: float, decimales: int = 1, miles: bool = True) -> str:
    """Formato es-AR: coma decimal y punto de miles. Sin decimales si son todos cero.

    Redondea una sola vez, desde el valor sin redondear y "mitad hacia arriba"
    (2,25 → 2,3). Error con NA: una cifra faltante en un texto se resuelve en el texto.
    """
    if pd.isna(valor):
        raise ValueError("No se formatea un valor NA")
    redondeado = Decimal(repr(float(valor))).quantize(
        Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP
    )
    if redondeado == redondeado.to_integral_value():
        redondeado = redondeado.quantize(Decimal(1))
    if redondeado == 0:
        redondeado = abs(redondeado)
    texto = f"{redondeado:,}" if miles else f"{redondeado}"
    return texto.translate(str.maketrans({",": ".", ".": ","}))


def verificar_cifras(
    texto: str, esperados: Iterable[float], decimales: int = 1, miles: bool = True
) -> list[str]:
    """Cifras esperadas (formateadas con `formatear`) que no aparecen en `texto`. Vacía = ok.

    Busca la cifra completa: "2,3" no coincide dentro de "12,3" ni de "2,35".
    """
    faltantes = []
    for valor in esperados:
        cifra = formatear(valor, decimales, miles)
        patron = rf"(?<![\d.,]){re.escape(cifra)}(?![\d]|[.,]\d)"
        if not re.search(patron, texto):
            faltantes.append(cifra)
    return faltantes
