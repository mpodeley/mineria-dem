# Caso público: Veladero (San Juan, Argentina)

El caso **público** elegido: **Veladero**, oro/plata a cielo abierto operado por Minera Argentina Gold
(JV **Barrick** 50% / **Shandong Gold** 50%), a ~4.000–4.850 m en la cordillera de San Juan. Dos pits
(**Filón Federico** y **Amable**). La empresa **reporta producción**, lo que permite contrastar el volumen
movido estimado por DEM-diff contra el **material declarado**.

!!! tip "Por qué Veladero es el caso ideal para datos gratuitos"
    La producción arrancó en **2005**. Entonces el **SRTM de febrero de 2000** capta la montaña **prístina**
    (pre-mina) y el **Copernicus GLO-30 (~2012)** capta los pits ya excavados. La diferencia es **enorme y
    limpia** — y ambos DEM son **gratuitos**. No hace falta DEM comercial para este período.

## Resultado (2000 → 2012)

| Métrica | Valor |
|---|---|
| **Excavado** | **≈ 285 Mm³** |
| **Depositado** | ≈ 267 Mm³ |
| Material movido (≈ excavado × 2,5 t/m³) | **≈ 700 Mt** en ~7 años |

El [mapa de Δh](resultados.md) muestra los dos pits (−200 a −320 m) y las escombreras adyacentes (hasta
+150 m). Ver [Resultados](resultados.md) para el detalle y los *caveats*.

## Candidatos alternativos (otros casos públicos)

| Mina | Operador | País | Notas |
|---|---|---|---|
| **Chuquicamata** | Codelco | Chile | Open-pit icónica; ya era enorme en 2000 (el cambio 2000–2012 es deepening, señal menos limpia). |
| **Escondida** | BHP | Chile | Mayor mina de cobre del mundo; expansión fuerte en los 2000. |

## Datos públicos a cruzar

- **Material movido / *strip ratio*** y **toneladas de mineral** de los reportes anuales y *technical reports*
  (NI 43-101 / informes de Barrick). Convertir toneladas → volumen con densidad de roca (~2,5–2,7 t/m³) para
  comparar con el Δh integrado.
- **Geometría del pit**: acá se usó el footprint de **OpenStreetMap** (`overlay_osm.py` → `overlay.geojson`);
  refinar contra Sentinel-2 / imágenes históricas.

## Estado

- [x] Elegir la mina y fijar el AOI en `aoi.py` (**Veladero**).
- [x] Conseguir DEM base (SRTM 2000) y reciente (Copernicus GLO-30 ~2012) — `fetch_dems.py`.
- [x] Footprint minero desde OSM → `overlay.geojson` (`overlay_osm.py`).
- [x] Correr `dem_diff.py` con co-registro → Δh + volumen ([Resultados](resultados.md)).
- [ ] Cruzar el volumen estimado contra el material movido **declarado** por Barrick (años 2005–2012).
- [ ] Conseguir un DEM **reciente** (estéreo/lidar) para extender la serie más allá de 2012.
