"""MACD auf Renko-Bricks -- der Aufbau, den man auf einem Renko-Chart sieht.

Wer in TradingView einen MACD auf einen Renko-Chart legt, rechnet ihn **nicht**
auf Zeitbars, sondern auf der **Brick-Reihe**. Das ist ein anderer Indikator:
Bricks entstehen nur bei Bewegung, also glaettet Renko die Zeitachse weg. Der
MACD sieht dadurch deutlich ruhiger aus -- und kreuzt seltener, aber
zusammenhaengender.

Dieses Modul baut genau das nach:

  * MACD(12/26/9) auf den **Brick-Schlusskursen**
  * Signal bei jeder **Kreuzung** von MACD-Linie und Signallinie
  * Jedes Signal traegt den Bar-Index der Bar, die den Brick ausgeloest hat --
    damit die Engine zum **Bar-Schluss** fuellen kann statt am Brick-Level.

Der letzte Punkt ist der wichtige. Ein Brick schliesst auf einem Gitter-Level
*innerhalb* einer Kerze. Wer dort fuellt, handelt zu einem Preis, der vor der
signalausloesenden Information liegt. Siehe ``docs/realism.md``.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

SIGNAL_COLUMNS = ["time", "src_index", "price", "target", "brick_size"]


def macd_lines(bricks: pd.DataFrame, fast: int = 12, slow: int = 26,
               signal: int = 9) -> pd.DataFrame:
    """MACD-Linie und Signallinie auf den Brick-Schlusskursen."""
    if fast >= slow:
        raise ValueError("fast muss kleiner als slow sein")
    close = pd.Series(bricks["close"].to_numpy(dtype=float))
    line = (close.ewm(span=fast, adjust=False).mean()
            - close.ewm(span=slow, adjust=False).mean())
    sig = line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"macd": line.to_numpy(), "signal": sig.to_numpy()})


def macd_signals(bricks: pd.DataFrame, fast: int = 12, slow: int = 26,
                 signal: int = 9, allow_long: bool = True,
                 allow_short: bool = True,
                 warmup: Optional[int] = None) -> pd.DataFrame:
    """Ein Signal je MACD-Kreuzung auf der Brick-Reihe.

    ``warmup`` verwirft die Einschwingphase der EMAs (Default ``slow + signal``
    Bricks) -- ohne das erzeugt der erste Brick sofort eine Scheinkreuzung.
    """
    if len(bricks) == 0:
        return pd.DataFrame(columns=SIGNAL_COLUMNS)
    lines = macd_lines(bricks, fast, slow, signal)
    diff = (lines["macd"] - lines["signal"]).to_numpy()
    warmup = (slow + signal) if warmup is None else warmup

    oben = diff > 0
    kreuzung = np.zeros(len(diff), dtype=int)
    kreuzung[1:] = np.where(oben[1:] & ~oben[:-1], 1,
                            np.where(~oben[1:] & oben[:-1], -1, 0))
    kreuzung[:max(warmup, 1)] = 0

    k = np.where(kreuzung != 0)[0]
    if allow_long is False:
        k = k[kreuzung[k] != 1]
    if allow_short is False:
        k = k[kreuzung[k] != -1]
    if len(k) == 0:
        return pd.DataFrame(columns=SIGNAL_COLUMNS)

    return pd.DataFrame({
        "time": bricks["time"].to_numpy()[k],
        "src_index": bricks["src_index"].to_numpy()[k].astype(int),
        "price": bricks["close"].to_numpy()[k].astype(float),
        "target": kreuzung[k].astype(int),
        "brick_size": bricks["brick_size"].to_numpy()[k].astype(float),
    })


def filter_signals(signals: pd.DataFrame, ok: np.ndarray) -> pd.DataFrame:
    """Behaelt nur Signale, deren Ausloesebar die Bedingung ``ok`` erfuellt.

    ``ok`` ist ein boolesches Feld ueber die **Bars** (nicht ueber die Signale),
    damit ein Filter genau so ausgewertet wird, wie er zum Signalzeitpunkt
    bekannt war.
    """
    if len(signals) == 0:
        return signals
    idx = signals["src_index"].to_numpy(dtype=int)
    maske = np.asarray(ok, dtype=bool)[idx]
    return signals[maske].reset_index(drop=True)


# --- Fertige Setups ---------------------------------------------------------
#
# Das Chart-Setup "Renko OHLC, Box 1 %, MACD" in drei Managementstufen. Die
# Renko-Einstellungen selbst kommen aus der Konfiguration (siehe
# ``configs/tradingview_renko_1pct.yaml``), damit man Boxgroesse und Quelle
# aendern kann, ohne den Code anzufassen.

def _setups():
    from .config import ManagementConfig
    from .renko_trail import Variant

    def v(key, label, mgmt):
        return Variant(key, label, "macd", management=mgmt)

    return {
        "MACD0": v("MACD0", "MACD-Kreuzung, kein Stop (dreht am Gegensignal)",
                   ManagementConfig()),
        "MACD1": v("MACD1", "MACD-Kreuzung + harter Stop (2 Boxen)",
                   ManagementConfig(hard_stop=True, stop_slippage_pct=0.0005)),
        "MACD2": v("MACD2", "MACD-Kreuzung + Stop + Break-even + Trailing",
                   ManagementConfig(hard_stop=True, stop_slippage_pct=0.0005,
                                    breakeven_bricks=2.0,
                                    breakeven_offset_pct=0.0016,
                                    trail_bricks=2.0)),
    }


SETUPS = _setups()
