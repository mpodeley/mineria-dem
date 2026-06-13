# ¿Cuánto material removió una mina a cielo abierto, visto desde el espacio?

Este sitio documenta un **experimento técnico**: estimar el **volumen excavado** en una mina
**open-pit** comparando **modelos de elevación (DEM)** de fechas distintas. Es el repo hermano de
[litio-insar](https://mpodeley.github.io/litio-insar/) y de
[vaca-muerta-insar](https://mpodeley.github.io/vaca-muerta-insar/), con la misma filosofía: datos
satelitales, método reproducible, y cruce con la actividad declarada de la empresa.

> **¿Se puede cuantificar el material movido en una open-pit con DEMs públicos, y cuánto coincide con
> la producción reportada?**

!!! danger "Por qué NO es InSAR (la diferencia clave con los repos hermanos)"
    El InSAR mide deformación de **milímetros a centímetros** por año y necesita que el suelo
    **conserve coherencia** entre pasadas. Una open-pit activa hace lo contrario: cambia **decenas de
    metros** y la voladura/excavación **decorrelaciona** la fase. Por eso el material removido se mide
    con **diferencia de DEMs** (Δh entre dos fechas), no con interferometría. El InSAR acá solo serviría,
    como complemento, para la **estabilidad de taludes y escombreras** (deformación lenta).

## La idea en una línea

`V_excavado = Σ (h_base − h_reciente) × área_celda`  (sumando solo donde la elevación **bajó**).

Restamos dos DEM, integramos el descenso de elevación sobre el área del pit, y obtenemos los **m³
excavados** (y los depositados en escombreras). → `pipeline/dem_diff.py`.

## Plan

- **[Caso público (Chile/AR)](caso-publico.md)** — una mina con empresa que reporta producción (p. ej.
  Chuquicamata/Codelco, Escondida/BHP, Veladero/Barrick) para contrastar el volumen estimado contra el
  material movido declarado.
- **[Caso opaco (China)](caso-opaco.md)** — replicar donde no hay datos operativos públicos (p. ej. carbón
  a cielo abierto en Mongolia Interior, o Bayan Obo).

!!! success "Estado: pipeline funcionando con datos 100% gratuitos"
    Ya hay un **resultado real** sobre [Veladero](caso-publico.md): restando **SRTM (2000)** vs
    **Copernicus GLO-30 (~2012)** —ambos gratuitos— se estiman **≈285 Mm³ excavados** en los dos pits, con
    los dos huecos y las escombreras nítidamente resueltos. Para una mina que arrancó después de 2000, no
    hace falta DEM comercial. Extender a **hoy** sí requiere un DEM reciente (estéreo/lidar). Ver
    [Resultados](resultados.md).
