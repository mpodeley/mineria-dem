#!/usr/bin/env python
"""Cruce: volumen excavado por DEM-diff vs material movido declarado (Veladero).

Compara el volumen que mide el satélite (dem_diff.py) contra lo que reporta la
empresa. OJO con las unidades:
  - DEM-diff mide VOLUMEN in-situ del hueco del pit (m³) = mineral + estéril removidos.
  - Los reportes dan MASA movida (toneladas de mineral + estéril).
Para comparar, convertimos el volumen a masa con la densidad in-situ de la roca.

    python cruce_volumen.py --exc 285 --epoch 2013

Las cifras de material movido por año salen de veladero_produccion.csv (miningdataonline).
La parte débil es el acumulado 2005–~2013: no hay tabla pública año a año previa a 2017,
así que se ESTIMA con la tasa media reciente y un factor de rampa. Es orden de magnitud.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

HERE = Path(__file__).parent
CSV = HERE / "veladero_produccion.csv"

# Densidad in-situ de la roca volcánica de caja (andesita/dacita alterada), t/m³.
RHO_LO, RHO_HI = 2.2, 2.6
START_YEAR = 2005  # inicio de producción


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exc", type=float, default=285.0,
                    help="volumen excavado por DEM-diff, en Mm³ (default 285)")
    ap.add_argument("--epoch", type=int, default=2013,
                    help="año del DEM reciente / GLO-30 (default 2013)")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8")) if r["total_movido_kt"]]
    tot = [float(r["total_movido_kt"]) / 1000.0 for r in rows]  # Mt/año
    strip = [float(r["strip_ratio"]) for r in rows]
    mean_rate = sum(tot) / len(tot)
    mean_strip = sum(strip) / len(strip)

    # DEM → masa
    m_lo, m_hi = args.exc * RHO_LO, args.exc * RHO_HI
    print("== DEM-differencing (2000 → %d) ==" % args.epoch)
    print(f"  Volumen excavado : {args.exc:.0f} Mm³")
    print(f"  Masa equivalente : {m_lo:.0f}–{m_hi:.0f} Mt  (ρ {RHO_LO}–{RHO_HI} t/m³)")

    # Reportado: estimación del acumulado a la época del DEM reciente
    yrs = args.epoch - START_YEAR + 1
    upper = mean_rate * yrs                       # a tasa plena todos los años
    lower = mean_rate * yrs * 0.7                 # con rampa de los primeros años
    print("\n== Reportado (Barrick / miningdataonline) ==")
    print(f"  Material movido medio (2017–2025): {mean_rate:.0f} Mt/año  (strip medio {mean_strip:.2f})")
    print(f"  Mineral acumulado a 2017: ~319 Mt (≈8,2 Moz Au)  [technical report 2018]")
    print(f"  Acumulado total estimado a {args.epoch} ({yrs} años): ~{lower:.0f}–{upper:.0f} Mt")
    print("    (estimado: no hay tabla pública año a año antes de 2017; rampa 2005–2009)")

    # Veredicto
    ratio_lo = m_lo / upper
    ratio_hi = m_hi / lower
    print("\n== Cruce ==")
    print(f"  DEM / reportado ≈ {ratio_lo:.1f}×–{ratio_hi:.1f}×  → mismo orden de magnitud.")
    print("  El DEM tiende a dar algo MÁS: el hueco incluye todo (mineral+estéril+pre-stripping),")
    print("  la época del GLO-30 (2011–2015) puede ser >2012, y queda sesgo/ruido residual del DEM.")


if __name__ == "__main__":
    main()
