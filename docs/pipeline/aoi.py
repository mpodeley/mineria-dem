"""AOI y config — mina open-pit. Volumen removido por DEM-differencing (NO InSAR).

A diferencia de litio-insar (subsidencia mm/año con Sentinel-1), acá medimos el
MATERIAL EXCAVADO: decenas de metros de cambio de elevación entre dos fechas. Eso
NO es un problema InSAR (la mina activa decorrelaciona la fase y el rango supera
al interferométrico); se resuelve restando dos Modelos de Elevación (DEM).

Caso público inicial (placeholder): Chuquicamata (Codelco, Chile), el open-pit
icónico. Bounding box APROXIMADO al pit, a refinar contra imagen satelital. El
caso opaco posterior: una open-pit en China (p. ej. carbón en Mongolia Interior).
"""

from __future__ import annotations

# --- Bounding box (lon/lat) cubriendo el pit y las escombreras ---
WEST = -68.95
SOUTH = -22.36
EAST = -68.85
NORTH = -22.26

# --- Referencia (lat, lon): centro del pit (aprox.) ---
PIT = (-22.31, -68.90)

# --- Épocas a comparar (DEM base vs DEM reciente). Solo informativo/etiquetas. ---
EPOCH_BASE = "2011"   # p. ej. Copernicus GLO-30 (adquisición ~2011–2015)
EPOCH_NEW = "2024"    # DEM reciente (estéreo óptico / lidar / proveedor)


def polygon_wkt() -> str:
    return (
        f"POLYGON(({WEST} {SOUTH},{EAST} {SOUTH},"
        f"{EAST} {NORTH},{WEST} {NORTH},{WEST} {SOUTH}))"
    )


def center_lonlat() -> tuple[float, float]:
    return ((WEST + EAST) / 2.0, (SOUTH + NORTH) / 2.0)
