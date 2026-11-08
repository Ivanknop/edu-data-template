---
name: validar-calidad
description: Controles de pertinencia de datos educativos y registro de alertas. Usar después
  de construir o actualizar una base procesada, antes de reportar resultados, y cuando el
  usuario pregunte si los datos están bien.
---

# Validar la calidad de los datos

## Controles (`edu_data.validacion_base`, `edu_data.perfil`)
1. **Estructurales** por período: filas, claves vacías o duplicadas, columnas ausentes,
   identidades (`verificar_identidades`).
2. **Saltos interanuales** por unidad y corte: `saltos_interanuales(t, valor, grupo, periodo,
   umbral)`. Umbrales orientativos: stocks (matrícula) ±10 %, flujos (egresos) ±20 %.
3. **Atípicos de la propia serie**: `atipicos_robustos(t, valor, grupo, z=3)` (mediana y MAD por
   grupo). Atrapa oscilaciones de carga y cambios de régimen.
4. **Coherencia entre indicadores relacionados**: `coherencia(t, a, b, grupo, umbral_pct)`, p. ej.
   egresados vs. promovidos del último año, o matrícula t+1 vs. promovidos t.
5. **Patrones de carga**: series que alternan pérdida y ganancia grandes (p. ej. +20 % / −16 %)
   suelen ser problemas de carga, no dinámica real.

## Revisión
- Para cada señal, mirar el detalle: ¿shock real (pandemia, cambio normativo) o problema de carga?
- Distinguir lo que **afecta el total** (unidades grandes o todas a la vez) de lo local.
  Si una sola unidad explica el movimiento del total (p. ej. pesa más del 30 % y tiene un cambio
  normativo), proponer la serie "total sin `<unidad>`" (`edu_data.metricas.sumar_excluyendo`).
- **Materialidad:** si la señal no mueve ninguna cifra mostrada (p. ej. unas decenas de casos
  sobre millones), se informa en una línea en la respuesta y **no** va al registro ni a notas.
- Las señales revisadas que resultan coherentes se documentan en el diccionario como
  "revisadas, sin alerta", para no reabrirlas.
- Cotejos externos (anuarios, otra fuente): proponerlos como opcionales, no como pendientes.

## Correcciones e imputaciones
- No corregir sin pedido. Si se corrige, conservar el original (`<columna>_informado`) y
  documentarlo en el diccionario.
- Imputación masiva de un mismo tipo (muchas columnas con la misma regla, p. ej. un bloque
  entero de "ceros no escritos"): en lugar de una columna `_informado` por columna, alcanza con
  una marca de conteo por bloque (`celdas_<bloque>_imputadas`) que se suma en los agregados.
  La regla y la cantidad de celdas van al diccionario.

## Registro de alertas
Cada alerta revisada se agrega a una lista `ALERTAS` en un único módulo del proyecto
(p. ej. `src/edu_data/alertas.py`):

```python
from edu_data.validacion_base import Alerta

ALERTAS = [
    Alerta(
        periodos=[2021],
        unidades=["X"],
        indicadores=["matricula"],
        texto="Cae 15 % y rebota 27 % al año siguiente: probable problema de carga",
    ),
]
```

- `texto`: una línea en lenguaje llano y con números. **Cada número del texto tiene un test**
  que lo recalcula desde `data/raw/` (`edu_data.cifras.verificar_cifras`). Contar sobre la misma
  medida que se muestra (p. ej. "N de M unidades" sobre el %, no sobre el conteo).
- Un texto que se ve tanto en el total como en una unidad debe leerse bien en los dos casos.
- `unidades=None` aplica a todas; `afecta_total=True` la muestra también en el total.
- `filtros={"sector": "privado"}` restringe a un corte.
- Las visualizaciones consultan `alerta_para(ALERTAS, periodo, indicador, unidades, **filtros)` y
  marcan el punto.

## Reporte
- En la respuesta al usuario: alertas nuevas con datos concretos, ordenadas por impacto. Lo no
  material, en una línea.
- Guardar cada control en `outputs/validacion_<control>.csv`.
