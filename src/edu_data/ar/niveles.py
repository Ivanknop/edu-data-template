"""Estructura del nivel primario por provincia (6 o 7 años) y nivel de un año de estudio.

Fuente: Ministerio de Educación de la Nación, Mapa Educativo Nacional, "Primaria"
(https://mapa.educacion.gob.ar/tag/primaria), consultado el 2026-11-08. La Ley de Educación
Nacional 26.206 deja a cada jurisdicción elegir 6+6 o 7+5. Es la estructura vigente: algunas
provincias cambiaron de estructura y en series largas hay que verificarla con los datos.
"""

import pandas as pd

from edu_data.ar.provincias import normalizar_provincia

PRIMARIA_6 = frozenset(
    {
        "Buenos Aires",
        "Catamarca",
        "Chubut",
        "Córdoba",
        "Corrientes",
        "Entre Ríos",
        "Formosa",
        "La Pampa",
        "San Juan",
        "San Luis",
        "Tierra del Fuego",
        "Tucumán",
    }
)
PRIMARIA_7 = frozenset(
    {
        "Chaco",
        "Ciudad de Buenos Aires",
        "Jujuy",
        "La Rioja",
        "Mendoza",
        "Misiones",
        "Neuquén",
        "Río Negro",
        "Salta",
        "Santa Cruz",
        "Santa Fe",
        "Santiago del Estero",
    }
)
FUENTE = "https://mapa.educacion.gob.ar/tag/primaria"
# Años de estudio corridos: 1º de primaria = 1; las secundarias técnicas llegan a 13 o 14
GRADO_MAXIMO = 14


def ultimo_grado_primaria(provincia: str) -> int:
    """6 o 7 según la estructura de la provincia (acepta variantes del nombre)."""
    return 7 if normalizar_provincia(provincia) in PRIMARIA_7 else 6


def nivel_de(grado, provincia):
    """Nivel ("primaria" o "secundaria") de un año de estudio corrido (1 a 14) en una provincia.

    `grado` y `provincia` pueden ser escalares o Series (con el mismo índice). Error con años
    fuera de rango o no numéricos, y con provincias no reconocidas.
    """
    if not isinstance(grado, pd.Series) and not isinstance(provincia, pd.Series):
        return nivel_de(pd.Series([grado]), pd.Series([provincia])).iloc[0]
    indice = (grado if isinstance(grado, pd.Series) else provincia).index
    grados = pd.to_numeric(pd.Series(grado, index=indice), errors="coerce")
    invalidos = grados.isna() | (grados % 1 != 0) | ~grados.between(1, GRADO_MAXIMO)
    if invalidos.any():
        malos = sorted(map(str, pd.Series(grado, index=indice)[invalidos].unique()))
        raise ValueError(f"Años de estudio fuera de 1–{GRADO_MAXIMO}: {malos}")
    provincias = pd.Series(provincia, index=indice)
    ultimo = provincias.map({p: ultimo_grado_primaria(p) for p in provincias.unique()})
    nivel = (grados <= ultimo).map({True: "primaria", False: "secundaria"})
    return nivel.astype("string")
