---
name: dataset-nuevo
description: Procedimiento para incorporar un dataset educativo nuevo (CSV o Excel oficiales).
  Usar cuando aparece un archivo nuevo en data/raw/, hay que descargar una base, o el usuario
  pide revisar, describir o perfilar un dataset.
---

# Incorporar un dataset nuevo

Objetivo: entender el dataset y dejarlo documentado y leíble de forma reproducible.
Todavía no se analiza ni se grafica.

## 0. Descarga reproducible
- Toda descarga va en un script de `src/edu_data/` desde el primer archivo: datos,
  diccionarios, documentos metodológicos y geometrías. Usar `edu_data.descarga.descargar`
  (reintentos, nunca pisa un archivo existente).
- No copiar a `data/raw/` con `cp` ni dejar insumos en carpetas temporales.
- Si la página arma los links desde otra fuente (una planilla, un almacenamiento que pide
  cookie), documentar en el docstring cómo se encontraron y la fecha en que estaban vigentes.
- Datos abiertos de la Secretaría de Educación (Argentina): `edu_data.ar.datos_abiertos_educacion`.

## 1. Inventario
- Listar `data/raw/` con tamaño y fecha. Agrupar por serie (mismo nombre, distinto período):
  `edu_data.series.archivos_por_periodo`.
- Por archivo: `file <archivo>` y `edu_data.io.detectar_formato(ruta)` (encoding, separador,
  CRLF, encabezado). No asumir UTF-8.
- Excel: `edu_data.io.listar_hojas(ruta)` y revisar cada hoja (los diccionarios oficiales
  suelen traer una pestaña por base). Leer con `leer_hoja(ruta, hoja)`.

## 2. Esquema entre períodos
- `edu_data.io.diff_columnas({periodo: df, ...})`: columnas que aparecen, desaparecen o cambian
  de mayúsculas. `leer_csv_oficial` ya pasa los nombres a minúsculas.
- Detectar patrones de nombre (prefijos de sexo, sufijos de grado o año, bloques). Escribirlos
  como constantes o regex, no como listas a mano. Atención a sufijos o bloques nuevos en un
  período: suelen ser un cambio de definición, no solo una columna más.
- `edu_data.io.unificar_esquema(dfs)`: ausentes → NA, registradas en `attrs`.
- Ancho → largo por bloques: `edu_data.series.ancho_a_largo`. Varios archivos:
  `edu_data.series.leer_en_paralelo`.

## 3. Lectura reproducible
- Escribir el lector en `src/edu_data/<base>.py` usando `edu_data.io.leer_csv_oficial`
  (`claves=` para las claves sin ceros a la izquierda; `decimal=","` si corresponde).
- Revisar `df.attrs["columnas_texto_por_ceros"]`: confirmar que son códigos y no números.
- Buscar errores de encoding de origen en los textos (caracteres raros repetidos) y corregirlos
  en el lector, con un comentario.

## 4. Vacíos y ceros
- `edu_data.perfil.perfil_columnas(df)`: vacíos y ceros por columna.
- `edu_data.perfil.vacios_con_denominador(df, pares)`: para cada columna, cuántos vacíos caen
  donde su denominador (total del grupo, matrícula del grado) existe.
- Lectura:
  - Vacíos solo donde el denominador también falta → "no aplica / sin oferta": NA.
  - Columna sin ningún 0 y con vacíos donde el denominador existe → probable **cero no
    escrito**. Proponer imputar a 0 con la evidencia (cantidad de celdas, peso sobre el total).
    Decide el usuario.
  - Vacíos dispersos con denominador y con ceros presentes en la columna → dato perdido: NA.
- Documentar la decisión en el diccionario. Si se imputa: original conservado y conteo de
  celdas imputadas (ver `validar-calidad`).

## 5. Unidad de análisis y claves
- ¿Fila = estudiante, escuela, sección, agregado? Verificar la unicidad de la clave.
- Revisar los valores de las dimensiones: totales mezclados con detalle, "sin datos", unidades
  enmascaradas o fusionadas por secreto estadístico (sirven para totales, no para el detalle).
- Categorías informadas en parte (un solo sexo, un solo sector): las demás se derivan por resta
  y se muestran todas, marcando cuál es derivada.
- ¿Ponderadores, valores plausibles o pesos replicados? Aplicar las reglas de CLAUDE.md.
- Si la unidad es una provincia argentina: `edu_data.ar.provincias` (nombres y códigos) y
  `edu_data.ar.niveles` (primaria de 6 o 7 años) en lugar de inferirlos de los datos.

## 6. Identidades contables
- Buscar relaciones que deberían cerrar: total = suma de partes, flujos (inicial + entradas −
  salidas = final), subconjunto ≤ total.
- Buscar equivalencias entre indicadores que sirvan para validar (p. ej. egreso de un nivel
  frente a los promovidos de su último año).
- `edu_data.perfil.verificar_identidades(df, reglas)` en todos los períodos. Informar
  `attrs["resumen"]`: las filas `no_evaluable` (con NA) se reportan aparte de las que fallan.
- Si cierran, decirlo: da confianza. Si no, listar las filas que fallan.

## 7. Período de referencia
- Buscar al menos un shock con fecha conocida (pandemia 2020, un cambio normativo citado por el
  usuario, un cambio de estructura): `edu_data.perfil.buscar_shock(t, valor, esperado, ...)`.
- ¿En qué archivo aparece?
  - En el del mismo año → sin desfase.
  - En el del año siguiente → la hipótesis por defecto es que **todo el archivo** informa el
    año anterior. No desfasar por variable sin evidencia específica.
- Si la documentación oficial dice otra cosa, mostrar las dos evidencias y **preguntar en la
  primera respuesta**, como pregunta separada y visible.
- Codificar `DESFASE_PERIODO` con la evidencia en el comentario. La columna de año del pipeline
  es el período; `anio_archivo` se conserva aparte. Visores y textos muestran el período.

## 8. Diccionario
- `edu_data.perfil.cruzar_diccionario(df, dicc)`: variables sin definición y definiciones sin
  variable.
- Controlar que cada descripción coincida con el prefijo y el perfil de la variable (p. ej. dos
  descripciones intercambiadas entre variables vecinas).
- Pedir al usuario lo que falte en la **primera** respuesta, no al final.
- Al proponer alcance, cada código con glosa llana y tamaño: "`<código>` (<qué es en lenguaje
  llano>), ~<n> casos, <qué indicadores trae>".
- Las decisiones del usuario van a la sección "Decisiones" del diccionario, no a la memoria.

## 9. Documentación
- `data/README.md`: fuente, URL, fecha de descarga, período que informa, unidad, encoding,
  ponderador, notas.
- `data/diccionario_<base>.md` a partir de `data/_plantilla_diccionario.md`.

## 10. Entrega
- Resumen corto: qué es, unidad, períodos, calidad (identidades, vacíos), preguntas abiertas.
- No generar gráficos en este paso. Seguir con la skill `validar-calidad` si se va a analizar.
