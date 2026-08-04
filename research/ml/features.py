"""Merkmale fuer jedes Ausbruch-Ereignis -- ausschliesslich zum Signalzeitpunkt bekannt.

Jede Groesse benutzt nur Daten bis einschliesslich Bar t. Der Ausgang
(Folgerendite) kommt getrennt und wird nie als Merkmal verwendet.
"""
import sys; sys.path.insert(0, "/home/user/Claude/src")
import numpy as np, pandas as pd
from prop_backtester import levels
from prop_backtester.renko import wilder_atr


def build(df: pd.DataFrame, min_touch: int = 4, horizon: int = 24) -> pd.DataFrame:
    o = df["open"].to_numpy(float); h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float);  c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float)
    n = len(df)
    atr = wilder_atr(df, 14).to_numpy(float)
    vol_ma = pd.Series(v).rolling(50).mean().to_numpy()
    idx = df.index

    by = levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)
    ev = levels.breakout_events(by, df, min_touch=min_touch)

    rows = []
    for (t, d, tc, lvl) in ev:
        if t + horizon >= n or not np.isfinite(atr[t]) or atr[t] <= 0:
            continue
        act = by.get(t - 1, ())
        strong = [x for x in act if x[2] >= min_touch]
        # naechstes Gegenlevel in Handelsrichtung
        opp = levels.nearest_opposite(by, t - 1, c[t], d, min_touch=2)
        # naechstes Level GEGEN die Richtung (potenzieller Widerstand im Weg)
        same = [x[0] for x in strong
                if (d > 0 and x[0] > c[t]) or (d < 0 and x[0] < c[t])]
        nearest_ahead = (min(same, key=lambda p: abs(p - c[t])) if same else np.nan)

        def ret(k):
            return (c[t] / c[t - k] - 1) * 1e4 if t - k >= 0 else np.nan

        rows.append(dict(
            t=t, time=idx[t], direction=d, touches=tc,
            # wie tief geht der Bruch
            pen_atr=abs(c[t] - lvl) / atr[t],
            # Volatilitaetsregime
            atr_rel=atr[t] / c[t] * 1e4,
            atr_chg=atr[t] / atr[t - 24] if t >= 24 and atr[t - 24] > 0 else np.nan,
            # Kursverlauf davor (Momentum in Handelsrichtung)
            ret_1=ret(1) * d, ret_6=ret(6) * d, ret_24=ret(24) * d,
            ret_72=ret(72) * d, ret_168=ret(168) * d,
            # Bar-Struktur
            bar_range_atr=(h[t] - l[t]) / atr[t],
            close_pos=(c[t] - l[t]) / max(h[t] - l[t], 1e-9),
            body_frac=abs(c[t] - o[t]) / max(h[t] - l[t], 1e-9),
            # Volumen
            vol_ratio=v[t] / vol_ma[t] if np.isfinite(vol_ma[t]) and vol_ma[t] > 0 else np.nan,
            # Umfeld
            n_strong=len(strong), n_levels=len(act),
            dist_opp_atr=abs(opp - c[t]) / atr[t] if np.isfinite(opp) else np.nan,
            dist_ahead_atr=(abs(nearest_ahead - c[t]) / atr[t]
                            if np.isfinite(nearest_ahead) else np.nan),
            # Lage im 24h-Fenster
            pos_24=((c[t] - l[max(0, t - 24):t + 1].min())
                    / max(h[max(0, t - 24):t + 1].max() - l[max(0, t - 24):t + 1].min(), 1e-9)),
            # Zeit
            hour=idx[t].hour, dow=idx[t].dayofweek,
            # ZIEL -- nie als Merkmal verwenden
            y=(c[t + horizon] / c[t] - 1) * d * 1e4,
        ))
    return pd.DataFrame(rows)


FEATURES = ["direction", "touches", "pen_atr", "atr_rel", "atr_chg",
            "ret_1", "ret_6", "ret_24", "ret_72", "ret_168",
            "bar_range_atr", "close_pos", "body_frac", "vol_ratio",
            "n_strong", "n_levels", "dist_opp_atr", "dist_ahead_atr",
            "pos_24", "hour", "dow"]

if __name__ == "__main__":
    V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
    full = pd.read_csv(V + "btc_1h.csv", index_col=0, parse_dates=True)
    for mt in (4, 6):
        X = build(full, min_touch=mt)
        X.to_csv(f"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/ml/feat_btc_t{mt}.csv", index=False)
        s = X[X.time < "2025-01-01"]
        print(f"min_touch={mt}: {len(X)} Ereignisse gesamt, davon {len(s)} im Suchzeitraum, "
              f"Basis-Erwartung {s.y.mean():+.1f} bp")
    E = build(pd.read_csv(V + "eth_1h.csv", index_col=0, parse_dates=True), min_touch=4)
    E.to_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/ml/feat_eth_t4.csv", index=False)
    print(f"ETH min_touch=4: {len(E)} Ereignisse, Basis {E.y.mean():+.1f} bp")
