# Referencias

## DEM-differencing y volumen en minería

- **Geomorphic change detection (DoD)** — el marco estándar de *DEM of Difference* para cuantificar erosión,
  depósito y excavación con incertidumbre. Ver Wheaton et al. (2010), *ESPL*.
- **Ames Stereo Pipeline (ASP)** — NASA, generación de DEM a partir de estéreo óptico satelital.
  [github.com/NeoGeographyToolkit/StereoPipeline](https://github.com/NeoGeographyToolkit/StereoPipeline)
- **Co-registro de DEM** — Nuth & Kääb (2011), *The Cryosphere*: alineación sobre terreno estable antes de
  restar (corrige sesgo y *tilt*); base de la mayoría de los flujos de change detection.

## DEMs

- **Copernicus DEM GLO-30** (~2011–2015, 30 m) — ESA, vía [OpenTopography](https://opentopography.org) / AWS.
- **NASADEM** (SRTM reprocesado, 2000, 30 m) y **ALOS World 3D AW3D30** (~2006–2011, 30 m) — bases alternativas.
- **Estéreo comercial** (Maxar, Pléiades, PlanetScope/SkySat) — DEM recientes de alta resolución (de pago).

## Datos satelitales y software

- **Sentinel-2** (ESA Copernicus) — geometría del pit / digitalización del polígono.
- **GDAL / rasterio / numpy** — reproyección, resta e integración de volumen.

## Operación y producción

- **Caso público**: reportes anuales y *technical reports* (NI 43-101) de Codelco / BHP / Barrick —
  material movido, *strip ratio*, toneladas de mineral.
- **Caso opaco (China)**: cobertura de prensa/empresas (cifras agregadas, sin material movido por sitio).

## Repos hermanos

- [litio-insar](https://github.com/mpodeley/litio-insar) · [vaca-muerta-insar](https://github.com/mpodeley/vaca-muerta-insar)

---

!!! note
    A diferencia de los repos hermanos (InSAR), acá la técnica central es **DEM-differencing**. El InSAR solo
    aplica como complemento para deformación lenta de taludes/escombreras, no para el volumen excavado.
