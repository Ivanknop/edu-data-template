# Changelog

Versiones de la plantilla. Los proyectos generados se actualizan con la skill
`actualizar-plantilla`, que lee este archivo entre la versión del proyecto y la de destino.

Formato de cada entrada:
- **Cambios**: qué cambia en los proyectos que se actualizan.
- **Pasos manuales**: lo que la actualización no hace sola (si no hay, "Ninguno").

## v0.1.0

### Cambios
- Skills de Claude: `dataset-nuevo` (incorporar y documentar un dataset), `validar-calidad`
  (controles de pertinencia y registro único de alertas) y `publicar` (GitHub Pages o artifact).
- Skill `actualizar-plantilla`: actualiza un proyecto generado a una versión nueva de la plantilla
  con merge de tres vías.
- Paquete `edu_data` con tests:
  - `io`: detección de formato, lectura de CSV oficiales (vacío ≠ 0, códigos como texto),
    unificación de esquemas entre períodos, lectura de hojas de Excel.
  - `perfil`: perfil por columna y verificación de identidades contables.
  - `validacion_base`: saltos interanuales, atípicos robustos, coherencia y alertas.
- `CLAUDE.md` con convenciones de la retrospectiva: período de referencia vs. año del archivo,
  vacío no es cero, calidad de datos, visualización on demand, marca `GENERADO por`.
- Plantillas de documentación: `data/README.md` y `data/_plantilla_diccionario.md`.
- Workflow de ejemplo para GitHub Pages: `.github/workflows/publicar.yml.ejemplo`.
- `.gitattributes`: los crudos (`data/raw/**`) se guardan byte a byte.
- Generador con soporte para Windows (`-so windows`) y registro de origen y versión en
  `.plantilla.json`.

### Pasos manuales
Ninguno.
