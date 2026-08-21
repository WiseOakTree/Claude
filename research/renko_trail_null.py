"""RENKO-TRAIL, Nullmodell: dasselbe Management auf Zufallseinstiege.

Punkt 5 der Auswertung aus docs/renko_trail_spec.md. Gleiche Anzahl Signale,
gleiche Long/Short-Quote, Zeitpunkte gleichverteilt ueber dieselben Bars,
identisches Management, identische Kosten. 200 Ziehungen je Variante.

Damit ist die Frage entschieden, die eine Backtest-Kurve allein nie beantwortet:
Liegt das Ergebnis am Signal -- oder am Management, das jedes beliebige Signal
genauso behandelt haette?
"""
import sys, warnings, pickle, os
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from multiprocessing import Pool
from prop_backtester import VARIANTS, run_variant
from prop_backtester.engine import run_backtest
from prop_backtester.renko import build_renko, wilder_atr
from prop_backtester.renko_trail import brick_grid, variant_config, variant_signals

from renko_trail import BASIS, MAERKTE, GRENZE, V, S, mit_stop_slippage

ZIEHUNGEN = 200


def vorbereiten():
    """Je Markt und Periode: Bars, Gitter, ATR und die echten Signalzahlen."""
    welt = {}
    for sym in MAERKTE:
        voll = pd.read_csv(V + f"{sym}_1h.csv", index_col=0, parse_dates=True)
        for periode, df in (("suche", voll[voll.index < GRENZE]),
                            ("holdout", voll[voll.index >= GRENZE])):
            cfg = variant_config(VARIANTS["V0"], BASIS)
            bricks = build_renko(df, cfg.renko).bricks
            atr = wilder_atr(df, cfg.renko.atr_period).to_numpy() * cfg.renko.atr_multiplier
            gueltig = np.where(np.isfinite(atr) & (atr > 0))[0]
            plan = {}
            for key, v in VARIANTS.items():
                sig = variant_signals(v, bricks, variant_config(v, BASIS))
                if len(sig):
                    plan[key] = (len(sig), float((sig["target"] > 0).mean()))
                else:
                    plan[key] = (0, 0.5)
            welt[(sym, periode)] = {
                "df": df, "grid": brick_grid(bricks, len(df)),
                "atr": atr, "gueltig": gueltig, "plan": plan,
            }
    return welt


WELT = None


def init():
    global WELT
    WELT = vorbereiten()


def zufalls_signale(w, n, long_anteil, rng):
    """n Einstiege, gleichverteilt ueber dieselben Bars, gleiche Long-Quote."""
    if n == 0:
        return pd.DataFrame(columns=["time", "src_index", "price", "target", "brick_size"])
    idx = np.sort(rng.choice(w["gueltig"], size=min(n, len(w["gueltig"])), replace=False))
    ziel = np.where(rng.random(len(idx)) < long_anteil, 1, -1)
    df = w["df"]
    return pd.DataFrame({
        "time": df.index.to_numpy()[idx],
        "src_index": idx,
        "price": df["close"].to_numpy()[idx],
        "target": ziel,
        "brick_size": w["atr"][idx],
    })


def eine_ziehung(d):
    """Eine Ziehung ueber alle Maerkte, Perioden und Varianten."""
    rng = np.random.default_rng(10_000 + d)
    zeilen = []
    for (sym, periode), w in WELT.items():
        for key, v in VARIANTS.items():
            n, anteil = w["plan"][key]
            sig = zufalls_signale(w, n, anteil, rng)
            cfg = variant_config(mit_stop_slippage(v), BASIS)
            res = run_backtest(w["df"], sig, cfg, grid=w["grid"])
            t = res.trades
            if not len(t):
                continue
            zeilen.append({
                "ziehung": d, "markt": sym, "periode": periode, "variante": key,
                "n": len(t),
                "bp_summe": float(t["return_pct"].sum()) * 1e4,
                "r_summe": float(t["r_multiple"].sum()),
                "bruch": int((t["r_multiple"] < -1.2).sum()),
                "q05_beitrag": float(np.quantile(t["r_multiple"], 0.05)),
            })
    return zeilen


if __name__ == "__main__":
    cache = S + "renko_trail_null.pkl"
    if os.path.exists(cache):
        roh = pickle.load(open(cache, "rb"))
    else:
        with Pool(4, initializer=init) as pool:
            teile = []
            for i, z in enumerate(pool.imap_unordered(eine_ziehung, range(ZIEHUNGEN))):
                teile.extend(z)
                print(f"  Ziehung {i+1}/{ZIEHUNGEN}", flush=True)
        roh = pd.DataFrame(teile)
        pickle.dump(roh, open(cache, "wb"))

    echt, _ = pickle.load(open(S + "renko_trail.pkl", "rb"))
    ohne_btc = [m for m in MAERKTE if m != "btc"]

    for periode, maerkte in (("suche", MAERKTE), ("holdout", ohne_btc)):
        print("\n" + "=" * 96)
        print(f"NULLMODELL -- Zufallseinstiege mit identischem Management ({periode})")
        print("=" * 96)
        print(f"{'':3s} {'Aufbau':34s} {'echt bp':>9s} {'Zufall Ø':>9s} "
              f"{'5%':>8s} {'95%':>8s} {'Perzentil':>10s}")
        print("-" * 96)
        n_roh = roh[(roh["periode"] == periode) & (roh["markt"].isin(maerkte))]
        e_roh = echt[(echt["periode"] == periode) & (echt["markt"].isin(maerkte))]
        for key, v in VARIANTS.items():
            e = e_roh[e_roh["variante"] == key]
            if not len(e):
                continue
            echt_bp = e["return_pct"].mean() * 1e4
            g = n_roh[n_roh["variante"] == key].groupby("ziehung")[["bp_summe", "n"]].sum()
            if not len(g):
                continue
            verteilung = (g["bp_summe"] / g["n"]).to_numpy()
            perzentil = float((verteilung < echt_bp).mean() * 100)
            print(f"{key:3s} {v.label:34s} {echt_bp:9.2f} {verteilung.mean():9.2f} "
                  f"{np.quantile(verteilung, 0.05):8.2f} "
                  f"{np.quantile(verteilung, 0.95):8.2f} {perzentil:9.1f}%")

    print("\n" + "=" * 96)
    print("FRAGE B im Nullmodell -- Anteil Trades mit Verlust > 1,2R (Suchzeitraum)")
    print("=" * 96)
    print(f"{'':3s} {'Aufbau':34s} {'echt':>8s} {'Zufall Ø':>9s} {'Perzentil':>10s}")
    print("-" * 96)
    n_roh = roh[roh["periode"] == "suche"]
    e_roh = echt[echt["periode"] == "suche"]
    for key, v in VARIANTS.items():
        e = e_roh[e_roh["variante"] == key]
        g = n_roh[n_roh["variante"] == key].groupby("ziehung")[["bruch", "n"]].sum()
        if not len(e) or not len(g):
            continue
        echt_q = float((e["r_multiple"] < -1.2).mean())
        vert = (g["bruch"] / g["n"]).to_numpy()
        print(f"{key:3s} {v.label:34s} {echt_q*100:7.1f}% {vert.mean()*100:8.1f}% "
              f"{float((vert < echt_q).mean()*100):9.1f}%")

    print("\nFERTIG")
