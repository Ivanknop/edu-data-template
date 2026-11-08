"""Perfil de columnas, identidades contables, vacíos, diccionario y shocks de un dataset."""

from collections.abc import Iterable, Mapping

import pandas as pd


def perfil_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Tipo, válidos, vacíos, ceros, suma, máximo y distintos por columna."""
    ausentes = set(df.attrs.get("columnas_ausentes", []))
    filas = []
    for columna in df.columns:
        serie = df[columna]
        numerica = pd.api.types.is_numeric_dtype(serie) and not pd.api.types.is_bool_dtype(serie)
        filas.append(
            {
                "columna": columna,
                "tipo": str(serie.dtype),
                "validos": int(serie.notna().sum()),
                "vacios": int(serie.isna().sum()),
                "pct_vacios": round(100 * serie.isna().mean(), 2) if len(serie) else 0.0,
                "ceros": int((serie == 0).sum()) if numerica else pd.NA,
                "suma": serie.sum() if numerica else pd.NA,
                "maximo": serie.max() if numerica else pd.NA,
                "distintos": int(serie.nunique()),
                "existe_en_origen": columna not in ausentes,
            }
        )
    return pd.DataFrame(filas).set_index("columna")


def verificar_identidades(
    df: pd.DataFrame, reglas: dict[str, str], tolerancia: float = 0
) -> pd.DataFrame:
    """Filas que no dan 0 en cada regla: "falla" o "no_evaluable" (algún término NA).

    Conteos por regla en attrs["resumen"].
    """
    resultados = []
    resumen = {}
    for nombre, expresion in reglas.items():
        residuo = pd.to_numeric(df.eval(expresion, engine="python"), errors="coerce")
        residuo = pd.Series(residuo, index=df.index).astype("Float64")
        no_evaluable = residuo.isna()
        falla = ~no_evaluable & (residuo.abs() > tolerancia)
        resumen[nombre] = {
            "ok": int((~no_evaluable & ~falla).sum()),
            "falla": int(falla.sum()),
            "no_evaluable": int(no_evaluable.sum()),
        }
        for estado, mascara in (("falla", falla), ("no_evaluable", no_evaluable)):
            mascara = mascara.fillna(False).astype(bool)
            resultados.append(
                pd.DataFrame(
                    {
                        "regla": nombre,
                        "fila": df.index[mascara],
                        "estado": estado,
                        "residuo": residuo[mascara].to_numpy(),
                    }
                )
            )
    salida = pd.concat(resultados, ignore_index=True)
    salida.attrs["resumen"] = resumen
    return salida


def vacios_con_denominador(df: pd.DataFrame, pares: Mapping[str, str]) -> pd.DataFrame:
    """Por columna: dónde caen sus vacíos respecto de su denominador ({columna: denominador}).

    `lectura` es una señal para decidir con el usuario, no una decisión:
    - vacíos solo donde el denominador también falta → "no aplica / sin oferta";
    - vacíos con denominador presente y ningún 0 en la columna → "probable cero no escrito";
    - vacíos con denominador presente y con ceros escritos → "dato perdido".
    """
    filas = []
    for columna, denominador in pares.items():
        vacio = df[columna].isna()
        con_denominador = vacio & df[denominador].notna()
        ceros = int((df[columna] == 0).fillna(False).sum())
        if not vacio.any():
            lectura = "sin vacíos"
        elif not con_denominador.any():
            lectura = "no aplica / sin oferta"
        elif ceros == 0:
            lectura = "probable cero no escrito"
        else:
            lectura = "dato perdido"
        filas.append(
            {
                "columna": columna,
                "denominador": denominador,
                "vacios": int(vacio.sum()),
                "vacios_con_denominador": int(con_denominador.sum()),
                "ceros": ceros,
                "lectura": lectura,
            }
        )
    return pd.DataFrame(filas).set_index("columna")


def cruzar_diccionario(
    df: pd.DataFrame, dicc: pd.DataFrame | Iterable[str], col: str = "variable"
) -> dict[str, list[str]]:
    """Variables sin definición y definiciones sin variable, sin distinguir mayúsculas."""
    definidas = dicc[col] if isinstance(dicc, pd.DataFrame) else dicc
    en_dicc = {str(v).strip().lower() for v in definidas if pd.notna(v) and str(v).strip()}
    en_datos = {str(c).strip().lower() for c in df.columns}
    return {
        "sin_definicion": sorted(en_datos - en_dicc),
        "sin_variable": sorted(en_dicc - en_datos),
    }


def buscar_shock(
    t: pd.DataFrame,
    valor: str,
    esperado: int,
    periodo: str = "periodo",
    grupo: str | None = None,
    sentido: str = "min",
) -> pd.DataFrame:
    """Dónde cae el extremo de una serie frente al período en que se espera un shock.

    Una fila por grupo (o una sola): período del mínimo (o máximo), su valor, la mediana del
    resto y `desfase` = período del extremo − `esperado`. Si el shock aparece en el archivo
    siguiente al esperado en casi todos los grupos, el archivo informa el período anterior.
    """
    if sentido not in ("min", "max"):
        raise ValueError("sentido debe ser 'min' o 'max'")
    claves = [grupo] if grupo else []
    filas = []
    grupos = t.groupby(claves, dropna=False) if claves else [((), t)]
    for clave, serie in grupos:
        serie = serie.dropna(subset=[valor]).sort_values(periodo)
        if serie.empty:
            continue
        valores = serie[valor].astype("Float64")
        posicion = valores.idxmin() if sentido == "min" else valores.idxmax()
        extremo = serie.loc[posicion, periodo]
        fila = dict(zip(claves, clave if isinstance(clave, tuple) else (clave,), strict=True))
        fila.update(
            periodo_extremo=extremo,
            valor_extremo=valores[posicion],
            mediana_resto=valores.drop(posicion).median(),
            desfase=int(extremo) - esperado,
        )
        filas.append(fila)
    return pd.DataFrame(filas)
