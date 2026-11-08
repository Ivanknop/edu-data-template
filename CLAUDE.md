# Proyecto: análisis de datasets educativos

## Forma de trabajo
- Por defecto, plan primero (explorar, preguntar, proponer). No se escribe ni modifica código
  hasta que el desarrollador lo pida explícitamente.
- Al pedir autorización, mostrar en el mismo mensaje el plan por etapas (archivos, tests,
  comando de construcción). Nunca cerrar con "¿arranco?" sin plan.
- No se hacen commits ni push sin autorización explícita.
- Ante rediseños o pedidos ambiguos, preguntar antes: alcance, formato, ejes, cortes, medida.
- En preguntas y propuestas, ningún código crudo sin glosa: nombre llano + tamaño o peso.
- Las decisiones sobre los datos (alcance, imputaciones, desfases, exclusiones) se escriben en
  `data/diccionario_<base>.md`, no en la memoria de Claude: la memoria no está en el repo
  (no viaja a otra PC, no se versiona, nadie más la ve).
- La performance importa: leer en paralelo, armar DataFrames de una vez, derivar agregados de
  la base más chica posible, fixtures de sesión. Medir antes y después (`time`).
- Actualizar a una versión nueva de la plantilla: skill `actualizar-plantilla`.

## Entorno y estructura
- Devcontainer con Python 3.12 y **uv** (venv en `/home/vscode/.venv`; ver `docs/entorno.md`).
  Ejecutar con `uv run python ...` / `uv run pytest`. Paquetes: `uv add`, nunca `pip install`.
- `data/raw/` — insumos originales (datos, diccionarios, documentos). **No se modifican.**
  Entran solo por un script de descarga en `src/` que nunca pisa (`edu_data.descarga`).
  Por defecto no se versionan; si `publicar` decide versionar, anotar acá qué y por qué.
- `data/processed/` — derivados (preferir Parquet). No se versionan.
- `src/edu_data/` — código (carga, limpieza, métricas, visores). `edu_data.ar`: referencias
  argentinas (provincias, niveles, mapa, datos abiertos de educación).
- `outputs/` — resultados finales, regenerables.

## Datos
- Dataset nuevo: skill `dataset-nuevo` (descarga, vacíos, período, diccionario) y catálogo en
  `data/README.md`. Si el diccionario no cubre todas las variables, pedirlo en la 1.ª respuesta.
- Todo paso raw → processed es un script en `src/` que regenera desde `data/raw/`.
- Archivos grandes: DuckDB o Polars. Encoding y separador se detectan, no se suponen.
  Códigos territoriales o institucionales: texto (conservar ceros a la izquierda).
- Período: separar "año del archivo" de "período que informa"; verificar con un shock conocido
  y decidirlo con el usuario en la primera respuesta (`dataset-nuevo` §7).
- Vacío no es cero: "no aplica / sin oferta" queda NA de punta a punta (gráficos: punto vacío).
  Un "cero no escrito" se imputa a 0 solo con decisión del usuario (`dataset-nuevo` §4).
- Categorías derivadas por resta: se calculan y se muestran **todas**, aclarando cuál se deriva.

## Rigor estadístico
- Con **ponderadores**, usarlos en toda estimación poblacional y aclararlo.
- **Valores plausibles** y **pesos replicados**: estimar con todos y combinar, nunca uno solo.
- No mezclar unidades de análisis. Reportar n, faltantes y su tratamiento.
- Verificar las identidades contables del dataset (total = partes, flujos que cierran).

## Calidad de datos
- Todo análisis corre la skill `validar-calidad` y reporta en la respuesta lo que parezca mal.
- Materialidad: todo hallazgo se informa; al registro y a los gráficos, solo si mueve una cifra.
- Alertas en un único registro; las visualizaciones las marcan. No se ocultan ni corrigen en
  silencio. Si se corrige, se conserva el original y se documenta (`validar-calidad`).

## Análisis y visualización
- De lo general a lo particular: primero el total y la evolución; los cortes, a pedido.
- Sin lotes de gráficos sin pedido. Visores: skill `visor-interactivo`.
- Métricas derivadas (brechas, índices) se proponen con un ejemplo de lectura antes.
- Cada número mostrado tiene un test, también los escritos en textos (alertas, portadas,
  README). Redondear una sola vez, al mostrar (`edu_data.cifras`).
- `outputs/` no se edita a mano: marca `GENERADO por <script> — editar en <origen>`.
- Revisión integral de datos y código: skill `auditar`.

## Tests y publicación
- Los tests parten de `data/raw/`, nunca de `data/processed/` ni `outputs/` (en la CI corren antes).
- Sin crudos: skip en local, fail en CI (fixture `requiere_crudos` de `tests/conftest.py`).
- Antes de publicar: visibilidad del repo y destino (Pages, artifact, nada). Skill `publicar`.

## Estilo
- Español está bien; funciones en snake_case. Comentar solo reglas de negocio o parámetros.
- Comentarios y docstrings ≤ 100 caracteres por línea; más de 150 en total va a `data/*.md`.
  Lint y formato: `uv run ruff check . && uv run ruff format .`
