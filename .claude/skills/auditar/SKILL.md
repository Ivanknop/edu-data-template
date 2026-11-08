---
name: auditar
description: Revisión integral de datos y código de un proyecto (recálculo independiente,
  cifras de textos, duplicación, performance). Usar cuando el usuario pide auditar, una
  "revisión integral", "revisar todo" o antes de una entrega o publicación importante.
---

# Auditoría de datos y código

Solo lectura: se informa y se propone. Se corrige después de que el usuario elige qué.

## 1. Datos
1. **Recálculo independiente.** Recalcular los totales principales con otro motor (DuckDB desde
   Python, leyendo los archivos de `data/raw/` directamente), sin pasar por el lector del
   proyecto. Comparar contra `data/processed/` y contra las series del visor: diferencias = 0.
2. **Identidades.** Correr todas las del diccionario: partes = total, subconjunto ≤ total,
   coherencias lógicas entre indicadores.
3. **Imputaciones.** Verificar que solo se aplicaron donde correspondía, con el valor decidido,
   y que el conteo de celdas imputadas coincide con el diccionario.
4. **Rangos.** Porcentajes en 0–100, sin NaN en lo que se muestra, proporciones plausibles.
5. **Cifras en textos.** Listar cada número escrito (alertas, portada, README) y si tiene test.
6. **Señales sin revisar.** Correr `validar-calidad` y listar lo que no está ni en el registro ni
   en "revisadas, sin alerta".

## 2. Código
- Duplicación (dos caminos para el mismo cálculo), nombres engañosos, trucos frágiles.
- Performance: medir la construcción completa y los tests (`time`). Buscar lecturas repetidas,
  bucles por unidad que se pueden vectorizar, DataFrames armados columna a columna, agregados
  calculados desde la base más grande.
- Reproducibilidad: ¿un solo comando raw → outputs? ¿descarga por script? ¿tests sin
  `data/processed/`?
- Ruff, tests, marca GENERADO en todo lo de `outputs/`.

## 3. Reporte
- Primero el veredicto: ¿hay errores de cálculo? Después, una lista numerada:
  - errores (con la cifra correcta);
  - riesgos;
  - deuda técnica;
  - mejoras de performance, con una estimación.
- Aplicar la **materialidad**: lo despreciable va en una línea, sin proponer notas.
- Cotejos externos (anuarios, otras fuentes) como opcionales.
- Cerrar preguntando qué se corrige. Después de corregir: resultados idénticos valor por valor
  (salvo los cambios buscados) y tiempos antes/después.
