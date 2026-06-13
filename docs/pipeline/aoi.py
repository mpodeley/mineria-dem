"""AOI y config multi-sitio — mina open-pit. Volumen por DEM-differencing (NO InSAR).

Medimos el MATERIAL EXCAVADO (decenas de metros de cambio de elevación entre dos
fechas) restando dos DEM. NO es un problema InSAR (la mina activa decorrelaciona
la fase y el rango supera al interferométrico).

Estrategia free: si la mina arrancó DESPUÉS de 2000, comparamos SRTM (feb 2000,
terreno prístino) vs Copernicus GLO-30 (~2012, pit desarrollado). Ambos gratuitos.
Extender a "hoy" requiere un DEM reciente (estéreo óptico/lidar, normalmente de pago).

Sitio activo por variable de entorno SITE (default 'veladero'):
    python fetch_dems.py                 # Veladero
    SITE=china python fetch_dems.py      # Haerwusu (Mongolia Interior)
"""

from __future__ import annotations

import os

SITES = {
    # Veladero (Barrick/Shandong, San Juan, AR) — oro, producción desde 2005.
    "veladero": dict(
        NAME="Veladero (San Juan, Argentina)",
        WEST=-69.97, SOUTH=-29.45, EAST=-69.83, NORTH=-29.31,
        PIT=(-29.3723, -69.8995),
        EPOCH_BASE="2000", EPOCH_NEW="2012",
    ),
    # Veladero, pero comparando contra un DEM RECIENTE de ASTER 2024 (estéreo 3N/3B,
    # vía Ames Stereo Pipeline) en vez del GLO-30 ~2012 → ventana 2000→2024.
    "veladero2024": dict(
        NAME="Veladero (San Juan, Argentina) — 2000→2024",
        WEST=-69.97, SOUTH=-29.45, EAST=-69.83, NORTH=-29.31,
        PIT=(-29.3723, -69.8995),
        EPOCH_BASE="2000", EPOCH_NEW="2024",
    ),
    # Haerwusu (Jungar/Ordos, Mongolia Interior, China) — carbón, producción desde oct-2008.
    # La mayor unidad de producción de carbón de China; opacidad operativa total.
    "china": dict(
        NAME="Haerwusu (Mongolia Interior, China)",
        WEST=111.18, SOUTH=39.64, EAST=111.40, NORTH=39.76,
        PIT=(39.70, 111.27),
        EPOCH_BASE="2000", EPOCH_NEW="2012",
    ),
    # Haerwusu contra DEM ASTER 2024 (estéreo 3N/3B vía ASP) → ventana 2000→2024.
    "china2024": dict(
        NAME="Haerwusu (Mongolia Interior, China) — 2000→2024",
        WEST=111.18, SOUTH=39.64, EAST=111.40, NORTH=39.76,
        PIT=(39.70, 111.27),
        EPOCH_BASE="2000", EPOCH_NEW="2024",
    ),
}

SITE = os.environ.get("SITE", "veladero").lower()
if SITE not in SITES:
    raise SystemExit(f"SITE='{SITE}' desconocido. Opciones: {', '.join(SITES)}")

_s = SITES[SITE]
NAME = _s["NAME"]
WEST, SOUTH, EAST, NORTH = _s["WEST"], _s["SOUTH"], _s["EAST"], _s["NORTH"]
PIT = _s["PIT"]
EPOCH_BASE, EPOCH_NEW = _s["EPOCH_BASE"], _s["EPOCH_NEW"]


def polygon_wkt() -> str:
    return (
        f"POLYGON(({WEST} {SOUTH},{EAST} {SOUTH},"
        f"{EAST} {NORTH},{WEST} {NORTH},{WEST} {SOUTH}))"
    )


def center_lonlat() -> tuple[float, float]:
    return ((WEST + EAST) / 2.0, (SOUTH + NORTH) / 2.0)
