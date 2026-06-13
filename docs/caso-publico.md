# Caso público (Chile / Argentina)

El caso **público**: una open-pit operada por una empresa que **reporta producción**, para contrastar el
volumen excavado estimado por DEM-diff contra el **material movido declarado**.

## Candidatos

| Mina | Operador | País | Por qué |
|---|---|---|---|
| **Chuquicamata** | Codelco | Chile | Open-pit icónica, enorme, datos de Codelco públicos (en transición a subterránea). |
| **Escondida** | BHP | Chile | Mayor mina de cobre del mundo; BHP cotiza y reporta material movido. |
| **Veladero** | Barrick / Shandong | Argentina (San Juan) | Oro a cielo abierto; reportes de producción públicos. |

*Placeholder por defecto en `aoi.py`: Chuquicamata. Elegir y refinar el bbox contra imagen satelital.*

## Datos públicos a cruzar

- **Material movido / *strip ratio*** y **toneladas de mineral** de los reportes anuales y *technical reports*
  (NI 43-101 / informes de la empresa). Convertir toneladas → volumen con la densidad de roca (~2.6–2.7 t/m³)
  para comparar con el Δh integrado.
- **Geometría del pit** desde Sentinel-2 / imágenes históricas para `pipeline/overlay.geojson`.

## Estado

!!! warning "Pendiente"
    - [ ] Elegir la mina y fijar el AOI en `aoi.py`.
    - [ ] Conseguir DEM base (Copernicus GLO-30) y un DEM reciente (estéreo/lidar).
    - [ ] Correr `dem_diff.py` y publicar Δh + volumen ([Resultados](resultados.md)).
    - [ ] Digitalizar el polígono del pit → `overlay.geojson`.
    - [ ] Cruzar volumen estimado vs material movido declarado.
