# edu-data-template

<!-- plantilla:inicio -->
Plantilla para analizar datasets educativos con Python y Claude Code, en un devcontainer
reproducible. No requiere Python instalado en la máquina: solo Docker.
Requisitos, uso y qué incluye: [`docs/entorno.md`](docs/entorno.md).

## Crear un proyecto nuevo
Esta plantilla no se usa para trabajar: se usa para generar proyectos.

```bash
scripts/nuevo_proyecto.sh -name ~/proyectos/mi-analisis -so linux     # o -so windows
```
En Windows, correrlo desde WSL2 o Git Bash.
Genera el directorio con todo lo necesario: nombre del proyecto en `pyproject.toml` y en el
devcontainer, un README con las secciones del proyecto a completar y `docs/entorno.md` para el
sistema operativo elegido.
El versionado (`git init`, remote, commits) queda a cargo de cada proyecto.

## Versiones y actualización de proyectos
- Cada proyecto guarda en `.plantilla.json` el origen (URL HTTPS) y la versión de la plantilla
  (`git describe --tags --always`: un tag o un hash). Conviene generar desde un tag.
- Al publicar una versión: entrada en `CHANGELOG.md` ("Cambios" y "Pasos manuales") y tag.
- `.plantilla/excluir_actualizacion.txt` lista lo que la actualización nunca toca.
- En el proyecto, la skill `actualizar-plantilla` trae los cambios con merge de tres vías.
<!-- plantilla:fin -->

<!-- proyecto:inicio
_Completar: en una línea, qué pregunta responde este análisis._

## Qué analiza
_Completar: pregunta de análisis, población, período y unidad de análisis._

## Fuentes
_Completar: organismo, relevamiento y link de cada fuente._
Catálogo completo en [`data/README.md`](data/README.md).

## Datos
_Completar: períodos, unidad de análisis y decisiones clave (alcance, período que informa,
imputaciones). El detalle de cada base va en `data/diccionario_<base>.md`._

## Resultados
_Completar: qué hay en `outputs/` y dónde se publica, si aplica._

## Cómo reproducir
```bash
uv run python -m edu_data.<descarga>   # completar: insumos → data/raw/
uv run python -m edu_data.<modulo>     # completar: raw → processed → outputs
uv run pytest
```
Entorno de trabajo: [`docs/entorno.md`](docs/entorno.md).

---
Generado desde [edu-data-template](URL_PLANTILLA) VERSION_PLANTILLA.
proyecto:fin -->
