"""Support/Resistance-Level aus Pivots -- look-ahead-frei per Konstruktion.

Bisher war diese Logik in fuenf Forschungsskripten kopiert. Hier einmal, mit
Tests.

**Die Zeitregel, an der alles haengt:**

Ein Pivot bei Bar ``i`` ist das Extrem ueber ``i-width .. i+width``. Er ist
damit erst bei Bar ``i+width`` bekannt -- vorher weiss man nicht, ob noch ein
hoeheres Hoch kommt. ``find_pivots`` gibt deshalb ``confirmed_at = i + width``
zurueck, und ``build_levels`` arbeitet Pivots erst ab diesem Bar ein.

Ereignisse (Ausbruch, Bounce) bei Bar ``t`` pruefen ausschliesslich den
Level-Stand von ``t-1``. Damit kann kein Level ein Ereignis ausloesen, das erst
durch denselben Bar entstanden ist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

from .renko import wilder_atr

RESISTANCE = 1
SUPPORT = -1


@dataclass(frozen=True)
class Pivot:
    """Ein bestaetigter Wendepunkt."""

    bar: int          # Bar, an dem das Extrem liegt
    confirmed_at: int # Bar, ab dem der Pivot bekannt ist (= bar + width)
    price: float
    kind: int         # RESISTANCE (Hoch) oder SUPPORT (Tief)


@dataclass
class Level:
    """Eine Zone, in der sich mehrere Pivots buendeln."""

    price: float      # laufender Mittelwert der zugehoerigen Pivots
    kind: int
    touches: int
    last_bar: int     # Bar der letzten Beruehrung (fuer das Verfallsdatum)

    def as_tuple(self) -> Tuple[float, int, int, int]:
        return (self.price, self.kind, self.touches, self.last_bar)


def find_pivots(df: pd.DataFrame, width: int = 8) -> List[Pivot]:
    """Pivot-Hochs und -Tiefs ueber ``+/- width`` Bars.

    Ein Bar kann gleichzeitig Hoch- und Tief-Pivot sein (bei sehr ruhigen
    Phasen); beide werden zurueckgegeben. ``>=``/``<=`` statt strikter
    Vergleiche, damit Plateaus nicht verloren gehen.
    """
    h = df["high"].to_numpy(dtype=float)
    l = df["low"].to_numpy(dtype=float)
    n = len(df)
    out: List[Pivot] = []
    for i in range(width, n - width):
        if h[i] >= h[i - width : i + width + 1].max():
            out.append(Pivot(i, i + width, float(h[i]), RESISTANCE))
        if l[i] <= l[i - width : i + width + 1].min():
            out.append(Pivot(i, i + width, float(l[i]), SUPPORT))
    out.sort(key=lambda p: (p.confirmed_at, p.kind))
    return out


def build_levels(df: pd.DataFrame, width: int = 8, tol_atr: float = 0.5,
                 max_age: int = 1000, atr_period: int = 14
                 ) -> Dict[int, List[Tuple[float, int, int, int]]]:
    """Level-Stand je Bar.

    Pivots innerhalb von ``tol_atr * ATR`` gelten als dasselbe Level; der
    Levelpreis wird als laufender Mittelwert nachgefuehrt, die Beruehrungszahl
    hochgezaehlt. Level ohne Beruehrung in ``max_age`` Bars verfallen.

    Rueckgabe: ``{bar: [(preis, art, beruehrungen, letzter_bar), ...]}``
    """
    pivots = find_pivots(df, width)
    atr = wilder_atr(df, atr_period).to_numpy(dtype=float)
    n = len(df)
    levels: List[Level] = []
    by_bar: Dict[int, List[Tuple[float, int, int, int]]] = {}
    pi = 0

    for t in range(n):
        # 1) alle Pivots einarbeiten, die bis einschliesslich t bestaetigt sind
        while pi < len(pivots) and pivots[pi].confirmed_at <= t:
            p = pivots[pi]
            pi += 1
            a = atr[min(t, n - 1)]
            if not np.isfinite(a) or a <= 0:
                continue
            tol = tol_atr * a
            hit = None
            for lv in levels:
                if lv.kind == p.kind and abs(lv.price - p.price) <= tol:
                    hit = lv
                    break
            if hit is not None:
                hit.price = (hit.price * hit.touches + p.price) / (hit.touches + 1)
                hit.touches += 1
                hit.last_bar = t
            else:
                levels.append(Level(p.price, p.kind, 1, t))

        # 2) verfallene Level entfernen
        levels = [lv for lv in levels if t - lv.last_bar <= max_age]
        by_bar[t] = [lv.as_tuple() for lv in levels]

    return by_bar


def breakout_events(by_bar, df: pd.DataFrame, min_touch: int = 6
                    ) -> List[Tuple[int, int, int, float]]:
    """Schlusskurs durchbricht ein Level mit genug Beruehrungen.

    Rueckgabe: ``[(bar, richtung, beruehrungen, levelpreis), ...]``
    Richtung +1 = Widerstand nach oben gebrochen, -1 = Unterstuetzung nach unten.
    """
    c = df["close"].to_numpy(dtype=float)
    out = []
    for t in range(1, len(df)):
        for (price, kind, touches, _) in by_bar.get(t - 1, ()):
            if touches < min_touch:
                continue
            if kind == RESISTANCE and c[t - 1] <= price < c[t]:
                out.append((t, 1, touches, price))
            elif kind == SUPPORT and c[t - 1] >= price > c[t]:
                out.append((t, -1, touches, price))
    return out


def bounce_events(by_bar, df: pd.DataFrame, min_touch: int = 6,
                  zone_atr: float = 0.25, atr_period: int = 14
                  ) -> List[Tuple[int, int, int, float]]:
    """Kurs laeuft in die Zone und schliesst auf der HALTENDEN Seite.

    Unterstuetzung: Tief erreicht die Zone, Schluss bleibt darueber -> long.
    Widerstand:     Hoch erreicht die Zone, Schluss bleibt darunter  -> short.

    Ein Bounce wird nur gezaehlt, wenn der Vorbar noch ausserhalb der Zone
    schloss -- sonst liefert jede Seitwaertsphase im Level dutzende Signale.
    """
    h = df["high"].to_numpy(dtype=float)
    l = df["low"].to_numpy(dtype=float)
    c = df["close"].to_numpy(dtype=float)
    atr = wilder_atr(df, atr_period).to_numpy(dtype=float)
    out = []
    for t in range(1, len(df)):
        a = atr[t]
        if not np.isfinite(a) or a <= 0:
            continue
        zone = zone_atr * a
        for (price, kind, touches, _) in by_bar.get(t - 1, ()):
            if touches < min_touch:
                continue
            if kind == SUPPORT:
                if l[t] <= price + zone and c[t] > price and c[t - 1] > price + zone:
                    out.append((t, 1, touches, price))
            elif kind == RESISTANCE:
                if h[t] >= price - zone and c[t] < price and c[t - 1] < price - zone:
                    out.append((t, -1, touches, price))
    return out


def nearest_opposite(by_bar, t: int, price: float, direction: int,
                     min_touch: int = 1) -> float:
    """Naechstes Gegenlevel in Handelsrichtung -- als Kursziel.

    ``direction`` +1 (long) sucht den naechsten Widerstand oberhalb,
    -1 (short) die naechste Unterstuetzung unterhalb. ``nan``, wenn keins da ist.
    """
    want = RESISTANCE if direction > 0 else SUPPORT
    best = np.nan
    for (p, kind, touches, _) in by_bar.get(t, ()):
        if kind != want or touches < min_touch:
            continue
        if direction > 0 and p > price:
            best = p if not np.isfinite(best) else min(best, p)
        elif direction < 0 and p < price:
            best = p if not np.isfinite(best) else max(best, p)
    return best
