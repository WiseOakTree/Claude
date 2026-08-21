"""RENKO (OHLC, 1 % Box) + MACD-Kreuzung + Open Interest.

Aufbau nach docs/renko_macd_oi_spec.md -- vor der Rechnung festgelegt.

Nachgebaut wird das Chart-Setup: Renko mit OHLC-Quelle, Boxgroesse 1 % vom
Kurs, klassische 2-Boxen-Umkehr, MACD(12/26/9) auf den Bricks. Einstieg bei
MACD-Kreuzung, gefiltert ueber Open Interest.

Gerechnet wird jede Kombination zweimal:
  * **ehrlich**  -- Fill zum Schlusskurs der Bar, auf der der Brick entstand
  * **TV-Stil**  -- Fill am Brick-Level (das, was ein Chart-Strategietester tut)
"""
import sys, os, warnings, pickle
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
from dataclasses import replace
import numpy as np, pandas as pd

from prop_backtester.config import (BacktestConfig, CostConfig, ExecutionConfig,
                                    ManagementConfig, RenkoConfig, RiskConfig)
from prop_backtester.engine import run_backtest
from prop_backtester.renko import build_renko
from prop_backtester.renko_macd import filter_signals, macd_signals
from prop_backtester.renko_trail import brick_grid

from renko_trail import kennzahlen, t_wert, tage_ueber_limit, max_dd, S, V

OI = S + "oi/"
MAERKTE = ["btc", "eth", "sol", "xrp", "doge", "ada"]
START = pd.Timestamp("2023-01-01", tz="UTC")
GRENZE = pd.Timestamp("2025-01-01", tz="UTC")

BASIS = BacktestConfig(
    initial_balance=50_000.0,
    renko=RenkoConfig(mode="fixed", fixed_brick_pct=0.01, source="ohlc",
                      reversal_boxes=2.0),
    costs=CostConfig(fee_pct=0.0004, slippage_pct=0.0002, half_spread_pct=0.0002,
                     slippage_vol_mult=0.0, funding_rate_daily_pct=0.0003),
    risk=RiskConfig(risk_per_trade_pct=0.005, stop_bricks=2.0, max_leverage=5.0),
)

#: Reihenfolge der Berichte -- die Hauptdefinition steht in der Spezifikation.
HAUPT = "dOI 24h > 0 (Haupt)"
LESARTEN = ["ohne Filter", HAUPT, "dOI 1h > 0", "dOI 168h > 0",
            "OI > Mittel 24h", "dOI-Wert 24h > 0", "dOI 24h < 0 (Gegenteil)"]

MANAGEMENT = {
    "M0": ("Stop-and-Reverse, kein Stop", ManagementConfig()),
    "M1": ("harter Stop, 2 Boxen", ManagementConfig(hard_stop=True,
                                                    stop_slippage_pct=0.0005)),
    "M2": ("Stop + Break-even + Trailing", ManagementConfig(
        hard_stop=True, stop_slippage_pct=0.0005, breakeven_bricks=2.0,
        breakeven_offset_pct=0.0016, trail_bricks=2.0)),
}


def oi_masken(df):
    """Die sieben vorab festgelegten Lesarten von "positives Open Interest"."""
    sym_datei = OI + f"oi_{df.attrs['sym']}.csv"
    oi = pd.read_csv(sym_datei, index_col=0, parse_dates=True)
    oi = oi.reindex(df.index, method="ffill")
    menge = oi["sum_open_interest"].to_numpy(float)
    wert = oi["sum_open_interest_value"].to_numpy(float)

    def delta(x, h):
        d = np.full(len(x), np.nan)
        d[h:] = x[h:] - x[:-h]
        return d

    mittel24 = pd.Series(menge).rolling(24).mean().to_numpy()
    return {
        "ohne Filter": np.ones(len(df), dtype=bool),
        HAUPT: delta(menge, 24) > 0,
        "dOI 1h > 0": delta(menge, 1) > 0,
        "dOI 168h > 0": delta(menge, 168) > 0,
        "OI > Mittel 24h": menge > mittel24,
        "dOI-Wert 24h > 0": delta(wert, 24) > 0,
        "dOI 24h < 0 (Gegenteil)": delta(menge, 24) < 0,
    }


def rechne(cache=S + "renko_macd_oi.pkl"):
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    trades, konten, zaehl = [], [], []
    for sym in MAERKTE:
        voll = pd.read_csv(V + f"{sym}_1h.csv", index_col=0, parse_dates=True)
        voll = voll[voll.index >= START]
        voll.attrs["sym"] = sym
        masken_voll = oi_masken(voll)
        for periode, fenster in (("suche", voll.index < GRENZE),
                                 ("holdout", voll.index >= GRENZE)):
            df = voll[fenster]
            masken = {k: v[fenster] for k, v in masken_voll.items()}
            bricks = build_renko(df, BASIS.renko).bricks
            grid = brick_grid(bricks, len(df))
            roh = macd_signals(bricks)
            spanne = (df.index[-1] - df.index[0]).total_seconds()
            for oi_name, maske in masken.items():
                sig = filter_signals(roh, np.nan_to_num(maske, nan=False).astype(bool))
                zaehl.append({"markt": sym, "periode": periode, "oi": oi_name,
                              "signale": len(sig), "roh": len(roh),
                              "bricks": len(bricks)})
                if len(sig) == 0:
                    continue
                for m_key, (_, mgmt) in MANAGEMENT.items():
                    for fill in ("ehrlich", "tv"):
                        cfg = replace(
                            BASIS, management=replace(mgmt),
                            execution=ExecutionConfig(
                                mode="close" if fill == "ehrlich" else "signal_price"),
                        ).validate()
                        res = run_backtest(df, sig, cfg, grid=grid)
                        t = res.trades.copy()
                        if not len(t):
                            continue
                        t["markt"], t["periode"] = sym, periode
                        t["oi"], t["mgmt"], t["fill"] = oi_name, m_key, fill
                        trades.append(t)
                        n_tage, _ = tage_ueber_limit(res.equity)
                        im_markt = (t["exit_time"] - t["entry_time"]).dt.total_seconds().sum()
                        konten.append({
                            "markt": sym, "periode": periode, "oi": oi_name,
                            "mgmt": m_key, "fill": fill,
                            "rendite": res.final_balance / res.initial_balance - 1.0,
                            "max_dd": max_dd(res.equity, res.initial_balance),
                            "tage_ueber_3pct": n_tage, "im_markt": im_markt / spanne,
                            "n": len(t)})
        print(f"  {sym} fertig", flush=True)
    out = (pd.concat(trades, ignore_index=True), pd.DataFrame(konten),
           pd.DataFrame(zaehl))
    pickle.dump(out, open(cache, "wb"))
    return out


def zeile(t):
    k = kennzahlen(t)
    return (f"{k['n']:6d} {k['bp']:9.2f} {k['t_maerkte']:7.2f} "
            f"{k['maerkte_positiv']:d}/{k['maerkte']:<2d} {k['R']:7.3f} "
            f"{k['trefferquote']*100:7.1f}% {k['gewinn_R']:7.2f} {k['verlust_R']:7.2f}")


def kopf(titel):
    print("\n" + "=" * 104)
    print(titel)
    print("=" * 104)
    print(f"{'Aufbau':38s} {'n':>6s} {'bp/Trade':>9s} {'t(Mkt)':>7s} {'+Mkt':>5s} "
          f"{'Ø R':>7s} {'Treffer':>8s} {'ØGew R':>7s} {'ØVer R':>7s}")
    print("-" * 104)


if __name__ == "__main__":
    print("Rechne (oder lade Cache) ...", flush=True)
    tr, kt, zl = rechne()
    ohne_btc = [m for m in MAERKTE if m != "btc"]

    print("\n" + "=" * 104)
    print("Wie viele Signale erzeugt der Aufbau ueberhaupt? (Suchzeitraum)")
    print("=" * 104)
    z = zl[zl["periode"] == "suche"]
    print(f"Bricks je Markt: " +
          ", ".join(f"{r.markt}:{r.bricks}" for r in
                    z[z['oi'] == 'ohne Filter'].itertuples()))
    tab = z.pivot_table(index="oi", values="signale", aggfunc="sum")
    roh_n = int(z[z["oi"] == "ohne Filter"]["signale"].sum())
    for name, r in tab.iterrows():
        print(f"  {name:26s} {int(r['signale']):5d} Signale "
              f"({r['signale']/roh_n*100:5.1f} % von ungefiltert)")

    for periode, maerkte in (("suche", MAERKTE), ("holdout", ohne_btc)):
        d = tr[(tr["periode"] == periode) & (tr["markt"].isin(maerkte))]
        kopf(f"OI-Lesarten, ehrlicher Fill, harter Stop (M1) -- {periode.upper()}")
        for oi_name in LESARTEN:
            t = d[(d["oi"] == oi_name) & (d["mgmt"] == "M1") & (d["fill"] == "ehrlich")]
            if len(t):
                print(f"{oi_name:38s} {zeile(t)}")

    kopf("Managementstufen bei der Hauptdefinition, ehrlicher Fill -- SUCHE")
    d = tr[(tr["periode"] == "suche") & (tr["oi"] == HAUPT)
           & (tr["fill"] == "ehrlich")]
    for m_key, (label, _) in MANAGEMENT.items():
        t = d[d["mgmt"] == m_key]
        if len(t):
            print(f"{m_key + ' ' + label:38s} {zeile(t)}")

    print("\n" + "=" * 104)
    print("DIE ENTSCHEIDENDE ZAHL: Fill am Brick-Level gegen Fill zum Bar-Schluss")
    print("=" * 104)
    print(f"{'Aufbau':38s} {'TV-Stil bp':>11s} {'ehrlich bp':>11s} {'Differenz':>11s}")
    print("-" * 104)
    for periode in ("suche", "holdout"):
        d = tr[tr["periode"] == periode]
        for m_key in MANAGEMENT:
            t = d[(d["oi"] == HAUPT) & (d["mgmt"] == m_key)]
            tv = t[t["fill"] == "tv"]["return_pct"].mean() * 1e4
            eh = t[t["fill"] == "ehrlich"]["return_pct"].mean() * 1e4
            print(f"{periode + ' / ' + m_key:38s} {tv:11.2f} {eh:11.2f} {tv-eh:11.2f}")

    print("\n" + "=" * 104)
    print("Risiko-Treue und Tageslimit (Hauptdefinition, ehrlicher Fill, Suche)")
    print("=" * 104)
    print(f"{'Aufbau':38s} {'Verlust>1,2R':>13s} {'groesster':>10s} "
          f"{'Ø Tage <-3%':>12s} {'Ø Rendite':>10s}")
    print("-" * 104)
    for m_key, (label, _) in MANAGEMENT.items():
        t = tr[(tr["periode"] == "suche") & (tr["oi"] == HAUPT)
               & (tr["fill"] == "ehrlich") & (tr["mgmt"] == m_key)]
        k = kt[(kt["periode"] == "suche") & (kt["oi"] == HAUPT)
               & (kt["fill"] == "ehrlich") & (kt["mgmt"] == m_key)]
        if len(t):
            print(f"{m_key + ' ' + label:38s} {(t['r_multiple'] < -1.2).mean()*100:12.1f}% "
                  f"{t['r_multiple'].min():10.2f} {k['tage_ueber_3pct'].mean():12.1f} "
                  f"{k['rendite'].mean()*100:9.1f}%")

    print("\n" + "=" * 104)
    print("bp je Trade und Markt (Hauptdefinition, M1, ehrlich)")
    print("=" * 104)
    for periode in ("suche", "holdout"):
        t = tr[(tr["periode"] == periode) & (tr["oi"] == HAUPT)
               & (tr["mgmt"] == "M1") & (tr["fill"] == "ehrlich")]
        m = (t.groupby("markt")["return_pct"].mean() * 1e4).reindex(MAERKTE)
        n = t.groupby("markt").size().reindex(MAERKTE)
        print(f"  {periode:8s} " + "  ".join(
            f"{s}:{m[s]:+7.1f}({int(n[s]) if n[s]==n[s] else 0})" for s in MAERKTE))

    print("\nFERTIG")
