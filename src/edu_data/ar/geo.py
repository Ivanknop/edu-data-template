"""Mapa de provincias en SVG: trazos simplificados, sin sector antártico y con recuadro de CABA.

El recurso ya preparado está versionado en `recursos/provincias_svg.json` (fuente y licencia en
`recursos/FUENTE.md`): un proyecto no necesita descargar ni procesar geometrías.
Regenerarlo: `uv run python -m edu_data.ar.geo <ruta.geojson>` (si no existe, se descarga).
"""

import json
import sys
from datetime import date
from pathlib import Path

from edu_data.ar.provincias import NOMBRES, normalizar_provincia
from edu_data.descarga import descargar

URL_GEOJSON = "https://infra.datos.gob.ar/georef/provincias.geojson"
RECURSO = Path(__file__).parent / "recursos" / "provincias_svg.json"
CABA = "Ciudad de Buenos Aires"
# Sin el sector antártico (al sur de 56° S) el continente no queda diminuto
RECORTE_LONLAT = (-75.0, -56.0, -52.0, -21.0)
# Cónica conforme de Lambert centrada en Argentina
PROYECCION = "+proj=lcc +lat_1=-24 +lat_2=-48 +lat_0=-36 +lon_0=-64 +datum=WGS84 +units=m"
ANCHO_SVG = 420
TOLERANCIA_M = 2_500
# Recuadro de CABA: lado en px y posición de su esquina (x desde la derecha, y como fracción)
LADO_CABA, MARGEN_DERECHO_CABA, ALTURA_CABA = 70, 95, 0.30


def cargar_provincias_svg(ruta: str | Path = RECURSO) -> dict:
    """{"ancho", "alto", "provincias": {nombre: path}, "caba": {...}, "fuente"}.

    `provincias` no incluye CABA: va en `caba["path"]`, ampliada dentro de `caba["recuadro"]`
    ([x, y, ancho, alto]); `caba["real"]` es su posición real en el mapa, para una marca.
    """
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _anillos_a_path(geom, x, y) -> str:
    partes = []
    for poligono in getattr(geom, "geoms", [geom]):
        for anillo in [poligono.exterior, *poligono.interiors]:
            puntos = [f"{x(px):.1f},{y(py):.1f}" for px, py in anillo.coords]
            partes.append("M" + "L".join(puntos) + "Z")
    return "".join(partes)


def preparar_provincias_svg(
    geojson: str | Path, destino: str | Path | None = RECURSO, completo: bool = True
) -> dict:
    """Arma el recurso SVG desde un GeoJSON de provincias (columna `nombre`, en WGS84).

    `completo=True` exige las 24 provincias. Con `destino=None` no escribe el archivo.
    """
    import geopandas as gpd  # solo para regenerar el recurso
    from shapely.geometry import box

    g = gpd.read_file(geojson)[["nombre", "geometry"]]
    g = g.set_crs(4326) if g.crs is None else g.to_crs(4326)
    g["provincia"] = [normalizar_provincia(n) for n in g["nombre"]]
    g = g.dissolve("provincia").reset_index()
    faltan = set(NOMBRES) - set(g["provincia"])
    if completo and faltan:
        raise ValueError(f"Provincias sin geometría: {sorted(faltan)}")
    g["geometry"] = g.geometry.intersection(box(*RECORTE_LONLAT))
    g = g.to_crs(PROYECCION)

    minx, miny, maxx, maxy = g.total_bounds
    escala = ANCHO_SVG / (maxx - minx)
    alto = (maxy - miny) * escala

    def x(px):
        return (px - minx) * escala

    def y(py):
        return (maxy - py) * escala

    simples = g.geometry.simplify(TOLERANCIA_M, preserve_topology=True)
    provincias = {
        p: _anillos_a_path(geom, x, y)
        for p, geom in zip(g["provincia"], simples, strict=True)
        if p != CABA and not geom.is_empty
    }
    salida = {
        "fuente": f"Servicio Georef – argentina.gob.ar/georef (IGN), {URL_GEOJSON}",
        "ancho": ANCHO_SVG,
        "alto": round(alto, 1),
        "provincias": provincias,
    }
    if CABA in set(g["provincia"]):
        # CABA ocupa unos pocos píxeles: va ampliada en un recuadro y sin simplificar
        caba = g.loc[g["provincia"] == CABA, "geometry"].iloc[0]
        cminx, cminy, cmaxx, cmaxy = caba.bounds
        ox, oy = ANCHO_SVG - MARGEN_DERECHO_CABA, alto * ALTURA_CABA
        cesc = LADO_CABA / max(cmaxx - cminx, cmaxy - cminy)
        real = caba.centroid
        salida["caba"] = {
            "path": _anillos_a_path(
                caba, lambda px: ox + (px - cminx) * cesc, lambda py: oy + (cmaxy - py) * cesc
            ),
            "recuadro": [round(ox - 8, 1), round(oy - 8, 1), LADO_CABA + 16, LADO_CABA + 16],
            "real": [round(x(real.x), 1), round(y(real.y), 1)],
        }
    if destino is not None:
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(salida, ensure_ascii=False), encoding="utf-8")
    return salida


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: uv run python -m edu_data.ar.geo <ruta.geojson>")
    ruta = Path(sys.argv[1])
    if descargar(URL_GEOJSON, ruta):
        print(f"Descargado {ruta} ({date.today().isoformat()})")
    geo = preparar_provincias_svg(ruta)
    print(f"{len(geo['provincias'])} provincias + CABA → {RECURSO} ({RECURSO.stat().st_size:,} B)")
