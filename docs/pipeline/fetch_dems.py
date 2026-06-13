#!/usr/bin/env python
"""Descarga los dos DEM gratuitos para el AOI y los recorta al bounding box.

  BASE     = SRTM (feb 2000, 1 arcsec) — skadi de elevation-tiles-prod (sin auth)
  RECIENTE = Copernicus GLO-30 (~2011–2015) — bucket público de AWS (sin auth)

Ambos quedan recortados al AOI de aoi.py y reproyectados a EGM/elipsoide tal cual
vienen (orthométricos). Salidas en dems/:
  dems/base_2000.tif   (SRTM)
  dems/new_2012.tif    (Copernicus GLO-30)

    python fetch_dems.py

Luego: python dem_diff.py --base dems/base_2000.tif --new dems/new_2012.tif

CAVEAT: SRTM referencia el geoide EGM96 y GLO-30 el EGM2008; la diferencia de
geoide en la zona es <~1 m (sesgo despreciable frente a una excavación de decenas
de metros, pero conviene co-registrar sobre terreno estable — ver próximos pasos).
"""

from __future__ import annotations

import gzip
import math
import urllib.request
from pathlib import Path

import aoi

HERE = Path(__file__).parent
DEMS = HERE / "dems"
UA = {"User-Agent": "mineria-dem/1.0 (fetch_dems.py)"}

COP_BASE = ("https://copernicus-dem-30m.s3.amazonaws.com/"
            "Copernicus_DSM_COG_10_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM/"
            "Copernicus_DSM_COG_10_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM.tif")
SKADI = ("https://s3.amazonaws.com/elevation-tiles-prod/skadi/"
         "{ns}{lat:02d}/{ns}{lat:02d}{ew}{lon:03d}.hgt.gz")


def _tiles() -> list[tuple[int, int]]:
    """Esquinas SW (floor) de los tiles de 1° que cubren el AOI."""
    out = []
    for lat in range(math.floor(aoi.SOUTH), math.ceil(aoi.NORTH)):
        for lon in range(math.floor(aoi.WEST), math.ceil(aoi.EAST)):
            out.append((lat, lon))
    return out


def _download(url: str, dst: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r, open(dst, "wb") as f:
            f.write(r.read())
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"    ! {url.split('/')[-1]}: {exc}")
        return False


def _fetch_copernicus(tiles) -> list[Path]:
    paths = []
    for lat, lon in tiles:
        ns, ew = ("S" if lat < 0 else "N"), ("W" if lon < 0 else "E")
        url = COP_BASE.format(ns=ns, lat=abs(lat), ew=ew, lon=abs(lon))
        dst = DEMS / f"_cop_{ns}{abs(lat):02d}{ew}{abs(lon):03d}.tif"
        print(f"  GLO-30 {ns}{abs(lat):02d}{ew}{abs(lon):03d}")
        if _download(url, dst):
            paths.append(dst)
    return paths


def _fetch_srtm(tiles) -> list[Path]:
    paths = []
    for lat, lon in tiles:
        ns, ew = ("S" if lat < 0 else "N"), ("W" if lon < 0 else "E")
        url = SKADI.format(ns=ns, lat=abs(lat), ew=ew, lon=abs(lon))
        # Nombre canónico EXACTO (sin prefijo): el driver SRTMHGT de GDAL lo exige.
        hgt = DEMS / f"{ns}{abs(lat):02d}{ew}{abs(lon):03d}.hgt"
        gz = DEMS / (hgt.name + ".gz")
        print(f"  SRTM   {ns}{abs(lat):02d}{ew}{abs(lon):03d}")
        if _download(url, gz):
            with gzip.open(gz, "rb") as fi, open(hgt, "wb") as fo:
                fo.write(fi.read())
            gz.unlink(missing_ok=True)
            paths.append(hgt)
    return paths


def _merge_clip(srcs: list[Path], out: Path) -> None:
    """Mosaica los tiles y recorta al AOI."""
    import rasterio
    from rasterio.merge import merge
    from rasterio.windows import from_bounds

    if not srcs:
        raise SystemExit("Sin tiles para procesar.")
    datasets = [rasterio.open(s) for s in srcs]
    mosaic, transform = merge(datasets, bounds=(aoi.WEST, aoi.SOUTH, aoi.EAST, aoi.NORTH))
    prof = datasets[0].profile
    for d in datasets:
        d.close()
    prof.update(driver="GTiff", height=mosaic.shape[1], width=mosaic.shape[2],
                transform=transform, count=1, compress="deflate")
    with rasterio.open(out, "w", **prof) as dst:
        dst.write(mosaic[0], 1)
    print(f"    → {out.relative_to(HERE)} ({mosaic.shape[2]}×{mosaic.shape[1]} px)")


def main() -> None:
    DEMS.mkdir(exist_ok=True)
    tiles = _tiles()
    print(f"==> AOI Veladero · tiles de 1°: {tiles}")
    print("==> Copernicus GLO-30 (reciente):")
    cop = _fetch_copernicus(tiles)
    print("==> SRTM 2000 (base):")
    srtm = _fetch_srtm(tiles)
    print("==> Mosaico + recorte al AOI:")
    _merge_clip(cop, DEMS / "new_2012.tif")
    _merge_clip(srtm, DEMS / "base_2000.tif")
    # limpiar tiles crudos
    for pat in ("_*", "*.hgt", "*.hgt.gz"):
        for p in DEMS.glob(pat):
            p.unlink(missing_ok=True)
    print("\nListo. Corré: python dem_diff.py --base dems/base_2000.tif --new dems/new_2012.tif")


if __name__ == "__main__":
    main()
