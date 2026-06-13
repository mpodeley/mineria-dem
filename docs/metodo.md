# Método paso a paso

Todo el procesamiento usa **software libre**. El pipeline está en
[`docs/pipeline/`](https://github.com/mpodeley/mineria-insar/tree/main/docs/pipeline) y, a diferencia de
los repos hermanos, **no** usa la cadena InSAR (HyP3/MintPy): solo manejo de rasters.

## Qué es DEM-differencing (en una línea)

Un **DEM** (modelo digital de elevación) da la altura del terreno celda por celda. Restando el DEM de una
fecha **reciente** menos el de una fecha **base** se obtiene **Δh** (cuánto subió o bajó el terreno). En una
open-pit, donde Δh es muy negativo se **excavó**; donde es positivo se **depositó** (escombreras, relaves).
Integrando Δh por el área de cada celda → **volumen en m³**.

## 0. Datos y herramientas

| Pieza | Qué | Fuente |
|---|---|---|
| DEM base | elevación de la época inicial | **Copernicus GLO-30** (~2011–2015), NASADEM (2000), AW3D30 |
| DEM reciente | elevación actual | **estéreo óptico** (Maxar/Pléiades/PlanetScope), **lidar**, o ALOS reciente |
| Resta + volumen | grilla UTM común, integración | `rasterio`, `numpy` (`dem_diff.py`) |
| Polígono del pit | acotar el cálculo | digitalización óptica (Sentinel-2 / OSM) → `overlay.geojson` |

!!! danger "El cuello de botella: la base temporal de los DEM gratuitos"
    Los DEM **gratuitos** (Copernicus GLO-30, NASADEM, AW3D30) son de hace **10–25 años**. Sirven como
    **base** antigua, pero para el **DEM reciente** casi siempre hace falta una fuente **comercial**
    (estéreo Maxar/Pléiades, ~$/km²) o **lidar/dron** del operador. La validez del volumen depende de
    documentar **las fechas reales** de cada DEM (`aoi.EPOCH_BASE`, `aoi.EPOCH_NEW`) y de su **incertidumbre
    vertical** (típicamente ±2–4 m para los globales → ruido que se integra sobre el área).

## 1. Área y época

`aoi.py` define el bounding box de la mina, el punto del pit y las dos épocas a comparar. El caso público es
**Veladero** (Barrick/Shandong, San Juan); refinar el bbox contra la imagen satelital.

## 2. Conseguir los DEM

La estrategia **gratuita** clave: si la mina arrancó **después de 2000**, comparamos dos DEM públicos de
épocas distintas — el SRTM capta el terreno prístino y el GLO-30 el pit ya excavado.

- **Base (2000)**: **SRTM** 1 arcsec, vía el endpoint *skadi* de `elevation-tiles-prod` (AWS, **sin auth**).
- **Reciente (~2012)**: **Copernicus GLO-30**, vía el bucket público `copernicus-dem-30m` (AWS, **sin auth**).
- **Para extender a hoy**: un DEM reciente de estéreo óptico ([Ames Stereo Pipeline](https://github.com/NeoGeographyToolkit/StereoPipeline)
  sobre Maxar/Pléiades/PlanetScope) o lidar/dron — normalmente de pago.

```bash
python pipeline/fetch_dems.py    # baja y recorta al AOI → dems/base_2000.tif, dems/new_2012.tif
```

## 3. Footprint del pit (opcional pero recomendado)

```bash
python pipeline/overlay_osm.py   # trae el footprint minero de OpenStreetMap → overlay.geojson
```

Sin acotar, el volumen integra el ruido de todo el AOI. Con el footprint, el cálculo se limita a la mina y el
**terreno de afuera** sirve para estimar el sesgo de co-registro.

## 4. Resta y volumen

```bash
mamba env create -f pipeline/environment.yml && mamba activate demdiff
python pipeline/dem_diff.py --base dems/base_2000.tif --new dems/new_2012.tif \
       --pit pipeline/overlay.geojson
```

`dem_diff.py` reproyecta ambos DEM a una **grilla UTM común** (área de celda en m²), resta, **co-registra en
vertical** (resta la mediana de Δh del terreno estable fuera del pit), acota al footprint, e imprime
**volumen excavado / depositado / neto**. Salidas: `dem_diff.tif` (Δh) y `demo_volumen.html` (mapa interactivo).

## 5. Cruce con producción

El volumen excavado se compara contra el **material movido declarado** (toneladas de mineral + estéril,
*strip ratio*) de los reportes de la empresa, para ver si el orden de magnitud cierra. → ver
[caso público](caso-publico.md).

!!! info "Complemento InSAR (opcional)"
    Para **estabilidad de taludes y escombreras** (deformación lenta, mm/año) sí aplica InSAR: ahí se puede
    reutilizar el pipeline Sentinel-1 → HyP3 → MintPy de los repos hermanos. Es un análisis distinto del
    volumen excavado.
