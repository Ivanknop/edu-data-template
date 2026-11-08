"""Series de archivos por período: ubicarlos, leerlos en paralelo y pasar de ancho a largo."""

import multiprocessing
import os
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd


def archivos_por_periodo(
    directorio: str | Path, patron: str | re.Pattern, desfase: int = 0
) -> dict[int, Path]:
    """{período: ruta} de los archivos cuyo nombre cumple `patron` (el grupo 1 es el año).

    período = año del nombre − `desfase`. Error si dos archivos caen en el mismo período.
    """
    patron = re.compile(patron)
    resultado: dict[int, Path] = {}
    for ruta in sorted(Path(directorio).iterdir()):
        coincidencia = patron.match(ruta.name)
        if not coincidencia:
            continue
        periodo = int(coincidencia.group(1)) - desfase
        if periodo in resultado:
            raise ValueError(f"Período {periodo} repetido: {resultado[periodo].name}, {ruta.name}")
        resultado[periodo] = ruta
    return dict(sorted(resultado.items()))


def _contexto(lector: Callable):
    # forkserver evita heredar hilos ya abiertos (pyarrow); precargar el módulo acelera el arranque
    if "forkserver" not in multiprocessing.get_all_start_methods():
        return multiprocessing.get_context("spawn")
    contexto = multiprocessing.get_context("forkserver")
    if lector.__module__ != "__main__":
        contexto.set_forkserver_preload([lector.__module__])
    return contexto


def leer_en_paralelo(rutas: Iterable[Path], lector: Callable, procesos: int = 4) -> list:
    """Aplica `lector` a cada ruta en procesos separados y conserva el orden.

    `lector` tiene que ser una función de un módulo (no una lambda). Con menos de 2 procesos
    útiles, lee en serie.
    """
    rutas = list(rutas)
    procesos = min(procesos, len(rutas), os.cpu_count() or 1)
    if procesos < 2:
        return [lector(r) for r in rutas]
    with ProcessPoolExecutor(max_workers=procesos, mp_context=_contexto(lector)) as ejecutor:
        return list(ejecutor.map(lector, rutas))


def ancho_a_largo(
    df: pd.DataFrame,
    claves: Sequence[str],
    bloques: Mapping[str, str],
    sufijos: Sequence[str],
    col_sufijo: str = "sufijo",
) -> pd.DataFrame:
    """Una fila por fila original × sufijo, con una columna por bloque.

    `bloques={"total": "_{}", "mujeres": "m_{}"}`: la columna `m_3` va a `mujeres` con sufijo
    "3". Una columna que no existe en `df` queda NA (no 0).
    """
    claves = list(claves)
    vacia = pd.array([pd.NA] * len(df), dtype="Int64")
    partes = []
    for sufijo in sufijos:
        columnas = {c: df[c].to_numpy() for c in claves}
        columnas[col_sufijo] = sufijo
        for medida, plantilla in bloques.items():
            nombre = plantilla.format(sufijo)
            columnas[medida] = df[nombre].array if nombre in df.columns else vacia
        partes.append(pd.DataFrame(columnas))
    largo = pd.concat(partes, ignore_index=True)
    for clave in claves:
        largo[clave] = largo[clave].astype(df[clave].dtype)
    return largo
