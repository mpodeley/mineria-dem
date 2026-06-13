# Próximos pasos

## Fase 2.a — Caso público (Chile/AR)

- [ ] Elegir mina (Chuquicamata / Escondida / Veladero) y fijar el AOI en `aoi.py`.
- [ ] Conseguir **DEM base** (Copernicus GLO-30 vía OpenTopography) y **DEM reciente** (estéreo óptico con
  Ames Stereo Pipeline, o lidar/dron si está disponible).
- [ ] Correr `dem_diff.py` → Δh + volumen excavado/depositado.
- [ ] Digitalizar el polígono del pit → `pipeline/overlay.geojson`.
- [ ] Cruzar el volumen estimado con el **material movido declarado** (toneladas × densidad).

## Fase 2.b — Caso opaco (China)

- [ ] Replicar en una open-pit china y comparar con el caso público.

## Mejoras metodológicas

- **Incertidumbre vertical**: cuantificar el error del DEM sobre zonas estables (fuera del pit) y propagarlo
  al volumen (barra de error en m³).
- **Co-registro**: alinear los DEM sobre terreno estable antes de restar (corrige *bias* y *tilt*).
- **Serie multi-época**: con varios DEM intermedios, estimar la **tasa anual** de excavación.
- **Complemento InSAR**: estabilidad de **taludes y escombreras** (mm/año) reutilizando el pipeline
  Sentinel-1 → HyP3 → MintPy de los repos hermanos.

## Repos hermanos

- [litio-insar](https://mpodeley.github.io/litio-insar/) — subsidencia en salares de litio (InSAR).
- [vaca-muerta-insar](https://mpodeley.github.io/vaca-muerta-insar/) — subsidencia en Vaca Muerta (InSAR).
