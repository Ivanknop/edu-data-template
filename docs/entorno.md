# Entorno de trabajo

Devcontainer con Python 3.12, uv y Claude Code. No requiere Python instalado en la máquina:
solo Docker.

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

## Uso
1. Abrir la carpeta del proyecto en VS Code.
2. `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**. La primera vez tarda unos minutos.
3. En la terminal del contenedor: `claude` y loguearse (una sola vez por máquina: la sesión
   queda guardada en el volumen `edu-data-claude-config`).

## Qué incluye
- Python 3.12 + uv, con pandas, polars, duckdb, pyreadstat (SPSS/Stata), geopandas,
  statsmodels, plotly, etc.
- Claude Code (CLI + extensión de VS Code) con un `CLAUDE.md` que fija convenciones de datos
  y rigor estadístico.
- Skills de Claude en `.claude/skills/`: `dataset-nuevo`, `validar-calidad`,
  `visor-interactivo`, `auditar`, `publicar` y `actualizar-plantilla`.
- Paquete `edu_data` con funciones genéricas y tests (`uv run pytest`):
  - `io`: detectar formato, leer CSV oficiales (vacío ≠ 0, códigos como texto), unificar
    esquemas entre períodos, leer hojas de Excel.
  - `descarga`: bajar insumos a `data/raw/` con reintentos, sin pisar archivos.
  - `series`: archivos por período, lectura en paralelo, ancho → largo.
  - `perfil`: perfil por columna, identidades, vacíos frente al denominador, cruce con el
    diccionario, búsqueda de shocks.
  - `metricas`: porcentajes y sumas que respetan "vacío no es cero", totales sin una unidad.
  - `cifras`: formato es-AR y verificación de cifras en textos.
  - `validacion_base`: saltos interanuales, atípicos robustos, coherencia y alertas.
  - `visor`: plantilla HTML + datos en JSON + marca GENERADO.
  - `ar`: provincias (nombres y códigos), primaria de 6 o 7 años, mapa SVG de provincias,
    links de datos abiertos de la Secretaría de Educación.
- Plantillas de documentación: catálogo `data/README.md` y `data/_plantilla_diccionario.md`.
- Workflow de ejemplo para GitHub Pages: `.github/workflows/publicar.yml.ejemplo`.
- Permisos de Claude que impiden editar archivos de `data/raw/`. Es un recordatorio, no una
  garantía: un script o comando de shell igual puede escribir ahí.

## Comandos frecuentes
```bash
uv add <paquete>          # agregar dependencia (actualiza pyproject.toml y uv.lock)
uv run python -m edu_data.<modulo>   # correr un módulo del proyecto
uv run pytest
uv run ruff check . && uv run ruff format .
```

## Navegador para verificar visores (opcional)
Claude puede revisar los visores con capturas si hay un Chromium sin interfaz. Pesa unos
300 MB y por defecto no se instala.
- Al crear el contenedor: definir `INSTALAR_NAVEGADOR=1` en el host antes de abrir VS Code y
  hacer **Rebuild Container**. `post-create.sh` corre la instalación.
<!-- so:linux:inicio -->
  En el shell desde el que se lanza VS Code: `export INSTALAR_NAVEGADOR=1 && code .`
<!-- so:linux:fin -->
<!-- so:windows:inicio -->
  - Proyecto dentro de WSL2: en la terminal de WSL, `export INSTALAR_NAVEGADOR=1 && code .`
  - Proyecto en el disco de Windows: en PowerShell, `setx INSTALAR_NAVEGADOR 1`, y cerrar y
    volver a abrir VS Code para que tome la variable.
<!-- so:windows:fin -->
- En un contenedor ya creado:
  `uv run --with playwright playwright install --with-deps chromium`.

## Red corporativa
- Proxy: no se configura en el proyecto. Docker lo inyecta en el build y en el contenedor
  desde `~/.docker/config.json` del host.
- Certificados (inspección SSL): copiar los `.crt` a `.devcontainer/certs/` y reconstruir el
  contenedor. No se versionan.
