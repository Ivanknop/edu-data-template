# edu-data-template

Entorno reproducible (devcontainer) para analizar datasets con Python y Claude Code.
No requiere Python instalado en la máquina: solo Docker.

## Requisitos
- Linux con Docker Engine.
- VS Code con la extensión **Dev Containers** (`ms-vscode-remote.remote-containers`).

## Usar como plantilla
1. En GitHub: **Use this template** → **Create a new repository**.
2. En el repo nuevo, quitar `uv.lock` del `.gitignore` y commitearlo después del primer `uv sync`.

## Uso
1. Clonar el repo y abrirlo en VS Code.
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

