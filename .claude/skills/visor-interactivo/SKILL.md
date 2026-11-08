---
name: visor-interactivo
description: Diseñar y generar un visor HTML interactivo (portada, mapa o selector de unidad,
  gráficos on demand) a partir de una base procesada. Usar cuando el usuario pide un visor, un
  tablero, "ver la evolución", un mapa por unidad territorial o mostrar resultados de forma
  interactiva.
---

# Visor interactivo

"On demand" = no se muestra nada que el usuario no haya elegido: primero la unidad, después el
indicador, después los filtros.

## 1. Preguntar antes (una sola tanda, con previews ASCII)
- Unidades: total, cada unidad, totales alternativos ("total sin `<unidad>`" si una alerta de
  una unidad grande mueve el total; ver `validar-calidad`).
- Selector de unidad: **mapa** si la unidad es territorial (default), lista si no.
- Indicadores y, para cada uno, qué cortes tiene en el dataset (sexo, sector, ámbito…). Avisar
  qué cortes **no** existen para un indicador.
- Destino: HTML local en `outputs/` (default) o Pages (skill `publicar`).

## 2. Estructura por defecto
- **Pestaña "Acerca de los datos":** 3–4 párrafos breves: qué es la fuente, qué se puede ver,
  por qué existen los totales alternativos, cómo leer el período (si hay desfase). Termina con
  un botón que lleva a la pestaña del mapa.
- **Pestaña del mapa:** botones para los totales arriba y el mapa neutro (sin coroplético salvo
  pedido). Clic en una unidad → panel.
- **Panel, on demand:**
  1. Primero se elige el indicador. No se muestra nada más hasta elegirlo.
  2. Recién entonces aparecen los filtros que ese indicador admite. Los que no aplican se
     muestran deshabilitados con la nota "El dataset no informa <corte> para este indicador".
  3. Un gráfico de evolución por la dimensión principal (p. ej. nivel).
  4. Debajo, solo la lista de alertas de la selección.
- **Sin tablas debajo del gráfico.** El valor exacto va en el tooltip. Una tabla de detalle solo
  con pedido explícito.
- Categorías derivadas por resta: mostrar todas (Total / una categoría / la otra), con una nota
  de cuál es derivada.
- Corte sin oferta: "Sin oferta para este corte", no ceros. NA = punto vacío o línea cortada.

## 3. Arquitectura
- `src/edu_data/visor_<base>.py`: arma un dict con **todos** los números, precalculados en Python
  y vectorizados (todos los cortes de una vez, no unidad por unidad). NA → `None` con
  `edu_data.visor.a_lista`.
- `src/edu_data/visor_<base>.html`: diseño, con un único marcador `__DATOS__`
  (`<script>const DATOS = __DATOS__;</script>`).
- `edu_data.visor.renderizar(plantilla, datos, destino, marca)`: embebe el JSON escapado y la
  marca `GENERADO por src/edu_data/visor_<base>.py — editar en src/edu_data/visor_<base>.*`.
  Salida autocontenida, rutas relativas, sin CDN si va a Pages.
- Mapa de provincias argentinas: `edu_data.ar.geo.cargar_provincias_svg()` (ya versionado; CABA
  en recuadro). Poner en el pie la atribución de `edu_data/ar/recursos/FUENTE.md`.
- Alertas: `alerta_para(ALERTAS, …)` → anillo en el punto del indicador afectado y texto en el
  tooltip.
- Si está disponible la skill `dataviz`, cargarla para colores, marcas y modo oscuro.
- Medir el tamaño del HTML. Si pasa de ~1 MB, revisar qué datos sobran.

## 4. Verificación
- Tests: cada serie del visor = tabla testeada = cálculo independiente sobre `data/raw/`, en
  varios cortes (incluido uno chico). Las categorías derivadas suman el total.
- Cifras de los textos (portada, alertas): `edu_data.cifras.verificar_cifras`.
- Capturas en desktop y en 375 px de ancho: mapa, tooltip, panel, modo oscuro. Con el navegador
  instalado (`INSTALAR_NAVEGADOR=1`, ver `docs/entorno.md`):
  `uv run --with playwright python <script_de_capturas>.py`, con el script en el scratchpad.
  Para instalarlo en un contenedor ya creado:
  `uv run --with playwright playwright install --with-deps chromium`.
- Si el navegador no está disponible, decirlo y pedir al usuario qué revisar a ojo.

## 5. Entrega
- Decir qué archivo editar (`.py` datos, `.html` diseño) y el comando para regenerar.
- No publicar sin la skill `publicar`.
