#!/usr/bin/env bash
# DEM reciente GRATIS desde estéreo óptico ASTER, con Ames Stereo Pipeline (ASP).
#
# Extiende el DEM-diff más allá del GLO-30 (~2012): ASTER tiene par estéreo
# (banda 3N nadir + 3B backward) y archivo gratuito 2000–~2024 vía NASA Earthdata.
# Reconstruye un DEM ~30 m de la fecha que elijas → lo restás contra el SRTM 2000.
#
# Requisitos:
#   - Ames Stereo Pipeline (binarios): https://github.com/NeoGeographyToolkit/StereoPipeline/releases
#   - ~/.netrc con credenciales Earthdata (machine urs.earthdata.nasa.gov)
#
# Uso:
#   export ASP_BIN=/ruta/a/StereoPipeline-*/bin
#   ./aster_dem.sh AST_L1A_00403192024141431_20251004042920   # granule id (0% nube)
#
# Buscar escenas despejadas (CMR), ordenadas por nube:
#   curl -s "https://cmr.earthdata.nasa.gov/search/granules.umm_json?short_name=AST_L1A\
#     &bounding_box=WEST,SOUTH,EAST,NORTH&temporal=2021-01-01T00:00:00Z,2024-12-31T23:59:59Z&page_size=40"
#   (filtrar por el campo CloudCover)
set -euo pipefail
GID="${1:?pasá el granule id de AST_L1A}"
: "${ASP_BIN:?exportá ASP_BIN al directorio bin de Ames Stereo Pipeline}"
export PATH="$ASP_BIN:$PATH"

WORK="aster_${GID}"
mkdir -p "$WORK"; cd "$WORK"

# Fecha del granule (AST_L1A_00MMDDYYYY...) → ruta del data pool
DATE_PART="${GID:11:8}"            # MMDDYYYY
YYYY="${DATE_PART:4:4}"; MM="${DATE_PART:0:2}"; DD="${DATE_PART:2:2}"
URL="https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/AST_L1A.004/${GID}/${GID}.hdf"

echo "==> Descargando $GID ($YYYY-$MM-$DD)"
curl -s -n -L -c /tmp/urscookies -b /tmp/urscookies "$URL" -o aster.hdf
file aster.hdf | grep -qi "Hierarchical Data Format" || { echo "descarga inválida (¿auth?)"; exit 1; }

echo "==> aster2asp (bandas 3N/3B + cámaras RPC)"
aster2asp aster.hdf -o asp

echo "==> parallel_stereo (correlación)"
rm -rf results; mkdir -p results
parallel_stereo -t aster --stereo-algorithm asp_bm \
    asp-Band3N.tif asp-Band3B.tif asp-Band3N.xml asp-Band3B.xml results/run

echo "==> point2dem (DEM 30 m)"
point2dem --tr 30 results/run-PC.tif -o "results/aster_${YYYY}"

echo "Listo → results/aster_${YYYY}-DEM.tif"
echo "Diff:  copiá ese DEM a dems/ y corré dem_diff.py --base dems/<srtm2000> --new <aster> --pit overlay_<sitio>.geojson"
echo "OJO: ASTER usa elipsoide WGS84 y SRTM el geoide EGM96 → el co-registro de dem_diff.py absorbe ese offset (~30 m)."
