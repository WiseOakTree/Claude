"""Heatmaps fuer Sweep-Ergebnisse.

Visualisiert eine Sweep-Tabelle als Parametergitter (z.B. ATR-Multiplikator x
Risiko) mit einer Kennzahl je Zelle. Farbwahl nach Aufgabe der Kennzahl:

  * ``pass_rate``      -> sequenziell (viridis), hoeher = besser
  * ``median_return``  -> divergierend um 0 (Verlust rot, Gewinn blau)
  * ``worst_maxdd``    -> divergierend um das Drawdown-Limit des Presets
                          (unter Limit gut, darueber = Bust-Gefahr)

Alle genutzten Colormaps sind perzeptuell uniform bzw. farbfehlsichtigkeits-
tauglich; jede Zelle ist zusaetzlich mit ihrem Wert beschriftet, sodass die
Farbe nie die einzige Information ist.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from .prop import PRESETS


def heatmap_pivot(table: pd.DataFrame, x_col: str, y_col: str, metric: str,
                  agg: str = "mean") -> pd.DataFrame:
    """Verdichtet die Sweep-Tabelle zu einem 2D-Gitter (y=Zeilen, x=Spalten).

    Ueber nicht dargestellte Parameter wird mit ``agg`` aggregiert (Default
    Mittelwert). Zeilen absteigend sortiert, sodass grosse y-Werte oben stehen.
    """
    for col in (x_col, y_col, metric):
        if col not in table.columns:
            raise ValueError(f"Spalte fehlt in der Sweep-Tabelle: {col!r}")
    pivot = table.pivot_table(index=y_col, columns=x_col, values=metric, aggfunc=agg)
    return pivot.sort_index(ascending=False)


def _short(col: str) -> str:
    return col.split(".")[-1]


def save_heatmap(sweep, path: str,
                 x_col: str = "risk.risk_per_trade_pct",
                 y_col: str = "renko.atr_multiplier",
                 agg: str = "mean") -> bool:
    """Speichert eine 3-Panel-Heatmap (Pass-Rate / Median-Rendite / Worst-DD).

    Gibt False zurueck, wenn matplotlib nicht verfuegbar ist.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import TwoSlopeNorm
    except Exception:
        return False

    table = sweep.table
    dd_limit = PRESETS[sweep.preset].max_total_drawdown_pct

    panels = [
        # Konsistente Semantik in beiden divergierenden Panels: blau = gut, rot = schlecht.
        ("pass_rate", "Pass-Rate", "viridis", None, lambda v: f"{v*100:.0f}%"),
        ("median_return", "Median-Rendite %", "coolwarm_r",
         "diverge0", lambda v: f"{v*100:.1f}"),
        ("worst_maxdd", f"Worst-Drawdown % (Limit {dd_limit*100:.0f}%)", "coolwarm",
         "diverge_limit", lambda v: f"{v*100:.1f}"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
    for ax, (metric, title, cmap, norm_kind, fmt) in zip(axes, panels):
        pivot = heatmap_pivot(table, x_col, y_col, metric, agg=agg)
        vals = pivot.to_numpy(dtype=float)

        norm = None
        if norm_kind == "diverge0" and np.nanmin(vals) < 0 < np.nanmax(vals):
            m = max(abs(np.nanmin(vals)), abs(np.nanmax(vals)))
            norm = TwoSlopeNorm(vmin=-m, vcenter=0.0, vmax=m)
        elif norm_kind == "diverge_limit":
            lo, hi = float(np.nanmin(vals)), float(np.nanmax(vals))
            if lo < dd_limit < hi:
                norm = TwoSlopeNorm(vmin=lo, vcenter=dd_limit, vmax=hi)

        im = ax.imshow(vals, cmap=cmap, norm=norm, aspect="auto")
        ax.set_title(title, fontsize=12, pad=10)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"{c*100:g}%" for c in pivot.columns], fontsize=9)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([f"{i:g}x" for i in pivot.index], fontsize=9)
        ax.set_xlabel(_short(x_col) + " (Risiko/Trade)", fontsize=10)
        ax.set_ylabel(_short(y_col) + " (Brick-Groesse)", fontsize=10)

        # Werte in die Zellen schreiben (Farbe ist nie die einzige Info)
        for r in range(vals.shape[0]):
            for c in range(vals.shape[1]):
                v = vals[r, c]
                if np.isnan(v):
                    continue
                ax.text(c, r, fmt(v), ha="center", va="center", fontsize=8,
                        color="white" if _needs_light_text(im, v) else "black")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle(
        f"Parameter-Heatmap -- {PRESETS[sweep.preset].name}  "
        f"({sweep.n_scenarios} Szenarien)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _needs_light_text(im, value: float) -> bool:
    """Heuristik fuer lesbaren Text: bei dunklem Zellhintergrund weiss."""
    try:
        rgba = im.cmap(im.norm(value))
        luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
        return luminance < 0.5
    except Exception:
        return False
