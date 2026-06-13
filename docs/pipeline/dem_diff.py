#!/usr/bin/env python
"""DEM-differencing — volumen removido en una mina open-pit.

Resta dos Modelos de Elevación (DEM) de fechas distintas y calcula el volumen de
material EXCAVADO (Δh < 0) y DEPOSITADO (Δh > 0). Ambos DEM se reproyectan a una
grilla UTM común (área de celda en m²) antes de restar, así el volumen sale en m³.

    conda activate demdiff
    python dem_diff.py --base dems/glo30_2011.tif --new dems/reciente_2024.tif

Opcional: --pit pipeline/overlay.geojson para acotar el cálculo al polígono del pit.

Salidas:
  dem_diff.tif        — Δh (m), grilla UTM, reciente − base
  demo_volumen.html   — mapa interactivo (Δh sobre satélite), rojo = excavado
  resumen impreso     — volumen excavado / depositado / neto (m³ y Mm³)

NOTA: el factor limitante con DEMs gratuitos es la BASE TEMPORAL. Copernicus GLO-30
es de ~2011–2015; para una resta significativa se necesita un DEM reciente (estéreo
óptico, lidar o proveedor comercial). Documentá siempre las fechas reales (ver aoi.py).
"""

from __future__ import annotations

import argparse
import base64
import io
from pathlib import Path

import numpy as np

import aoi

HERE = Path(__file__).parent
DIFF_TIF = HERE / f"dem_diff_{aoi.SITE}.tif"
HTML_OUT = HERE / f"demo_volumen_{aoi.SITE}.html"


def _utm_epsg(lon: float, lat: float) -> str:
    zone = int((lon + 180) / 6) + 1
    return f"EPSG:{(32700 if lat < 0 else 32600) + zone}"


def _reproject_to(src_path: Path, dst_crs: str, ref=None):
    """Reproyecta un DEM a dst_crs. Si `ref` (dataset) se pasa, calca su grilla."""
    import rasterio
    from rasterio.warp import Resampling, calculate_default_transform, reproject

    with rasterio.open(src_path) as src:
        if ref is None:
            transform, w, h = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds
            )
        else:
            transform, w, h = ref["transform"], ref["width"], ref["height"]
        dst = np.full((h, w), np.nan, dtype="float32")
        reproject(
            source=rasterio.band(src, 1), destination=dst,
            src_transform=src.transform, src_crs=src.crs,
            dst_transform=transform, dst_crs=dst_crs,
            resampling=Resampling.bilinear,
            src_nodata=src.nodata, dst_nodata=np.nan,
        )
    return dst, {"transform": transform, "width": w, "height": h, "crs": dst_crs}


def _pit_mask(geojson: Path, grid) -> np.ndarray:
    from rasterio.features import geometry_mask
    from rasterio.warp import transform_geom
    import json
    # El overlay viene en EPSG:4326; reproyectar a la grilla (UTM) antes de rasterizar.
    geoms = [transform_geom("EPSG:4326", grid["crs"], f["geometry"])
             for f in json.load(open(geojson))["features"]]
    # geometry_mask: True = fuera de los polígonos → invertimos para quedarnos dentro
    return ~geometry_mask(geoms, out_shape=(grid["height"], grid["width"]),
                          transform=grid["transform"], invert=False)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True, type=Path, help="DEM base (más antiguo)")
    ap.add_argument("--new", required=True, type=Path, help="DEM reciente")
    ap.add_argument("--pit", type=Path, help="GeoJSON del pit para acotar (opcional)")
    ap.add_argument("--no-coreg", action="store_true",
                    help="no restar el sesgo de co-registro vertical")
    args = ap.parse_args()

    import rasterio

    lon, lat = aoi.center_lonlat()
    crs = _utm_epsg(lon, lat)
    print(f"==> Grilla común {crs} (UTM, área de celda en m²)")

    base, grid = _reproject_to(args.base, crs)            # define la grilla
    new, _ = _reproject_to(args.new, crs, ref=grid)       # calcada a la misma grilla
    dh = new - base                                       # Δh (m): + sube, − baja

    px = abs(grid["transform"].a)
    py = abs(grid["transform"].e)
    cell_area = px * py
    print(f"    resolución {px:.0f}×{py:.0f} m  ·  celda {cell_area:.0f} m²")

    valid = np.isfinite(dh)

    # Co-registro vertical: los DEM tienen un sesgo de altura (geoide/banda/penetración).
    # Lo estimamos como la mediana de Δh en TERRENO ESTABLE (fuera del pit) y lo restamos.
    inside = None
    if args.pit and args.pit.exists():
        inside = _pit_mask(args.pit, grid)
        stable = valid & ~inside
        bias = float(np.median(dh[stable])) if stable.any() else 0.0
        print(f"    co-registro: sesgo {bias:+.2f} m (mediana en {int(stable.sum())} "
              f"celdas estables fuera del pit) → restado")
        region_label = "pit"
    else:
        bias = float(np.median(dh[valid]))
        print(f"    co-registro: sesgo {bias:+.2f} m (mediana de TODO el AOI) → restado")
        print("    AVISO: sin --pit, el volumen es de TODO el AOI (incluye ruido del terreno).")
        region_label = "AOI"

    if not args.no_coreg:
        dh = dh - bias
    region = (inside if inside is not None else valid) & np.isfinite(dh)

    exc = float(-np.nansum(dh[region & (dh < 0)]) * cell_area)   # excavado (m³, +)
    dep = float(np.nansum(dh[region & (dh > 0)]) * cell_area)    # depositado (m³)
    print(f"\n  Épocas: {aoi.EPOCH_BASE} → {aoi.EPOCH_NEW}  ·  región: {region_label} "
          f"({int(region.sum())} celdas)")
    print(f"  Excavado : {exc/1e6:8.2f} Mm³  ({exc:,.0f} m³)")
    print(f"  Depositado: {dep/1e6:8.2f} Mm³  ({dep:,.0f} m³)")
    print(f"  Neto      : {(dep-exc)/1e6:8.2f} Mm³  (depositado − excavado)")

    # Mostrar Δh solo en la región de interés en el raster/mapa de salida.
    dh = np.where(region, dh, np.nan)

    prof = {"driver": "GTiff", "dtype": "float32", "count": 1,
            "width": grid["width"], "height": grid["height"],
            "crs": crs, "transform": grid["transform"], "nodata": np.nan}
    with rasterio.open(DIFF_TIF, "w", **prof) as dst:
        dst.write(dh.astype("float32"), 1)
    print(f"\n  → {DIFF_TIF.name}")

    _build_html(dh, grid, crs)
    print(f"  → {HTML_OUT.name}")


def _build_html(dh, grid, crs) -> None:
    import folium
    import rasterio
    from matplotlib import cm, colors
    from rasterio.warp import Resampling, calculate_default_transform, reproject

    # Δh (UTM) → EPSG:4326 para que el overlay calce con el basemap satelital
    src_bounds = rasterio.transform.array_bounds(
        grid["height"], grid["width"], grid["transform"]
    )  # (west, south, east, north) en UTM
    dt, w, h = calculate_default_transform(
        crs, "EPSG:4326", grid["width"], grid["height"], *src_bounds
    )
    dh4326 = np.full((h, w), np.nan, dtype="float32")
    reproject(
        source=dh, destination=dh4326,
        src_transform=grid["transform"], src_crs=crs,
        dst_transform=dt, dst_crs="EPSG:4326",
        resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan,
    )
    west, south, east, north = rasterio.transform.array_bounds(h, w, dt)

    finite = dh4326[np.isfinite(dh4326)]
    vmax = float(np.nanpercentile(np.abs(finite), 98)) if finite.size else 50.0
    norm = colors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    rgba = cm.get_cmap("RdBu")(norm(dh4326))
    rgba[..., 3] = np.where(np.isfinite(dh4326), 0.8, 0.0)
    buf = io.BytesIO()
    from matplotlib import pyplot as plt
    plt.imsave(buf, rgba, format="png")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    m = folium.Map(location=[aoi.PIT[0], aoi.PIT[1]], zoom_start=13, tiles=None)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery", name="Satélite",
    ).add_to(m)
    folium.raster_layers.ImageOverlay(
        image=f"data:image/png;base64,{b64}",
        bounds=[[south, west], [north, east]], opacity=1.0,
        name=f"Δh {aoi.EPOCH_BASE}→{aoi.EPOCH_NEW} (m)",
    ).add_to(m)
    folium.Marker([aoi.PIT[0], aoi.PIT[1]], tooltip="Pit").add_to(m)
    folium.LayerControl().add_to(m)
    m.save(str(HTML_OUT))


if __name__ == "__main__":
    main()
