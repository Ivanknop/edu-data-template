# edu-data-template

Entorno reproducible (devcontainer) para analizar datasets con Python y Claude Code.
No requiere Python instalado en la máquina: solo Docker.

## Requisitos
- Linux con Docker Engine.
- Windows con Docker Desktop (backend WSL2).
- Recomendado: tener el proyecto dentro de WSL2 (`~/proyectos/...` en Ubuntu) y abrirlo con VS Code vía WSL.
  En el disco de Windows (`C:\...`) funciona, pero el acceso a archivos desde el contenedor es lento.
- VS Code con la extensión **Dev Containers** (`ms-vscode-remote.remote-containers`).

## Crear un proyecto nuevo
Esta plantilla no se usa para trabajar: se usa para generar proyectos.

```bash
scripts/nuevo_proyecto.sh -name ~/proyectos/mi-analisis -so linux     # o -so windows
```
En Windows, correrlo desde WSL2 o Git Bash.
Genera el directorio con todo lo necesario. El versionado (`git init`, remote, commits) queda a cargo de cada proyecto.

## Uso
1. Abrir la carpeta del proyecto en VS Code.
2. `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**. La primera vez tarda unos minutos.
3. En la terminal del contenedor: `claude` y loguearse (una sola vez por máquina: la sesión
   queda guardada en el volumen `edu-data-claude-config`).

## Qué incluye
- Python 3.12 + uv, con pandas, polars, duckdb, pyreadstat (SPSS/Stata), geopandas, statsmodels, Jupyter, etc.
- Claude Code (CLI + extensión de VS Code) con un `CLAUDE.md` que fija convenciones de datos
  y rigor estadístico (ponderadores, valores plausibles).
- Permisos de Claude que impiden modificar `data/raw/`.
  Es un recordatorio, no una garantía: un script o comando de shell igual puede escribir ahí.

## Comandos frecuentes
```bash
uv add <paquete>          # agregar dependencia (actualiza pyproject.toml y uv.lock)
uv run python script.py   # correr un script
uv run jupyter lab --ip 0.0.0.0 --no-browser   # o abrir .ipynb directo en VS Code
uv run ruff check . && uv run ruff format .
```

