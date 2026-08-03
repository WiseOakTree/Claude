"""Liquiditaetskarte aus Orderbuch-Tiefendaten.

Binance liefert die Tiefe als **kumulierte** Summe je Abstandsband vom
Mittelkurs (+/- 0,2 / 1 / 2 / 3 / 4 / 5 %). Daraus wird hier eine Karte in
ABSOLUTEN Preisen: wie viel USD lagen im Buch in der Naehe eines bestimmten
Kurses.

Der Zweck: Ein S/R-Level, hinter dem viel Kapital liegt, verhaelt sich anders
als eines, hinter dem ein Loch klafft. Und ein Stop gehoert jenseits des
Clusters, nicht mittendrin.

**Grenzen, die man kennen muss:**

* Aufloesung nur 0,2 / 1 / 2 / 3 / 4 / 5 % -- Feinstruktur direkt am Level ist
  nicht sichtbar. Die Karte zeigt Groessenordnungen, keine exakten Cluster.
* Die Daten beginnen 2023-01.
* Ruhende Limit-Orders sind NICHT dasselbe wie Stop-Orders. Ein Cluster zeigt,
  wo Liquiditaet bereitsteht -- nicht, wo Stops ausgeloest werden. Die Aussage
  "hier liegen Stops" bleibt ein Indiz, keine Messung.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd

# 0,1-%-Raster: fein genug fuer Level, grob genug fuer handhabbare Datenmengen
LOG_STEP = math.log(1.001)


def price_bucket(price: float) -> int:
    """Preis -> Rasterindex (logarithmisch, damit die relative Breite konstant ist)."""
    return int(math.floor(math.log(price) / LOG_STEP))


def bucket_price(idx: int) -> float:
    """Rasterindex -> Preis in der Mitte des Eimers."""
    return math.exp((idx + 0.5) * LOG_STEP)


def incremental_bands(pcts: Sequence[float], notionals: Sequence[float]
                      ) -> List[Tuple[float, float, float]]:
    """Kumulierte Tiefe -> inkrementelle Baender.

    Rueckgabe: ``[(pct_innen, pct_aussen, notional_in_diesem_band), ...]``,
    Prozente mit Vorzeichen (negativ = Bid-Seite).

    Beispiel: Ist bei -1 % kumuliert 300 Mio und bei -0,2 % kumuliert 80 Mio,
    dann liegen 220 Mio zwischen -0,2 % und -1 %.
    """
    order = sorted(zip(pcts, notionals), key=lambda x: abs(x[0]))
    out: List[Tuple[float, float, float]] = []
    prev_bid = 0.0
    prev_ask = 0.0
    prev_bid_pct = 0.0
    prev_ask_pct = 0.0
    for pct, cum in order:
        if not np.isfinite(cum):
            continue
        if pct < 0:
            inc = cum - prev_bid
            if inc > 0:
                out.append((prev_bid_pct, pct, inc))
            prev_bid, prev_bid_pct = cum, pct
        elif pct > 0:
            inc = cum - prev_ask
            if inc > 0:
                out.append((prev_ask_pct, pct, inc))
            prev_ask, prev_ask_pct = cum, pct
    return out


def snapshot_to_buckets(mid: float, pcts, notionals) -> Dict[int, float]:
    """Ein Orderbuch-Schnappschuss -> {Rasterindex: USD}.

    Der Betrag eines Bands wird gleichmaessig ueber die Eimer verteilt, die es
    ueberdeckt. Genauer geht es mit dieser Datenaufloesung nicht.
    """
    out: Dict[int, float] = {}
    if not np.isfinite(mid) or mid <= 0:
        return out
    for lo_pct, hi_pct, notional in incremental_bands(pcts, notionals):
        p_lo = mid * (1 + min(lo_pct, hi_pct) / 100.0)
        p_hi = mid * (1 + max(lo_pct, hi_pct) / 100.0)
        if p_lo <= 0 or p_hi <= p_lo:
            continue
        b_lo, b_hi = price_bucket(p_lo), price_bucket(p_hi)
        span = b_hi - b_lo + 1
        share = notional / span
        for b in range(b_lo, b_hi + 1):
            out[b] = out.get(b, 0.0) + share
    return out


def daily_map(depth: pd.DataFrame, mid: pd.Series) -> pd.DataFrame:
    """Rohe Tiefendaten -> Tageskarte.

    ``depth``: Spalten ``timestamp, percentage, notional``.
    ``mid``:   Mittelkurs-Zeitreihe (wird auf die Schnappschuesse gelegt).

    Rueckgabe: DataFrame ``day, bucket, notional`` -- Mittelwert je
    Schnappschuss, damit Tage mit mehr Datenpunkten nicht schwerer wiegen.
    """
    d = depth.copy()
    d["timestamp"] = pd.to_datetime(d["timestamp"], utc=True, format="mixed")
    d = d.sort_values("timestamp")
    m = mid.sort_index()
    d["mid"] = np.interp(d["timestamp"].astype("int64"),
                         m.index.astype("int64"), m.to_numpy())

    acc: Dict[Tuple[pd.Timestamp, int], float] = {}
    counts: Dict[pd.Timestamp, int] = {}
    for ts, grp in d.groupby("timestamp", sort=False):
        day = ts.normalize()
        counts[day] = counts.get(day, 0) + 1
        buckets = snapshot_to_buckets(float(grp["mid"].iloc[0]),
                                      grp["percentage"].to_numpy(),
                                      grp["notional"].to_numpy())
        for b, v in buckets.items():
            acc[(day, b)] = acc.get((day, b), 0.0) + v

    if not acc:
        return pd.DataFrame(columns=["day", "bucket", "notional"])
    rows = [(day, b, v / max(counts[day], 1)) for (day, b), v in acc.items()]
    return pd.DataFrame(rows, columns=["day", "bucket", "notional"])


class LiquidityMap:
    """Nachschlagewerk: wie viel USD lagen um einen Preis herum?"""

    def __init__(self, table: pd.DataFrame, window_days: int = 7):
        self.window = window_days
        t = table.copy()
        t["day"] = pd.to_datetime(t["day"], utc=True)
        self._by_day: Dict[pd.Timestamp, Dict[int, float]] = {}
        for day, grp in t.groupby("day"):
            self._by_day[day] = dict(zip(grp["bucket"], grp["notional"]))
        self._days = sorted(self._by_day)

    def _window_days(self, when: pd.Timestamp) -> List[pd.Timestamp]:
        day = pd.Timestamp(when).tz_convert("UTC").normalize()
        return [d for d in self._days if day - pd.Timedelta(days=self.window) <= d < day]

    def at(self, price: float, when: pd.Timestamp, width_pct: float = 0.3) -> float:
        """Mittlere Buchtiefe (USD) im Band ``price * (1 +/- width_pct/100)``.

        Nutzt nur Tage VOR ``when`` -- damit ist der Aufruf look-ahead-frei.
        """
        days = self._window_days(when)
        if not days or not np.isfinite(price) or price <= 0:
            return float("nan")
        b_lo = price_bucket(price * (1 - width_pct / 100.0))
        b_hi = price_bucket(price * (1 + width_pct / 100.0))
        total = 0.0
        for d in days:
            m = self._by_day[d]
            for b in range(b_lo, b_hi + 1):
                total += m.get(b, 0.0)
        return total / len(days)

    def void_ratio(self, price: float, when: pd.Timestamp, direction: int,
                   width_pct: float = 0.3, gap_pct: float = 0.5) -> float:
        """Tiefe JENSEITS des Levels im Verhaeltnis zur Tiefe davor.

        ``direction`` +1: jenseits heisst oberhalb (Widerstandsbruch nach oben).
        Kleine Werte = Loch hinter dem Level, der Kurs faellt schneller durch.
        """
        here = self.at(price, when, width_pct)
        beyond = self.at(price * (1 + direction * gap_pct / 100.0), when, width_pct)
        if not np.isfinite(here) or here <= 0:
            return float("nan")
        return beyond / here

    def profile(self, when: pd.Timestamp) -> pd.Series:
        """Ganze Karte als Serie ``Preis -> USD`` (fuer Diagnose und Plots)."""
        days = self._window_days(when)
        if not days:
            return pd.Series(dtype=float)
        agg: Dict[int, float] = {}
        for d in days:
            for b, v in self._by_day[d].items():
                agg[b] = agg.get(b, 0.0) + v
        idx = sorted(agg)
        return pd.Series([agg[b] / len(days) for b in idx],
                         index=[bucket_price(b) for b in idx])
