"""RENKO + MACD + OI mit fester Klammer: SL 3 Boxen, TP 6 Boxen, 1 % Risiko.

Aufbau nach docs/renko_macd_klammer_spec.md -- vor der Rechnung festgelegt.

Bei festem CRV 1:2 haengt alles an einer Zahl: der Trefferquote. Deshalb wird
sie zweimal gemessen -- fuer die Strategie und als **Basissatz** derselben
Maerkte (von jedem beliebigen Bar aus).
"""
import sys, os, warnings, pickle
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
from dataclasses import replace
import numpy as np, pandas as pd

from prop_backtester.config import ManagementConfig, RiskConfig
from prop_backtester.engine import run_backtest
from prop_backtester.renko import build_renko
from prop_backtester.renko_macd import filter_signals, macd_signals
from prop_backtester.renko_trail import brick_grid

from renko_trail import kennzahlen, t_wert, tage_ueber_limit, max_dd, S, V
from renko_macd_oi import BASIS, MAERKTE, START, GRENZE, HAUPT, oi_masken

BOX = 0.01          # Boxgroesse 1 %
STOP_BOXEN = 3.0    # Stop 3 Boxen = 3 %
ZIEL_R = 2.0        # Ziel 6 Boxen = 6 % = 2R
RISIKO = 0.01       # 1 % des Kontos je Trade
HORIZONT = 2160     # 90 Tage fuer den Basissatz


def klammer_risk(stop_boxen=STOP_BOXEN, ziel_r=ZIEL_R):
    return RiskConfig(risk_per_trade_pct=RISIKO, stop_bricks=stop_boxen,
                      max_leverage=5.0, tp_r_multiples=[ziel_r],
                      tp_take_fractions=[1.0])


def klammer_mgmt(dreht=False):
    return ManagementConfig(hard_stop=True, stop_slippage_pct=0.0005,
                            ignore_reverse_signals=not dreht)


KOMBIS = {
    "K1": ("OI-Filter, feste Klammer", True, False),
    "K2": ("OI-Filter, Klammer + Drehen", True, True),
    "K3": ("ohne OI-Filter, feste Klammer", False, False),
    "K4": ("ohne OI-Filter, Klammer + Drehen", False, True),
}


def basissatz(df, hoch_pct=0.06, tief_pct=0.03, horizont=HORIZONT):
    """Von JEDEM Bar aus: wird +hoch_pct vor -tief_pct erreicht?

    Gibt (treffer_long, treffer_short, unaufgeloest_long, unaufgeloest_short)
    als Anteile zurueck. Brutto, ohne Kosten -- es geht um die reine
    Kursfrage, nicht um Handelbarkeit.
    """
    c = df["close"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    n = len(c)
    erg = {}
    for richtung in (1, -1):
        treffer = offen = entschieden = 0
        for i in range(n - 1):
            e = c[i]
            if richtung == 1:
                ziel, stop = e * (1 + hoch_pct), e * (1 - tief_pct)
            else:
                ziel, stop = e * (1 - hoch_pct), e * (1 + tief_pct)
            j0, j1 = i + 1, min(i + 1 + horizont, n)
            hs, ls = h[j0:j1], l[j0:j1]
            if richtung == 1:
                t_ziel = np.argmax(hs >= ziel) if (hs >= ziel).any() else -1
                t_stop = np.argmax(ls <= stop) if (ls <= stop).any() else -1
            else:
                t_ziel = np.argmax(ls <= ziel) if (ls <= ziel).any() else -1
                t_stop = np.argmax(hs >= stop) if (hs >= stop).any() else -1
            if t_ziel < 0 and t_stop < 0:
                offen += 1
                continue
            entschieden += 1
            # Gleiche Bar -> Stop zaehlt (pessimistisch, wie in der Engine)
            if t_stop < 0 or (t_ziel >= 0 and t_ziel < t_stop):
                treffer += 1
        erg[richtung] = (treffer / max(entschieden, 1), offen / max(n - 1, 1),
                         entschieden)
    return erg


def rechne(cache=S + "renko_macd_klammer.pkl"):
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    trades, konten, basis, sens = [], [], [], []
    for sym in MAERKTE:
        voll = pd.read_csv(V + f"{sym}_1h.csv", index_col=0, parse_dates=True)
        voll = voll[voll.index >= START]
        voll.attrs["sym"] = sym
        masken_voll = oi_masken(voll)
        for periode, fenster in (("suche", voll.index < GRENZE),
                                 ("holdout", voll.index >= GRENZE)):
            df = voll[fenster]
            maske = np.nan_to_num(masken_voll[HAUPT][fenster], nan=False).astype(bool)
            bricks = build_renko(df, BASIS.renko).bricks
            grid = brick_grid(bricks, len(df))
            roh = macd_signals(bricks)
            gefiltert = filter_signals(roh, maske)
            spanne = (df.index[-1] - df.index[0]).total_seconds()

            b = basissatz(df)
            basis.append({"markt": sym, "periode": periode,
                          "long": b[1][0], "short": b[-1][0],
                          "offen_long": b[1][1], "n_long": b[1][2]})

            for key, (label, mit_oi, dreht) in KOMBIS.items():
                sig = gefiltert if mit_oi else roh
                if not len(sig):
                    continue
                cfg = replace(BASIS, risk=klammer_risk(),
                              management=klammer_mgmt(dreht)).validate()
                res = run_backtest(df, sig, cfg, grid=grid)
                t = res.trades.copy()
                if not len(t):
                    continue
                t["markt"], t["periode"], t["kombi"] = sym, periode, key
                trades.append(t)
                n_tage, _ = tage_ueber_limit(res.equity)
                im_markt = (t["exit_time"] - t["entry_time"]).dt.total_seconds().sum()
                konten.append({
                    "markt": sym, "periode": periode, "kombi": key,
                    "rendite": res.final_balance / res.initial_balance - 1.0,
                    "max_dd": max_dd(res.equity, res.initial_balance),
                    "tage_ueber_3pct": n_tage, "im_markt": im_markt / spanne,
                    "n": len(t)})

            # Empfindlichkeit: Ziel und Stop variiert (nur K1-Aufbau)
            for stop_b in (2.0, 3.0, 4.0):
                for ziel_r in (1.0, 2.0, 3.0, 4.0):
                    cfg = replace(BASIS, risk=klammer_risk(stop_b, ziel_r),
                                  management=klammer_mgmt(False)).validate()
                    res = run_backtest(df, gefiltert, cfg, grid=grid)
                    t = res.trades
                    if not len(t):
                        continue
                    sens.append({
                        "markt": sym, "periode": periode, "stop_boxen": stop_b,
                        "ziel_r": ziel_r, "n": len(t),
                        "bp": float(t["return_pct"].mean()) * 1e4,
                        "treffer": float((t["exit_reason"] == "ziel").mean()),
                        "R": float(t["r_multiple"].mean())})
        print(f"  {sym} fertig", flush=True)
    out = (pd.concat(trades, ignore_index=True), pd.DataFrame(konten),
           pd.DataFrame(basis), pd.DataFrame(sens))
    pickle.dump(out, open(cache, "wb"))
    return out


def binomial_p(treffer, n, p0):
    """Einseitiger Binomialtest: ist die Trefferquote ueber p0?"""
    from scipy import stats
    return float(stats.binomtest(int(treffer), int(n), p0, alternative="greater").pvalue)


if __name__ == "__main__":
    print("Rechne (oder lade Cache) ...", flush=True)
    tr, kt, bs, sn = rechne()
    ohne_btc = [m for m in MAERKTE if m != "btc"]

    print("\n" + "=" * 100)
    print("BASISSATZ: von JEDEM Bar aus -- wird +6 % vor -3 % erreicht?")
    print("=" * 100)
    print(f"{'Markt':8s} {'Periode':9s} {'long':>8s} {'short':>8s} "
          f"{'unaufgeloest':>13s} {'n':>9s}")
    print("-" * 100)
    for r in bs.itertuples():
        print(f"{r.markt:8s} {r.periode:9s} {r.long*100:7.1f}% {r.short*100:7.1f}% "
              f"{r.offen_long*100:12.1f}% {r.n_long:9d}")
    for p in ("suche", "holdout"):
        d = bs[bs["periode"] == p]
        print(f"  {p:8s} Mittel long {d['long'].mean()*100:.1f} %, "
              f"short {d['short'].mean()*100:.1f} %  (Theorie 33,3 %)")

    print("\n" + "=" * 100)
    print("DIE ENTSCHEIDENDE ZAHL: Trefferquote gegen Break-even und Basissatz")
    print("=" * 100)
    print(f"{'':3s} {'Aufbau':34s} {'n':>6s} {'Treffer':>8s} {'Basis':>7s} "
          f"{'bp/Trade':>9s} {'Ø R':>7s} {'t(Mkt)':>7s} {'Binomial p':>11s}")
    print("-" * 100)
    for periode, maerkte in (("suche", MAERKTE), ("holdout", ohne_btc)):
        print(f"--- {periode.upper()} " + "-" * 80)
        basis_p = bs[(bs["periode"] == periode) & (bs["markt"].isin(maerkte))]
        p0 = float((basis_p["long"].mean() + basis_p["short"].mean()) / 2)
        for key, (label, _, _) in KOMBIS.items():
            t = tr[(tr["periode"] == periode) & (tr["kombi"] == key)
                   & (tr["markt"].isin(maerkte))]
            if not len(t):
                continue
            entschieden = t[t["exit_reason"].isin(["ziel", "stop"])]
            treffer = int((entschieden["exit_reason"] == "ziel").sum())
            quote = treffer / max(len(entschieden), 1)
            k = kennzahlen(t)
            p = binomial_p(treffer, len(entschieden), p0)
            print(f"{key:3s} {label:34s} {k['n']:6d} {quote*100:7.1f}% "
                  f"{p0*100:6.1f}% {k['bp']:9.2f} {k['R']:7.3f} "
                  f"{k['t_maerkte']:7.2f} {p:11.3f}")

    print("\n" + "=" * 100)
    print("Wie die Trades enden und wie lange sie dauern (Suche, K1)")
    print("=" * 100)
    t = tr[(tr["periode"] == "suche") & (tr["kombi"] == "K1")]
    for grund, teil in t.groupby("exit_reason"):
        print(f"  {grund:8s} {len(teil)/len(t)*100:5.1f} %  "
              f"Ø {teil['bars_held'].mean():6.1f} Bars ({teil['bars_held'].mean()/24:5.1f} Tage)"
              f"  Ø {teil['r_multiple'].mean():+6.2f} R")

    print("\n" + "=" * 100)
    print("Konto-Ebene (1 % Risiko je Trade, 0,33x Nominal)")
    print("=" * 100)
    print(f"{'':3s} {'Periode':9s} {'Ø Rendite':>10s} {'Ø max DD':>9s} "
          f"{'Tage <-3%':>10s} {'Ø im Markt':>11s} {'Konten +':>9s}")
    print("-" * 100)
    for key in KOMBIS:
        for periode in ("suche", "holdout"):
            k = kt[(kt["kombi"] == key) & (kt["periode"] == periode)]
            if not len(k):
                continue
            print(f"{key:3s} {periode:9s} {k['rendite'].mean()*100:9.1f}% "
                  f"{k['max_dd'].mean()*100:8.1f}% {k['tage_ueber_3pct'].mean():10.1f} "
                  f"{k['im_markt'].mean()*100:10.1f}% "
                  f"{int((k['rendite']>0).sum()):4d}/{len(k)}")

    print("\n" + "=" * 100)
    print("EMPFINDLICHKEIT (keine Auswahl daraus!) -- bp je Trade, Suche / Holdout")
    print("=" * 100)
    for p in ("suche", "holdout"):
        d = sn[sn["periode"] == p]
        piv = d.pivot_table(index="stop_boxen", columns="ziel_r",
                            values="bp", aggfunc="mean")
        tref = d.pivot_table(index="stop_boxen", columns="ziel_r",
                             values="treffer", aggfunc="mean") * 100
        print(f"\n  {p.upper()} -- bp je Trade (Zeilen: Stop in Boxen, Spalten: Ziel in R)")
        print(piv.round(1).to_string())
        print(f"  {p.upper()} -- Trefferquote %")
        print(tref.round(1).to_string())

    print("\nFERTIG")
