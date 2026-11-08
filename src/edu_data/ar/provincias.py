"""Provincias argentinas: nombre canónico, código INDEC e ISO 3166-2, y equivalencias entre fuentes.

El nombre canónico es el corto que usan las bases educativas ("Ciudad de Buenos Aires",
"Tierra del Fuego"). Los códigos INDEC son texto de dos dígitos (conservan el cero inicial).
"""

import unicodedata

import pandas as pd

# (código INDEC, ISO 3166-2, nombre canónico)
_TABLA = [
    ("02", "AR-C", "Ciudad de Buenos Aires"),
    ("06", "AR-B", "Buenos Aires"),
    ("10", "AR-K", "Catamarca"),
    ("14", "AR-X", "Córdoba"),
    ("18", "AR-W", "Corrientes"),
    ("22", "AR-H", "Chaco"),
    ("26", "AR-U", "Chubut"),
    ("30", "AR-E", "Entre Ríos"),
    ("34", "AR-P", "Formosa"),
    ("38", "AR-Y", "Jujuy"),
    ("42", "AR-L", "La Pampa"),
    ("46", "AR-F", "La Rioja"),
    ("50", "AR-M", "Mendoza"),
    ("54", "AR-N", "Misiones"),
    ("58", "AR-Q", "Neuquén"),
    ("62", "AR-R", "Río Negro"),
    ("66", "AR-A", "Salta"),
    ("70", "AR-J", "San Juan"),
    ("74", "AR-D", "San Luis"),
    ("78", "AR-Z", "Santa Cruz"),
    ("82", "AR-S", "Santa Fe"),
    ("86", "AR-G", "Santiago del Estero"),
    ("90", "AR-T", "Tucumán"),
    ("94", "AR-V", "Tierra del Fuego"),
]

PROVINCIAS: dict[str, str] = {codigo: nombre for codigo, _, nombre in _TABLA}
CODIGOS_ISO: dict[str, str] = {nombre: iso for _, iso, nombre in _TABLA}
NOMBRES = tuple(PROVINCIAS.values())

# Variantes de otras fuentes (IGN/georef, INDEC, uso corriente), comparadas sin tildes
_VARIANTES = {
    "ciudad autonoma de buenos aires": "Ciudad de Buenos Aires",
    "caba": "Ciudad de Buenos Aires",
    "capital federal": "Ciudad de Buenos Aires",
    "tierra del fuego, antartida e islas del atlantico sur": "Tierra del Fuego",
    "tierra del fuego antartida e islas del atlantico sur": "Tierra del Fuego",
}


def _clave(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    clave = " ".join(sin_tildes.lower().split())
    for prefijo in ("provincia de ", "provincia del "):
        if clave.startswith(prefijo):
            clave = clave.removeprefix(prefijo)
    return clave


_EQUIVALENCIAS = {**{_clave(n): n for n in NOMBRES}, **_VARIANTES}


def normalizar_provincia(nombre: str) -> str:
    """Nombre canónico desde cualquier variante (mayúsculas, tildes, "Provincia de…").

    Error si no se reconoce: mejor que dejar pasar una provincia sin cruzar.
    """
    clave = _clave(str(nombre))
    if clave not in _EQUIVALENCIAS:
        raise ValueError(f"Provincia no reconocida: {nombre!r}")
    return _EQUIVALENCIAS[clave]


def normalizar_serie(serie: pd.Series) -> pd.Series:
    """`normalizar_provincia` sobre una columna (calcula una vez por valor distinto)."""
    mapa = {v: normalizar_provincia(v) for v in serie.dropna().unique()}
    return serie.map(mapa).astype("string")


def codigo_indec(nombre: str) -> str:
    """Código INDEC de dos dígitos ("02" = Ciudad de Buenos Aires)."""
    canonico = normalizar_provincia(nombre)
    return next(c for c, n in PROVINCIAS.items() if n == canonico)


def nombre_desde_codigo(codigo: str | int) -> str:
    """Nombre canónico desde el código INDEC (acepta 2, "2" o "02")."""
    codigo = str(codigo).strip().zfill(2)
    if codigo not in PROVINCIAS:
        raise ValueError(f"Código INDEC de provincia desconocido: {codigo!r}")
    return PROVINCIAS[codigo]
