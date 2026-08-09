"""Renko-Reversal-Strategie: Signal nach N gleichgerichteten Bricks.

Semantik (wie vom Nutzer gewuenscht -- "Reversal wenn 2 Bricks die Richtung
drehen"):
  * Zaehle aufeinanderfolgende Bricks gleicher Richtung.
  * Sobald ``reversal_bricks`` (Default 2) Bricks in eine Richtung zeigen, ist
    die Zielposition long (+1) bzw. short (-1).
  * Es wird "Stop-and-Reverse" gehandelt: die Position bleibt, bis das
    Gegensignal (2 Gegen-Bricks) kommt.

Der Fill-Preis eines Signals ist der Schlusskurs des ausloesenden 2. Bricks --
also ein Gitter-Level, das innerhalb der Bar real erreicht wurde. Damit gibt es
keinen Lookahead (der Preis war zum Ausloesezeitpunkt tatsaechlich dort).
"""

from __future__ import annotations

import pandas as pd

from .config import StrategyConfig


def generate_signals(bricks: pd.DataFrame, cfg: StrategyConfig) -> pd.DataFrame:
    """Erzeugt aus Bricks eine Signal-Tabelle.

    Rueckgabe: DataFrame mit einer Zeile pro *Positionswechsel* und Spalten
    ``time, src_index, price, target, brick_size`` -- ``target`` in {-1, +1}.
    """
    cfg.validate()
    out_time, out_idx, out_price, out_target, out_size = [], [], [], [], []

    run_dir = 0     # Richtung der aktuellen Brick-Serie
    run_len = 0     # Laenge der aktuellen Serie
    position = 0    # aktuell gehaltene Zielposition

    directions = bricks["direction"].to_numpy()
    closes = bricks["close"].to_numpy()
    sizes = bricks["brick_size"].to_numpy()
    times = bricks["time"].to_numpy()
    src = bricks["src_index"].to_numpy()

    for k in range(len(directions)):
        d = int(directions[k])
        if d == run_dir:
            run_len += 1
        else:
            run_dir = d
            run_len = 1

        if run_len < cfg.reversal_bricks:
            continue

        # Bestaetigte Richtung -> Zielposition. Ist die Richtung nicht erlaubt,
        # wird eine offene Gegenposition zumindest glattgestellt (Kapitalschutz).
        if run_dir == 1:
            desired = 1 if cfg.allow_long else (0 if position == -1 else position)
        else:
            desired = -1 if cfg.allow_short else (0 if position == 1 else position)

        if desired != position:
            out_time.append(times[k])
            out_idx.append(int(src[k]))
            out_price.append(float(closes[k]))
            out_target.append(int(desired))
            out_size.append(float(sizes[k]))
            position = desired

    return pd.DataFrame({
        "time": out_time,
        "src_index": out_idx,
        "price": out_price,
        "target": out_target,
        "brick_size": out_size,
    })
