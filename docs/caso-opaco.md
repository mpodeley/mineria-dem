# Caso opaco: Haerwusu (Mongolia Interior, China)

El mismo DEM-differencing, ahora sobre **Haerwusu** (哈尔乌素), en el carbonífero de Jungar (Ordos, Mongolia
Interior): la **mayor mina de carbón a cielo abierto de China**, de Shenhua Group, en producción desde
**octubre de 2008**. Acá no hay tabla pública año a año de mineral/estéril como en Veladero — el satélite pasa
a ser **la medida independiente** del ritmo de extracción.

!!! tip "Mismo truco free que Veladero"
    Haerwusu arrancó en 2008, así que el **SRTM 2000** capta la estepa casi intacta y el **GLO-30 (~2012)** el
    pit ya abierto. El AOI incluye también el pit vecino **Heidaigou** (en operación desde 1999). Ambos DEM,
    gratuitos. El co-registro dio un sesgo de **+0,08 m** (terreno llano, los DEM concuerdan casi perfecto).

## Resultado (2000 → ~2012)

![Δh Haerwusu 2000→2012](assets/dem_diff_china.png){ loading=lazy }

<iframe src="../assets/demo_volumen_china.html" width="100%" height="540" style="border:1px solid #ccc;border-radius:6px"></iframe>

*Rojo = excavado, azul = depositado (escombreras). Se ven el gran pit de Haerwusu/Heidaigou (−150 a −200 m) y
un pit menor al este. Acotado al footprint minero de OpenStreetMap (incluye el polígono del 准格尔煤田,
"carbonífero de Jungar").*

| Métrica | Valor |
|---|---|
| **Excavado** | **≈ 480 Mm³** |
| **Depositado** (dentro del footprint) | ≈ 118 Mm³ |
| **Neto** (excavado − depositado) | ≈ **−362 Mm³** de remoción |
| Footprint | 56.956 celdas (~37 km², celda 26×26 m) |
| Co-registro | sesgo +0,08 m (insignificante) |

A diferencia de Veladero (donde excavado ≈ depositado, todo dentro del footprint), acá hay **remoción neta
grande**: el **carbón se extrae y se va** (se quema, no se apila), y parte del estéril se deposita **fuera**
del polígono. Es la firma volumétrica de una mina de carbón.

## Cruce con lo poco que se reporta

Convirtiendo el volumen a masa (carbón+roca, ρ ~1,8–2,2 t/m³): **≈ 480 Mm³ → ~860–1.060 Mt** de material
removido de los pits entre 2000 y ~2012.

Para contexto: Haerwusu tiene capacidad **aprobada de 35 Mtpa** de carbón (real ~20–27 Mtpa) y Heidaigou
~30 Mtpa. El **carbón** es solo una fracción de lo movido —el grueso es **estéril** (alto *strip ratio*)—, así
que ~1.000 Mt de material total sobre ~12 años (Heidaigou) más ~4 años (Haerwusu) es del orden esperado.

!!! danger "La opacidad es el punto"
    No existe un dataset público de mineral/estéril año a año para estas minas (a diferencia del *technical
    report* de Veladero). Acá el DEM-diff **no se valida contra el dato fino porque ese dato no es público** —
    y eso es exactamente lo que hace valioso al método: una medición **independiente y verificable** del
    material removido, a partir de satélites gratuitos, donde el reporte oficial no transparenta los números.

## Estado

- [x] Elegir mina y AOI (**Haerwusu**, `SITE=china` en `aoi.py`).
- [x] Bajar SRTM 2000 + GLO-30 ~2012 (`SITE=china python fetch_dems.py`).
- [x] Footprint desde OSM (`overlay_china.geojson`) y `dem_diff.py` con co-registro.
- [ ] Datar la expansión del pit con Sentinel-2 (óptico) año a año.
- [ ] DEM reciente (estéreo/lidar) para extender más allá de ~2012 y estimar la tasa actual.
