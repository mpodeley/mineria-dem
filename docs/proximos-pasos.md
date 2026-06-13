# Próximos pasos

## Fase 2.a — Caso público (Veladero) ✅

- [x] Elegir mina y fijar el AOI en `aoi.py` (**Veladero**).
- [x] DEM base (SRTM 2000) + reciente (GLO-30 ~2012) y **además ASTER 2024** vía Ames Stereo Pipeline.
- [x] `dem_diff.py` con co-registro → Δh + volumen (2000→2012 **y** 2000→2024).
- [x] Footprint del pit desde OSM (`overlay_veladero.geojson`).
- [x] Cruce con el material movido declarado por Barrick → 1,0–1,8×.

## Fase 2.b — Caso opaco (Haerwusu, China) ✅

- [x] Replicar en una open-pit china (Haerwusu) y comparar firmas con el caso público.

## Mejoras metodológicas

- **Incertidumbre vertical**: cuantificar el error del DEM sobre zonas estables (fuera del pit) y propagarlo
  al volumen (barra de error en m³) — especialmente para el DEM de ASTER, más ruidoso.
- **Co-registro x-y-z**: hoy se resta solo el *bias* vertical (mediana del terreno estable); sumar
  alineación horizontal + *tilt* (Nuth & Kääb).
- **Serie multi-época**: con varios DEM ASTER intermedios (2005, 2010, 2015, 2020…), estimar la **tasa anual**
  de excavación, no solo el acumulado.
- **DEM reciente para Haerwusu**: aplicar el mismo `aster_dem.sh` al caso chino para llevarlo a 2024.
- **Complemento InSAR**: estabilidad de **taludes y escombreras** (mm/año) reutilizando el pipeline
  Sentinel-1 → HyP3 → MintPy de los repos hermanos.

## Repos hermanos

- [litio-insar](https://mpodeley.github.io/litio-insar/) — subsidencia en salares de litio (InSAR).
- [vaca-muerta-insar](https://mpodeley.github.io/vaca-muerta-insar/) — subsidencia en Vaca Muerta (InSAR).
