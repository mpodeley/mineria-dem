#!/usr/bin/env python
"""Evolución temporal del pit: sección transversal + slider de 3 épocas.

Toma los tres DEM de un sitio (2000 SRTM, ~2012 GLO-30, 2024 ASTER), los lleva a
una grilla UTM común, los co-registra en vertical (resta la mediana del terreno
estable fuera del pit, referida al DEM 2000) y produce:

  seccion_<sitio>.png        — perfil de elevación a lo largo de una línea que
                               cruza el pit, una curva por época (se ve el hueco
                               profundizándose).
  demo_timeline_<sitio>.html — slider Leaflet: Δh acumulado vs 2000 en 3 pasos
                               (2000 → 2012 → 2024) sobre imagen satelital.

    SITE=veladero python evolucion.py
    SITE=china    python evolucion.py

Por defecto usa los DEM estándar de cada sitio en dems/. Línea de sección: E–O por
el punto más profundo, o pasá --line "lon0,lat0,lon1,lat1".
"""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np

import aoi

HERE = Path(__file__).parent
DEMS = HERE / "dems"

# DEM por sitio: (2000, ~2012, 2024). El sufijo de sitio sale de aoi.SITE.
DEFAULTS = {
    "veladero": ("base_2000.tif", "new_2012.tif", "veladero2024_new.tif"),
    "china": ("china_base.tif", "china_new.tif", "china2024_new.tif"),
}
EPOCHS = ("2000", "2012", "2024")
COLORS = ("#2c7fb8", "#d95f0e", "#b2182b")  # 2000, 2012, 2024


def _utm_epsg(lon, lat):
    zone = int((lon + 180) / 6) + 1
    return f"EPSG:{(32700 if lat < 0 else 32600) + zone}"


def _to_grid(path, crs, ref=None):
    import rasterio
    from rasterio.warp import Resampling, calculate_default_transform, reproject
    with rasterio.open(path) as src:
        if ref is None:
            tr, w, h = calculate_default_transform(src.crs, crs, src.width, src.height, *src.bounds)
        else:
            tr, w, h = ref["transform"], ref["width"], ref["height"]
        out = np.full((h, w), np.nan, "float32")
        reproject(source=rasterio.band(src, 1), destination=out,
                  src_transform=src.transform, src_crs=src.crs,
                  dst_transform=tr, dst_crs=crs, resampling=Resampling.bilinear,
                  src_nodata=src.nodata, dst_nodata=np.nan)
    return out, {"transform": tr, "width": w, "height": h, "crs": crs}


def _pit_mask(geojson, grid):
    from rasterio.features import geometry_mask
    from rasterio.warp import transform_geom
    geoms = [transform_geom("EPSG:4326", grid["crs"], f["geometry"])
             for f in json.load(open(geojson))["features"]]
    return ~geometry_mask(geoms, out_shape=(grid["height"], grid["width"]),
                          transform=grid["transform"], invert=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pit", type=Path, default=HERE / f"overlay_{aoi.SITE}.geojson")
    ap.add_argument("--line", help="lon0,lat0,lon1,lat1 (override de la sección)")
    args = ap.parse_args()

    base_f, mid_f, new_f = (DEMS / n for n in DEFAULTS[aoi.SITE])
    lon, lat = aoi.center_lonlat()
    crs = _utm_epsg(lon, lat)

    base, grid = _to_grid(base_f, crs)
    mid, _ = _to_grid(mid_f, crs, ref=grid)
    new, _ = _to_grid(new_f, crs, ref=grid)

    inside = _pit_mask(args.pit, grid) if args.pit.exists() else np.zeros(base.shape, bool)
    stable = np.isfinite(base) & ~inside

    # Co-registro: cada época al datum del DEM 2000 (resta mediana del terreno estable).
    dems = {"2000": base}
    for name, arr in (("2012", mid), ("2024", new)):
        d = arr - base
        bias = float(np.nanmedian(d[stable & np.isfinite(arr)]))
        dems[name] = arr - bias
        print(f"  co-registro {name}: sesgo {bias:+.2f} m")

    T = grid["transform"]
    px, py = abs(T.a), abs(T.e)

    _cross_section(dems, grid, inside, args.line, T, px)
    _slider(dems, grid, crs)


def _xy_to_rc(x, y, T):
    col = (x - T.c) / T.a
    row = (y - T.f) / T.e
    return row, col


def _cross_section(dems, grid, inside, line, T, px):
    from scipy.ndimage import map_coordinates
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    H, W = dems["2000"].shape
    if line:
        lon0, lat0, lon1, lat1 = (float(v) for v in line.split(","))
        from rasterio.warp import transform
        (x0, x1), (y0, y1) = transform("EPSG:4326", grid["crs"], [lon0, lon1], [lat0, lat1])
        r0, c0 = _xy_to_rc(x0, y0, T); r1, c1 = _xy_to_rc(x1, y1, T)
    else:
        # E–O por el punto más profundo (2024 vs 2000) dentro del pit.
        dh = np.where(inside, dems["2024"] - dems["2000"], np.nan)
        if np.isfinite(dh).any():
            r, _c = np.unravel_index(np.nanargmin(dh), dh.shape)
        else:
            r = H // 2
        r0 = r1 = r; c0, c1 = 0, W - 1

    n = int(np.hypot(r1 - r0, c1 - c0)) + 1
    rr = np.linspace(r0, r1, n); cc = np.linspace(c0, c1, n)
    dist = np.arange(n) * px / 1000.0  # km

    fig, ax = plt.subplots(figsize=(11, 5))
    prof = {}
    for (name, arr), col in zip(dems.items(), COLORS):
        z = map_coordinates(np.nan_to_num(arr, nan=np.nan), [rr, cc], order=1, cval=np.nan)
        prof[name] = z
        ax.plot(dist, z, color=col, lw=2.0, label=name)
    # relleno excavado (2000→2024)
    ax.fill_between(dist, prof["2024"], prof["2000"],
                    where=prof["2024"] < prof["2000"], color="#b2182b", alpha=0.15)
    ax.set_xlabel("Distancia a lo largo del perfil (km)")
    ax.set_ylabel("Elevación (m s.n.m., datum 2000)")
    ax.set_title(f"Sección transversal del pit — {aoi.NAME}", weight="bold", fontsize=12)
    ax.legend(title="Época", loc="best")
    ax.grid(alpha=0.3)
    drop = float(np.nanmin(prof["2024"] - prof["2000"]))
    ax.text(0.01, 0.02, f"Máx. descenso 2000→2024 ≈ {drop:.0f} m",
            transform=ax.transAxes, fontsize=9, color="#b2182b")
    fig.tight_layout()
    out = HERE / f"seccion_{aoi.SITE}.png"
    fig.savefig(out, dpi=140)
    print(f"  → {out.name}  (descenso máx {drop:.0f} m)")


def _slider(dems, grid, crs):
    import rasterio
    from matplotlib import cm, colors
    from rasterio.warp import Resampling, calculate_default_transform, reproject

    base = dems["2000"]
    frames_dh = [("2000", np.zeros_like(base)),
                 ("2012", dems["2012"] - base),
                 ("2024", dems["2024"] - base)]
    allv = np.concatenate([f[1][np.isfinite(f[1])] for f in frames_dh])
    vmax = float(np.nanpercentile(np.abs(allv), 98)) or 100.0
    norm = colors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    cmap = cm.get_cmap("RdBu")

    # transform a 4326 una vez
    src_bounds = rasterio.transform.array_bounds(grid["height"], grid["width"], grid["transform"])
    dt, w, h = calculate_default_transform(crs, "EPSG:4326", grid["width"], grid["height"], *src_bounds)
    west, south, east, north = rasterio.transform.array_bounds(h, w, dt)

    out_frames = []
    for label, dh in frames_dh:
        dh4326 = np.full((h, w), np.nan, "float32")
        reproject(source=dh, destination=dh4326, src_transform=grid["transform"], src_crs=crs,
                  dst_transform=dt, dst_crs="EPSG:4326", resampling=Resampling.nearest,
                  src_nodata=np.nan, dst_nodata=np.nan)
        rgba = cmap(norm(dh4326))
        rgba[..., 3] = np.where(np.isfinite(dh4326) & (np.abs(dh4326) > 0.5), 0.85, 0.0)
        buf = io.BytesIO()
        from matplotlib import pyplot as plt
        plt.imsave(buf, rgba, format="png")
        out_frames.append({"label": label,
                           "png": base64.b64encode(buf.getvalue()).decode("ascii")})

    _write_html(out_frames, (south, west, north, east), vmax)


def _write_html(frames, bounds, vmax):
    s, w, n, e = bounds
    data = json.dumps(frames)
    out = HERE / f"demo_timeline_{aoi.SITE}.html"
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Evolución del pit — {aoi.NAME}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html,body,#map{{height:100%;margin:0}}
  .panel{{position:absolute;bottom:18px;left:50%;transform:translateX(-50%);z-index:1000;
    background:rgba(255,255,255,.94);padding:10px 16px;border-radius:8px;
    font:13px sans-serif;box-shadow:0 1px 6px rgba(0,0,0,.3);width:min(440px,86vw)}}
  #yr{{font-weight:bold;color:#b2182b;font-size:15px}} input[type=range]{{width:100%}}
  .legend{{position:absolute;top:12px;right:12px;z-index:1000;background:rgba(255,255,255,.92);
    padding:8px 12px;border-radius:6px;font:12px sans-serif}}
  .bar{{height:10px;width:170px;background:linear-gradient(to right,#b2182b,#f7f7f7,#2166ac);
    border:1px solid #999;margin:3px 0}} .bl{{display:flex;justify-content:space-between;font-size:11px}}
</style></head><body>
<div id="map"></div>
<div class="legend"><b>Δh acumulado vs 2000</b><div class="bar"></div>
  <div class="bl"><span>−{vmax:.0f} m (excavado)</span><span>0</span><span>+{vmax:.0f} m (depositado)</span></div></div>
<div class="panel">
  <div><b>Año:</b> <span id="yr"></span></div>
  <input type="range" id="sl" min="0" max="{len(frames)-1}" value="0" step="1">
  <div style="font-size:11px;color:#666;text-align:center">
    SRTM 2000 · Copernicus GLO-30 ~2012 · ASTER 2024 (estéreo, ASP) — co-registrados</div>
</div>
<script>
const FR={data}; const B=[[{s},{w}],[{n},{e}]];
const map=L.map('map').fitBounds(B);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
  {{attribution:'Esri World Imagery'}}).addTo(map);
const layers=FR.map(f=>L.imageOverlay('data:image/png;base64,'+f.png,B,{{opacity:0}}).addTo(map));
const sl=document.getElementById('sl'),yr=document.getElementById('yr');
function show(i){{layers.forEach((l,k)=>l.setOpacity(k==i?1:0));yr.textContent=FR[i].label;}}
sl.addEventListener('input',ev=>show(+ev.target.value)); show(0);
</script></body></html>"""
    out.write_text(html, encoding="utf-8")
    print(f"  → {out.name}")


if __name__ == "__main__":
    main()
