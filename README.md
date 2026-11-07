# edu-data-template

<!-- plantilla:inicio -->
Entorno reproducible (devcontainer) para analizar datasets con Python y Claude Code.
No requiere Python instalado en la máquina: solo Docker.
<!-- plantilla:fin -->

<!-- proyecto:inicio
> Proyecto generado con [edu-data-template](https://github.com/Ivanknop/edu-data-template).

## Qué analiza
_Completar: pregunta de análisis, población, período y unidad de análisis._

## Fuentes
Catálogo y diccionarios en [`data/README.md`](data/README.md).
Los datos crudos no se versionan: indicar ahí cómo descargarlos a `data/raw/`.

## Cómo reproducir
```bash
uv run python -m edu_data.<modulo>   # completar: raw → processed → outputs
uv run pytest
```

## Resultados
_Completar: qué hay en `outputs/` y dónde se publica, si aplica._
proyecto:fin -->

## Requisitos
<!-- so:linux:inicio -->
- Linux con Docker Engine.
<!-- so:linux:fin -->
<!-- so:windows:inicio -->
- Windows con Docker Desktop (backend WSL2).
- Recomendado: tener el proyecto dentro de WSL2 (`~/proyectos/...` en Ubuntu) y abrirlo con
  VS Code vía WSL. En el disco de Windows (`C:\...`) funciona, pero el acceso a archivos desde
  el contenedor es lento.
<!-- so:windows:fin -->
- VS Code con la extensión **Dev Containers** (`ms-vscode-remote.remote-containers`).

<!-- plantilla:inicio -->
## Crear un proyecto nuevo
Esta plantilla no se usa para trabajar: se usa para generar proyectos.

```bash
scripts/nuevo_proyecto.sh -name ~/proyectos/mi-analisis -so linux     # o -so windows
```
En Windows, correrlo desde WSL2 o Git Bash.
Genera el directorio con todo lo necesario: nombre del proyecto en `pyproject.toml` y en el
devcontainer, y un README propio con secciones a completar.
El versionado (`git init`, remote, commits) queda a cargo de cada proyecto.
<!-- plantilla:fin -->

## Uso
1. Abrir la carpeta del proyecto en VS Code.
2. `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**. La primera vez tarda unos minutos.
3. En la terminal del contenedor: `claude` y loguearse (una sola vez por máquina: la sesión
   queda guardada en el volumen `edu-data-claude-config`).

## Qué incluye
- Python 3.12 + uv, con pandas, polars, duckdb, pyreadstat (SPSS/Stata), geopandas,
  statsmodels, Jupyter, etc.
- Claude Code (CLI + extensión de VS Code) con un `CLAUDE.md` que fija convenciones de datos
  y rigor estadístico (ponderadores, valores plausibles).
- Skills de Claude en `.claude/skills/`: `dataset-nuevo` (incorporar y documentar un dataset),
  `validar-calidad` (controles y registro de alertas) y `publicar` (GitHub Pages).
- Paquete `edu_data` con funciones genéricas y tests (`uv run pytest`):
  - `io`: detectar formato, leer CSV oficiales (vacío ≠ 0, códigos como texto), unificar
    esquemas entre períodos, leer hojas de Excel.
  - `perfil`: perfil por columna y verificación de identidades contables.
  - `validacion_base`: saltos interanuales, atípicos robustos, coherencia y alertas.
- Plantillas de documentación: catálogo `data/README.md` y `data/_plantilla_diccionario.md`.
- Workflow de ejemplo para GitHub Pages: `.github/workflows/publicar.yml.ejemplo`.
- Permisos de Claude que impiden modificar `data/raw/`.
  Es un recordatorio, no una garantía: un script o comando de shell igual puede escribir ahí.

## Comandos frecuentes
```bash
uv add <paquete>          # agregar dependencia (actualiza pyproject.toml y uv.lock)
uv run python script.py   # correr un script
uv run jupyter lab --ip 0.0.0.0 --no-browser   # o abrir .ipynb directo en VS Code
uv run ruff check . && uv run ruff format .
```
