import json

import pandas as pd
import pytest

from edu_data.ar import datos_abiertos_educacion as dae
from edu_data.ar.geo import cargar_provincias_svg, preparar_provincias_svg
from edu_data.ar.niveles import PRIMARIA_6, PRIMARIA_7, nivel_de, ultimo_grado_primaria
from edu_data.ar.provincias import (
    CODIGOS_ISO,
    NOMBRES,
    PROVINCIAS,
    codigo_indec,
    nombre_desde_codigo,
    normalizar_provincia,
    normalizar_serie,
)

# --- provincias ---


def test_provincias():
    assert len(PROVINCIAS) == 24
    assert all(len(c) == 2 for c in PROVINCIAS)
    assert set(CODIGOS_ISO) == set(NOMBRES)
    assert codigo_indec("Ciudad Autónoma de Buenos Aires") == "02"
    assert nombre_desde_codigo(6) == "Buenos Aires"


@pytest.mark.parametrize(
    ("variante", "canonico"),
    [
        ("CIUDAD AUTONOMA DE BUENOS AIRES", "Ciudad de Buenos Aires"),
        ("caba", "Ciudad de Buenos Aires"),
        ("Tierra del Fuego, Antártida e Islas del Atlántico Sur", "Tierra del Fuego"),
        ("Provincia del Neuquén", "Neuquén"),
        ("  cordoba ", "Córdoba"),
        ("Provincia de Buenos Aires", "Buenos Aires"),
    ],
)
def test_normalizar_provincia(variante, canonico):
    assert normalizar_provincia(variante) == canonico


def test_normalizar_provincia_desconocida():
    with pytest.raises(ValueError):
        normalizar_provincia("Atlántida")
    with pytest.raises(ValueError):
        nombre_desde_codigo("99")


def test_normalizar_serie():
    serie = pd.Series(["CABA", None, "Salta"])
    assert normalizar_serie(serie).tolist() == ["Ciudad de Buenos Aires", pd.NA, "Salta"]


# --- niveles ---


def test_estructura_de_primaria_cubre_las_24():
    assert not PRIMARIA_6 & PRIMARIA_7
    assert PRIMARIA_6 | PRIMARIA_7 == set(NOMBRES)
    assert ultimo_grado_primaria("CABA") == 7
    assert ultimo_grado_primaria("Córdoba") == 6


def test_nivel_de():
    assert nivel_de(7, "Salta") == "primaria"
    assert nivel_de(7, "Córdoba") == "secundaria"
    provincias = pd.Series(["Salta", "Córdoba", "Salta", "Córdoba"], index=[10, 11, 12, 13])
    grados = pd.Series(["6", "6", "8", "13"], index=provincias.index)
    assert nivel_de(grados, provincias).tolist() == [
        "primaria",
        "primaria",
        "secundaria",
        "secundaria",
    ]
    assert nivel_de(7, provincias).index.tolist() == [10, 11, 12, 13]


@pytest.mark.parametrize("grado", [0, 15, "1314", 2.5])
def test_nivel_de_grado_invalido(grado):
    with pytest.raises(ValueError):
        nivel_de(grado, "Salta")


# --- geo ---


def test_recurso_svg():
    geo = cargar_provincias_svg()
    assert set(geo["provincias"]) == set(NOMBRES) - {"Ciudad de Buenos Aires"}
    assert geo["caba"]["path"].startswith("M")
    assert 0 < geo["alto"] and geo["ancho"] == 420
    assert "Georef" in geo["fuente"]


def _cuadrado(x, y, lado):
    return [[[x, y], [x + lado, y], [x + lado, y + lado], [x, y + lado], [x, y]]]


def test_preparar_provincias_svg_recorta_la_antartida(tmp_path):
    rasgos = [
        ("Buenos Aires", _cuadrado(-63, -40, 5)),
        ("Ciudad Autónoma de Buenos Aires", _cuadrado(-58.5, -34.7, 0.2)),
        # Continente más un sector antártico que debe quedar afuera
        ("Tierra del Fuego, Antártida e Islas del Atlántico Sur", _cuadrado(-68, -55, 2)),
        ("Tierra del Fuego, Antártida e Islas del Atlántico Sur", _cuadrado(-60, -80, 10)),
    ]
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"nombre": n},
                "geometry": {"type": "Polygon", "coordinates": c},
            }
            for n, c in rasgos
        ],
    }
    ruta = tmp_path / "p.geojson"
    ruta.write_text(json.dumps(geojson))
    with pytest.raises(ValueError, match="sin geometría"):
        preparar_provincias_svg(ruta, destino=None)
    geo = preparar_provincias_svg(ruta, destino=tmp_path / "p.json", completo=False)
    assert set(geo["provincias"]) == {"Buenos Aires", "Tierra del Fuego"}
    # Recortado va de 34,5° S a 55° S (≈ 2,8 veces el ancho); con el sector antártico pasaría de 6
    assert geo["alto"] < 3.5 * geo["ancho"]
    assert cargar_provincias_svg(tmp_path / "p.json") == geo


# --- datos abiertos ---

PLANILLA = """año,nombre,descripción,link
2023,2023 Base - agregada.csv,Base,https://sp.example/a?e=1
2024,2024 Base - agregada.csv,Base,https://sp.example/b?e=2
2024,Otra cosa.pdf,Doc,https://sp.example/c
"""


def test_links_de_la_planilla():
    assert dae.links(PLANILLA, r"^\d{4} Base - agregada\.csv$") == {
        "2023 Base - agregada.csv": "https://sp.example/a?e=1",
        "2024 Base - agregada.csv": "https://sp.example/b?e=2",
    }


def test_descargar_sharepoint(tmp_path, monkeypatch):
    pedidos = []

    def abrir_falso(url, abridor=None, timeout=60):
        pedidos.append(url)
        return b"contenido" if url.endswith("download=1") else b"<html>"

    monkeypatch.setattr(dae, "abrir", abrir_falso)
    destino = tmp_path / "a.csv"
    assert dae.descargar_sharepoint("https://sp.example/a?e=1", destino)
    assert pedidos == ["https://sp.example/a?e=1", "https://sp.example/a?e=1&download=1"]
    assert destino.read_bytes() == b"contenido"
    assert not dae.descargar_sharepoint("https://sp.example/a?e=1", destino)
