# Fuente de `provincias_svg.json`

- **Datos:** límites provinciales del Servicio Georef (Dirección Nacional de Datos e Información
  Pública), elaborados en base a datos del Instituto Geográfico Nacional (IGN).
- **Archivo:** <https://infra.datos.gob.ar/georef/provincias.geojson> (WGS84), descargado el
  2026-11-08.
- **Licencia:** Creative Commons Atribución 4.0 Internacional (CC BY 4.0).
- **Atribución requerida:** "Servicio Georef – argentina.gob.ar/georef". Incluirla en el pie de
  los visores que usen el mapa.

## Transformaciones
`edu_data.ar.geo.preparar_provincias_svg`:
1. Nombres normalizados a los canónicos de `edu_data.ar.provincias`.
2. Recorte a 75°–52° O y 56°–21° S: deja afuera el sector antártico e islas lejanas, solo por
   escala del dibujo. No implica una posición sobre límites.
3. Proyección cónica conforme de Lambert centrada en Argentina.
4. Simplificación (tolerancia 2,5 km) y trazos SVG de 420 px de ancho.
5. CABA va aparte, sin simplificar, ampliada en un recuadro.

Regenerar: `uv run python -m edu_data.ar.geo <ruta.geojson>`.
