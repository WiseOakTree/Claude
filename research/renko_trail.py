"""RENKO-TRAIL: Was leistet Handelsmanagement?

Aufbau nach docs/renko_trail_spec.md -- vor der Rechnung festgelegt.

Frage A: Veraendert Management den Erwartungswert je Trade?
Frage B: Bringt Management den Trade zu dem Ergebnis, das geplant war?
"""
import sys, warnings, pickle, os
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import VARIANTS, run_variant
from prop_backtester.config import BacktestConfig, CostConfig, RiskConfig

S = "/tmp/claude-0/-home-user/6ea4b953-8381-58a1-a843-0b428058fee5/scratchpad/"
V = S + "vol/"
MAERKTE = ["btc", "eth", "sol", "bnb", "xrp", "ada", "doge", "link", "ltc",
           "avax", "dot", "bch"]
GRENZE = pd.Timestamp("2025-01-01", tz="UTC")

# Kosten laut Spezifikation: 8 bp je Seite, Funding 0,01 % je 8 h.
BASIS = BacktestConfig(
    initial_balance=50_000.0,
    costs=CostConfig(fee_pct=0.0004, slippage_pct=0.0002, half_spread_pct=0.0002,
                     slippage_vol_mult=0.0, funding_rate_daily_pct=0.0003),
    risk=RiskConfig(risk_per_trade_pct=0.005, stop_bricks=2.0, max_leverage=5.0),
)
STOP_SLIP = 0.0005   # zusaetzliche Slippage auf Stop-Ausfuehrungen


def mit_stop_slippage(v):
    """Stop-Slippage aus der Spezifikation auf jede Stufe mit hartem Stop."""
    from dataclasses import replace
    if not v.management.hard_stop:
        return v
    return replace(v, management=replace(v.management, stop_slippage_pct=STOP_SLIP))


def tage_ueber_limit(eq, limit=0.03):
    """Handelstage, an denen die Equity um mehr als ``limit`` unter den
    Vortagesschluss faellt -- gemessen am Intrabar-Tief (Kraken-Tageslimit)."""
    tag = eq.index.floor("1D")
    schluss = eq["equity_close"].groupby(tag).last()
    tief = eq["equity_low"].groupby(tag).min()
    vortag = schluss.shift(1)
    verlust = tief / vortag - 1.0
    return int((verlust < -limit).sum()), float(verlust.min())


def max_dd(eq, start):
    hoch = eq["equity_close"].cummax().clip(lower=start)
    return float((1.0 - eq["equity_low"] / hoch).max())


def rechne(cache=S + "renko_trail.pkl"):
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    trades, konten = [], []
    for sym in MAERKTE:
        voll = pd.read_csv(V + f"{sym}_1h.csv", index_col=0, parse_dates=True)
        for periode, df in (("suche", voll[voll.index < GRENZE]),
                            ("holdout", voll[voll.index >= GRENZE])):
            spanne = (df.index[-1] - df.index[0]).total_seconds()
            for key, v in VARIANTS.items():
                res = run_variant(df, mit_stop_slippage(v), BASIS)
                t = res.trades.copy()
                t["markt"], t["variante"], t["periode"] = sym, key, periode
                trades.append(t)
                n_tage, schlimmster = tage_ueber_limit(res.equity)
                im_markt = (t["exit_time"] - t["entry_time"]).dt.total_seconds().sum()
                konten.append({
                    "markt": sym, "variante": key, "periode": periode,
                    "start": res.initial_balance, "ende": res.final_balance,
                    "rendite": res.final_balance / res.initial_balance - 1.0,
                    "max_dd": max_dd(res.equity, res.initial_balance),
                    "tage_ueber_3pct": n_tage, "schlimmster_tag": schlimmster,
                    "im_markt": im_markt / spanne, "n": len(t),
                })
            print(f"  {sym:5s} {periode:8s} fertig", flush=True)
    out = (pd.concat(trades, ignore_index=True), pd.DataFrame(konten))
    pickle.dump(out, open(cache, "wb"))
    return out


def t_wert(x):
    x = np.asarray(x, float)
    if len(x) < 2 or x.std(ddof=1) == 0:
        return np.nan
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))


def kennzahlen(t):
    """Alle vorab festgelegten Groessen fuer eine Trade-Menge."""
    bp = t["return_pct"].to_numpy() * 1e4
    r = t["r_multiple"].to_numpy()
    gewinne, verluste = r[r > 0], r[r <= 0]
    je_markt = t.groupby("markt")["return_pct"].mean() * 1e4
    return {
        "n": len(t),
        "bp": bp.mean(),
        "t_trades": t_wert(bp),
        "t_maerkte": t_wert(je_markt.to_numpy()),
        "maerkte_positiv": int((je_markt > 0).sum()),
        "maerkte": len(je_markt),
        "R": r.mean(),
        "trefferquote": len(gewinne) / len(r) if len(r) else np.nan,
        "gewinn_R": gewinne.mean() if len(gewinne) else np.nan,
        "verlust_R": verluste.mean() if len(verluste) else np.nan,
        "bruch_1_2R": float((r < -1.2).mean()),
        "q05_R": float(np.quantile(r, 0.05)),
        "min_R": float(r.min()),
    }


def tabelle(df, titel, maerkte=None):
    if maerkte is not None:
        df = df[df["markt"].isin(maerkte)]
    print("\n" + "=" * 108)
    print(titel)
    print("=" * 108)
    print(f"{'':3s} {'Aufbau':34s} {'n':>6s} {'bp/Trade':>9s} {'t(Tr)':>6s} "
          f"{'t(Mkt)':>6s} {'+Mkt':>5s} {'Ø R':>7s} {'Treffer':>8s} "
          f"{'ØGew R':>7s} {'ØVer R':>7s}")
    print("-" * 108)
    zeilen = {}
    for key, v in VARIANTS.items():
        t = df[df["variante"] == key]
        if not len(t):
            continue
        k = kennzahlen(t)
        zeilen[key] = k
        print(f"{key:3s} {v.label:34s} {k['n']:6d} {k['bp']:9.2f} "
              f"{k['t_trades']:6.2f} {k['t_maerkte']:6.2f} "
              f"{k['maerkte_positiv']:2d}/{k['maerkte']:<2d} {k['R']:7.3f} "
              f"{k['trefferquote']*100:7.1f}% {k['gewinn_R']:7.2f} {k['verlust_R']:7.2f}")
    return zeilen


def risiko_tabelle(df, titel, maerkte=None):
    if maerkte is not None:
        df = df[df["markt"].isin(maerkte)]
    print("\n" + "=" * 96)
    print(titel)
    print("=" * 96)
    print(f"{'':3s} {'Aufbau':34s} {'Verlust>1,2R':>13s} {'5%-Quantil R':>13s} "
          f"{'groesster Verlust':>18s}")
    print("-" * 96)
    for key, v in VARIANTS.items():
        t = df[df["variante"] == key]
        if not len(t):
            continue
        k = kennzahlen(t)
        print(f"{key:3s} {v.label:34s} {k['bruch_1_2R']*100:12.1f}% "
              f"{k['q05_R']:13.2f} {k['min_R']:18.2f}")


def gruende(df, titel):
    print("\n" + "=" * 96)
    print(titel)
    print("=" * 96)
    tab = (df.groupby(["variante", "exit_reason"]).size()
             .unstack(fill_value=0))
    tab = tab.div(tab.sum(axis=1), axis=0) * 100
    print(tab.round(1).to_string())


def konto_tabelle(k, titel, maerkte=None):
    if maerkte is not None:
        k = k[k["markt"].isin(maerkte)]
    print("\n" + "=" * 96)
    print(titel)
    print("=" * 96)
    print(f"{'':3s} {'Aufbau':34s} {'Ø Rendite':>10s} {'Ø max DD':>9s} "
          f"{'Tage <-3%':>10s} {'Ø im Markt':>11s}")
    print("-" * 96)
    for key, v in VARIANTS.items():
        z = k[k["variante"] == key]
        if not len(z):
            continue
        print(f"{key:3s} {v.label:34s} {z['rendite'].mean()*100:9.1f}% "
              f"{z['max_dd'].mean()*100:8.1f}% {z['tage_ueber_3pct'].mean():10.1f} "
              f"{z['im_markt'].mean()*100:10.1f}%")


if __name__ == "__main__":
    print("Rechne (oder lade Cache) ...", flush=True)
    tr, kt = rechne()
    suche = tr[tr["periode"] == "suche"]
    hold = tr[tr["periode"] == "holdout"]
    ohne_btc = [m for m in MAERKTE if m != "btc"]

    tabelle(suche, "FRAGE A -- Erwartungswert, SUCHZEITRAUM (12 Maerkte, bis 2024-12-31)")
    tabelle(hold, "FRAGE A -- HOLDOUT ab 2025-01-01 (11 Maerkte, BTC ausgeschlossen)",
            maerkte=ohne_btc)
    tabelle(hold, "nachrichtlich: BTC-Holdout allein (als Holdout verbraucht)",
            maerkte=["btc"])

    risiko_tabelle(suche, "FRAGE B -- Risiko-Treue, SUCHZEITRAUM")
    risiko_tabelle(hold, "FRAGE B -- Risiko-Treue, HOLDOUT (11 Maerkte)",
                   maerkte=ohne_btc)

    gruende(suche, "Wie die Trades enden (% je Variante, Suchzeitraum)")
    konto_tabelle(kt[kt["periode"] == "suche"], "Konto-Ebene, Suchzeitraum")
    konto_tabelle(kt[kt["periode"] == "holdout"], "Konto-Ebene, Holdout (11 Maerkte)",
                  maerkte=ohne_btc)

    print("\n" + "=" * 96)
    print("bp je Trade, je Markt und Variante (Suchzeitraum)")
    print("=" * 96)
    m = (suche.groupby(["markt", "variante"])["return_pct"].mean() * 1e4).unstack()
    print(m.reindex(MAERKTE).round(1).to_string())

    print("\n" + "=" * 96)
    print("bp je Trade, je Markt und Variante (Holdout)")
    print("=" * 96)
    m = (hold.groupby(["markt", "variante"])["return_pct"].mean() * 1e4).unstack()
    print(m.reindex(MAERKTE).round(1).to_string())

    print("\nFERTIG")
