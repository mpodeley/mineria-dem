# Caso opaco (China)

Aplicar el **mismo DEM-differencing** a una open-pit donde **no hay datos operativos públicos**. Ahí el
volumen estimado por satélite es la única medida independiente del ritmo de extracción.

## Candidatos

| Mina | Tipo | Ubicación | Notas |
|---|---|---|---|
| **Carbón a cielo abierto** | carbón | Mongolia Interior (p. ej. cuenca de Shengli/Xilinhot) | Open-pits gigantes, expansión rápida, reporte operativo opaco. |
| **Bayan Obo** | hierro / tierras raras | Mongolia Interior | Complejo estratégico; datos de producción muy poco transparentes. |

## Cómo se adapta el método

- **Pipeline idéntico**: solo cambian el bbox y las épocas en `aoi.py`. `dem_diff.py` es agnóstico al lugar.
- **DEM base gratis** (Copernicus GLO-30) + **DEM reciente** (estéreo óptico comercial o, si alcanza, ALOS).
- **Sin producción declarada**: el análisis recae en el **volumen medido** y en la **expansión del pit** vista
  en óptico (Sentinel-2) a lo largo del tiempo.

## Estado

!!! warning "Fase 2 — arranca después del caso público"
    - [ ] Elegir mina y AOI.
    - [ ] Conseguir los dos DEM y correr `dem_diff.py`.
    - [ ] Comparar magnitud/evolución del volumen con el caso público.
