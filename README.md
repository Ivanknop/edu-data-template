# edu-data-claude

Entorno reproducible (devcontainer) para analizar datasets educativos con Python y Claude Code.
No requiere Python instalado en la máquina: solo Docker.

## Requisitos
- Docker Desktop (Windows/macOS) o Docker Engine (Linux). En Windows, con backend WSL2.
- VS Code con la extensión **Dev Containers** (`ms-vscode-remote.remote-containers`).

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

## Comandos frecuentes
```bash
uv add <paquete>          # agregar dependencia (actualiza pyproject.toml y uv.lock)
uv run python script.py   # correr un script
uv run jupyter lab --ip 0.0.0.0 --no-browser   # o abrir .ipynb directo en VS Code
uv run ruff check . && uv run ruff format .
```

Commitear `uv.lock` (se genera en el primer `uv sync`): garantiza las mismas versiones en ambas PCs.

## Red corporativa
- **Proxy**: si la PC define `HTTP_PROXY`/`HTTPS_PROXY`, Docker los usa en el build. Para
  el contenedor en ejecución, configuralos en Docker Desktop → Settings → Resources → Proxies.
- **Inspección SSL**: copiar el certificado raíz (`.crt`, PEM) en `.devcontainer/certs/` y
  hacer *Rebuild Container*. No se sube a git.

## Problemas comunes
- `bad interpreter: /bin/bash^M` → el `.sh` quedó con CRLF. El `.gitattributes` lo evita;
  si ya clonaste antes: `git rm --cached -r . && git reset --hard`.
- Claude pide login de nuevo → se borró el volumen (`docker volume ls | grep edu-data`).
