# Changelog

Versiones de la plantilla. Los proyectos generados se actualizan con la skill
`actualizar-plantilla`, que lee este archivo entre la versión del proyecto y la de destino.

Formato de cada entrada:
- **Cambios**: qué cambia en los proyectos que se actualizan.
- **Pasos manuales**: lo que la actualización no hace sola (si no hay, "Ninguno").

## v0.2.0

### Cambios
- **Sin Jupyter:** fuera `jupyterlab`, `ipykernel`, el registro del kernel, la extensión de VS Code
  y la carpeta `notebooks/`. El flujo es scripts en `src/`, tests y visores.
- **`edu_data.ar`** (opcional, el resto no depende de él):
  - `provincias`: nombre canónico, códigos INDEC e ISO, equivalencias entre fuentes.
  - `niveles`: primaria de 6 o 7 años por provincia (fuente oficial) y `nivel_de(grado, provincia)`.
  - `geo`: mapa SVG de provincias versionado en `ar/recursos/` (Georef/IGN, CC BY 4.0), sin
    sector antártico y con recuadro de CABA. No hace falta descargar geometrías.
  - `datos_abiertos_educacion`: links de la página de datos abiertos (planilla + SharePoint).
- **Módulos nuevos:** `descarga` (reintentos, nunca pisa), `series` (archivos por período,
  lectura en paralelo, ancho → largo), `metricas` (`pct`, `sumar_por`, `sumar_excluyendo`),
  `cifras` (formato es-AR, verificación de cifras en textos), `visor` (`renderizar`, `a_lista`).
- `perfil`: `vacios_con_denominador`, `cruzar_diccionario`, `buscar_shock`.
- `io`: lectura más rápida (DataFrame armado de una vez, enteros con una sola regex).
- `tests/conftest.py`: fixture `requiere_crudos` (skip en local, fail en CI).
- **Skills nuevas:** `visor-interactivo` y `auditar`.
- **Skills modificadas:**
  - `dataset-nuevo`: descarga por script, vacíos frente al denominador ("cero no escrito"),
    período con shock y desfase de todo el archivo, glosas al proponer alcance.
  - `validar-calidad`: materialidad, serie "total sin `<unidad>`", cifras de textos con test,
    señales revisadas sin alerta, marca de conteo por bloque para imputaciones masivas.
  - `publicar`: README propio, coherencia con CLAUDE.md al versionar crudos, tests sin
    `data/processed/`, borra `publicar.yml.ejemplo` después de copiarlo.
  - `actualizar-plantilla`: actualiza la línea "Generado desde" del README y avisa si cambió
    `docs/entorno.md`.
- `CLAUDE.md`: plan por etapas al pedir autorización, glosas, decisiones en el diccionario (no en
  la memoria de Claude), performance, cero no escrito, categorías derivadas, materialidad,
  cifras de textos con test, tests desde `data/raw/`. Corrige la contradicción sobre versionar
  crudos.
- `settings.json`: se permite crear archivos en `data/raw/` (los insumos entran por script de
  descarga, que nunca pisa); se sigue negando editarlos. Se agrega `Bash(time:*)`.
- Navegador opcional para verificar visores: `INSTALAR_NAVEGADOR=1` instala Chromium en
  `post-create.sh`.
- Generador: el README del proyecto tiene solo sus secciones y la línea "Generado desde
  edu-data-template vX"; el entorno pasa a `docs/entorno.md` (según `-so`); `.plantilla.json`
  guarda la URL HTTPS.
- `data/_plantilla_diccionario.md`: sección "Decisiones".

### Pasos manuales
1. **Nombres que chocan:** si el proyecto ya tiene módulos propios con el nombre de alguno nuevo
   (`src/edu_data/descarga.py`, `series.py`, `metricas.py`, `cifras.py`, `visor.py`, `ar/`),
   renombrarlos **antes** de actualizar y ajustar sus imports.
2. **Jupyter y `notebooks/`:** la actualización borra `notebooks/.gitkeep`. Si la carpeta quedó
   vacía, borrarla. Si había notebooks propios, pasar lo útil a `src/` o conservarlos; si se
   sigue usando Jupyter, `uv add jupyterlab ipykernel`.
3. **Entorno fuera del README:** crear `docs/entorno.md` desde el de la plantilla
   (`git -C "$C" show "$D:docs/entorno.md"`), dejar solo el bloque `so:` del sistema del proyecto
   (sin las marcas) y borrar del README "Requisitos", "Uso", "Qué incluye" y "Comandos
   frecuentes". Agregar al final del README `Generado desde [edu-data-template](<URL>) <versión>`.
4. **`.plantilla.json`:** si `plantilla` es una URL SSH, pasarla a HTTPS.
5. **`data/` no se actualiza:** traer `data/_plantilla_diccionario.md` de la plantilla
   (`git -C "$C" show "$D:data/_plantilla_diccionario.md"`), agregar la sección "Decisiones" a
   los `data/diccionario_*.md` existentes y mover ahí las decisiones que estén solo en la
   memoria de Claude.

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
