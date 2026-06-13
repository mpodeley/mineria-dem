"""AOI y config — mina open-pit. Volumen removido por DEM-differencing (NO InSAR).

A diferencia de litio-insar (subsidencia mm/año con Sentinel-1), acá medimos el
MATERIAL EXCAVADO: decenas de metros de cambio de elevación entre dos fechas. Eso
NO es un problema InSAR (la mina activa decorrelaciona la fase y el rango supera
al interferométrico); se resuelve restando dos Modelos de Elevación (DEM).

Caso público inicial: VELADERO (Barrick / Shandong, San Juan, Argentina), oro a
cielo abierto a ~4.000–4.850 m. La producción arrancó en 2005, así que el SRTM de
feb-2000 capta la montaña PRÍSTINA y el Copernicus GLO-30 (~2012) capta el pit ya
excavado → señal de excavación grande y limpia, con DOS DEM GRATUITOS.

Estrategia free: BASE = SRTM/NASADEM (2000), RECIENTE = Copernicus GLO-30 (~2012).
Extender a "hoy" requiere un DEM reciente (estéreo óptico/lidar, normalmente de pago).
Bounding box a refinar contra imagen satelital.
"""

from __future__ import annotations

# --- Bounding box (lon/lat) cubriendo los pits (Filón Federico, Amable) y escombreras ---
WEST = -69.97
SOUTH = -29.45
EAST = -69.83
NORTH = -29.31

# --- Referencia (lat, lon): mina Veladero ---
PIT = (-29.3723, -69.8995)

# --- Épocas a comparar (DEM base = más antiguo; reciente = más nuevo) ---
EPOCH_BASE = "2000"   # SRTM / NASADEM (feb 2000) — terreno prístino (pre-mina)
EPOCH_NEW = "2012"    # Copernicus GLO-30 (TanDEM-X ~2011–2015) — pit desarrollado


def polygon_wkt() -> str:
    return (
        f"POLYGON(({WEST} {SOUTH},{EAST} {SOUTH},"
        f"{EAST} {NORTH},{WEST} {NORTH},{WEST} {SOUTH}))"
    )


def center_lonlat() -> tuple[float, float]:
    return ((WEST + EAST) / 2.0, (SOUTH + NORTH) / 2.0)
