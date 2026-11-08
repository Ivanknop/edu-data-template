"""Porcentajes y sumas que respetan "vacío no es cero"."""

from collections.abc import Sequence

import pandas as pd


def pct(parte: pd.Series, total: pd.Series) -> pd.Series:
    """100 · parte / total, sin redondear. NA si el total es NA o 0."""
    total = total.astype("Float64")
    return 100 * parte.astype("Float64") / total.mask(total == 0)


def sumar_por(df: pd.DataFrame, claves: Sequence[str], medidas: Sequence[str]) -> pd.DataFrame:
    """Suma de `medidas` por `claves`. Un grupo sin ningún dato queda NA, no 0."""
    claves, medidas = list(claves), list(medidas)
    if not claves:
        return df[medidas].sum(min_count=1).to_frame().T.astype(df[medidas].dtypes.to_dict())
    agrupado = df.groupby(claves, dropna=False, observed=True, sort=True)
    return agrupado[medidas].sum(min_count=1).reset_index()


def sumar_excluyendo(
    df: pd.DataFrame,
    unidad: str,
    excluir: Sequence[str],
    claves: Sequence[str],
    medidas: Sequence[str],
    etiqueta: str,
) -> pd.DataFrame:
    """Suma de las unidades que no están en `excluir`, con `unidad = etiqueta`.

    `claves`: el resto de la agrupación (p. ej. período, nivel), sin `unidad`. Con `excluir=[]`
    da el total. Error si alguna unidad a excluir no aparece: suele ser un nombre mal escrito.
    """
    faltan = set(excluir) - set(df[unidad].dropna())
    if faltan:
        raise ValueError(f"Unidades a excluir que no están en '{unidad}': {sorted(faltan)}")
    resto = df[~df[unidad].isin(list(excluir))]
    total = sumar_por(resto, claves, medidas)
    total.insert(0, unidad, etiqueta)
    return total
