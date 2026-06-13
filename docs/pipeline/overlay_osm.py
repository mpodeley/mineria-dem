#!/usr/bin/env python
"""Genera overlay.geojson a partir de OpenStreetMap (Overpass) para el AOI.

Trae los polígonos del footprint minero (cantera/pit, uso industrial, escombreras)
dentro del bounding box de aoi.py y los guarda como overlay.geojson. dem_diff.py lo
usa con --pit para acotar el volumen al área de la mina (y estimar el sesgo en el
terreno estable de afuera).

    python overlay_osm.py            # escribe overlay.geojson

Es un PUNTO DE PARTIDA: la cobertura de OSM en alta montaña es parcial. Revisá el
resultado contra la imagen satelital y completá/edita a mano si hace falta.
Sin dependencias externas (urllib stdlib).
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

import aoi

HERE = Path(__file__).parent
OUT = HERE / "overlay.geojson"
OVERPASS = "https://overpass-api.de/api/interpreter"

# (clave, valor) a buscar como way/relation con geometría dentro del bbox.
TAGS = [
    ("landuse", "quarry"),
    ("man_made", "mineshaft"),
    ("landuse", "industrial"),
    ("man_made", "spoil_heap"),
    ("landuse", "landfill"),
    ("natural", "water"),
]


def _query() -> str:
    s, w, n, e = aoi.SOUTH, aoi.WEST, aoi.NORTH, aoi.EAST
    bbox = f"{s},{w},{n},{e}"
    parts = []
    for k, v in TAGS:
        parts.append(f'way["{k}"="{v}"]({bbox});')
        parts.append(f'relation["{k}"="{v}"]({bbox});')
    return f"[out:json][timeout:90];({''.join(parts)});out geom;"


def _way_to_polygon(el: dict) -> list | None:
    geom = el.get("geometry")
    if not geom or len(geom) < 4:
        return None
    ring = [[p["lon"], p["lat"]] for p in geom]
    if ring[0] != ring[-1]:
        ring.append(ring[0])  # cerrar el anillo
    return [ring]


def main() -> None:
    q = _query()
    print(f"==> Overpass query sobre bbox {aoi.SOUTH},{aoi.WEST},{aoi.NORTH},{aoi.EAST}")
    req = urllib.request.Request(
        OVERPASS, data=b"data=" + urllib.parse.quote(q).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": "litio-insar/1.0 (overlay_osm.py; github.com/mpodeley/litio-insar)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)

    feats = []
    for el in data.get("elements", []):
        coords = _way_to_polygon(el) if el["type"] == "way" else None
        if not coords:
            continue
        tags = el.get("tags", {})
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": coords},
            "properties": {"osm_id": el["id"],
                           "name": tags.get("name", ""),
                           "tag": next((f"{k}={v}" for k, v in TAGS if tags.get(k) == v), "")},
        })

    fc = {"type": "FeatureCollection", "features": feats}
    OUT.write_text(json.dumps(fc), encoding="utf-8")
    print(f"    {len(feats)} polígonos → {OUT.name}")
    if not feats:
        print("    (OSM no devolvió polígonos; digitalizá las piletas a mano sobre Sentinel-2)")


if __name__ == "__main__":
    main()
