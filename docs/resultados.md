# Resultados

El producto principal es el **mapa de cambio de elevación (Δh)** entre dos fechas y el **volumen** integrado
sobre el pit.

!!! warning "Resultados pendientes de los DEM"
    El pipeline está listo, pero el mapa de abajo es un **placeholder** hasta conseguir los dos DEM y correr
    `pipeline/dem_diff.py` (ver [Método](metodo.md)). El paso bloqueante es obtener un **DEM reciente** de
    calidad (la base gratuita ya existe).

## Cambio de elevación (Δh) sobre el pit

<iframe src="../assets/demo_volumen.html" width="100%" height="540" style="border:1px solid #ccc;border-radius:6px"></iframe>

*Rojo = terreno que bajó (excavado), azul = terreno que subió (depositado). Δh en metros, sobre imagen
satelital.*

## Qué reportará el cálculo

| Métrica | Qué |
|---|---|
| Volumen **excavado** | Σ del descenso de elevación × área de celda (m³ / Mm³) |
| Volumen **depositado** | Σ del ascenso (escombreras / relaves) |
| Volumen **neto** | depositado − excavado |
| Período | `EPOCH_BASE → EPOCH_NEW` (fechas reales de cada DEM) |

## Qué buscamos confirmar

1. **Δh coherente** con la geometría del pit (descenso concentrado en el hueco, ascenso en las escombreras).
2. **Orden de magnitud** del volumen excavado comparable al **material movido declarado** por la empresa
   (ver [caso público](caso-publico.md)).
3. **Incertidumbre acotada**: el ruido vertical del DEM (±2–4 m en los globales) integrado sobre el área no
   debe dominar la señal.
