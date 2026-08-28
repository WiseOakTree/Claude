"""Dieselbe Leiter, aber MACD auf HEIKIN-ASHI-Kerzen (1h und 4h).

Ergaenzung zu liq_macd.py. Zwei Fragen:
  1. Aendert HA das Ergebnis der Methode?
  2. Wie gross ist die Abrechnungsfalle bei GENAU diesem Aufbau?
     (Signal auf HA, aber Fill zum echten Kurs -- gegen die geschoente
      Variante, die auch mit HA-Preisen abrechnet.)
"""
import sys, os, warnings, pickle
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

from prop_backtester import levels
from prop_backtester.renko import wilder_atr
from liq_macd import (S, V, MAERKTE, GRENZE, ZIEL, STOP, MAXH, KOSTEN,
                      MIN_TOUCH, NAEHE_ATR, macd, handeln, zufall)


def heikin_ashi(df):
    """HA-Kerzen. HA_close ist KEIN handelbarer Preis -- nur fuer Signale."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    ha_c = (o + h + l + c) / 4.0
    ha_o = np.empty(len(c))
    ha_o[0] = (o[0] + c[0]) / 2.0
    for i in range(1, len(c)):
        ha_o[i] = (ha_o[i - 1] + ha_c[i - 1]) / 2.0
    ha_h = np.maximum.reduce([h, ha_o, ha_c])
    ha_l = np.minimum.reduce([l, ha_o, ha_c])
    return pd.DataFrame({"open": ha_o, "high": ha_h, "low": ha_l, "close": ha_c},
                        index=df.index)


def bausteine_ha(df):
    """Wie liq_macd.bausteine, aber MACD auf HA-Schlusskursen."""
    ha = heikin_ashi(df)
    n = len(df)
    h1 = macd(ha["close"].to_numpy())
    kreuz = np.zeros(n, dtype=int)
    kreuz[1:] = np.where((h1[1:] > 0) & (h1[:-1] <= 0), 1,
                         np.where((h1[1:] < 0) & (h1[:-1] >= 0), -1, 0))
    kreuz[:40] = 0

    # 4h: echte 4h-Kerzen bilden, DARAUF HA rechnen, dann MACD -- so wie es
    # der Chart macht. shift(1), weil der 4h-Wert erst zum Kerzenschluss steht.
    r4 = df.resample("4h").agg({"open": "first", "high": "max",
                                "low": "min", "close": "last"}).dropna()
    ha4 = heikin_ashi(r4)
    h4 = pd.Series(macd(ha4["close"].to_numpy()), index=ha4.index).shift(1)
    trend4 = np.sign(h4.reindex(df.index, method="ffill").fillna(0).to_numpy()).astype(int)

    atr = wilder_atr(df, 14).to_numpy(float)
    by_bar = levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)
    c = df["close"].to_numpy(float)
    oben = np.full(n, np.inf); unten = np.full(n, np.inf)
    for t in range(n):
        lv = by_bar.get(t)
        if not lv:
            continue
        p = c[t]
        for preis, art, touch, letzter in lv:
            if touch < MIN_TOUCH:
                continue
            d = abs(preis - p)
            if preis >= p:
                oben[t] = min(oben[t], d)
            else:
                unten[t] = min(unten[t], d)
    with np.errstate(invalid="ignore"):
        nah_oben = np.nan_to_num(oben <= NAEHE_ATR * atr).astype(bool)
        nah_unten = np.nan_to_num(unten <= NAEHE_ATR * atr).astype(bool)
    return dict(kreuz=kreuz, trend4=trend4, atr=atr,
                nah_oben=nah_oben, nah_unten=nah_unten), ha


def signale(b, stufe, n):
    k, t4 = b["kreuz"], b["trend4"]
    if stufe == "H1":
        return k.copy()
    if stufe == "H2":
        return np.where(k == t4, k, 0)
    if stufe == "H3a":
        basis = np.where(k == t4, k, 0)
        return np.where(np.where(basis == 1, b["nah_unten"], b["nah_oben"]), basis, 0)
    if stufe == "H3b":
        basis = np.where(k == t4, k, 0)
        return np.where(np.where(basis == 1, b["nah_oben"], b["nah_unten"]), basis, 0)
    raise ValueError(stufe)


def rechne(cache=S + "liq_macd_ha.pkl"):
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    alle, kontrolle = [], []
    for sym in MAERKTE:
        voll = pd.read_csv(V + f"{sym}_1h.csv", index_col=0, parse_dates=True)
        b_voll, ha_voll = bausteine_ha(voll)
        for periode, maske in (("suche", voll.index < GRENZE),
                               ("holdout", voll.index >= GRENZE)):
            df, ha = voll[maske], ha_voll[maske]
            b = {k: (v[maske] if isinstance(v, np.ndarray) else v)
                 for k, v in b_voll.items()}
            for stufe in ("H1", "H2", "H3a", "H3b"):
                sig = signale(b, stufe, len(df))
                for kost in ("brutto", "8bp", "12bp"):
                    t = handeln(df, sig, kost)          # Fill zum ECHTEN Kurs
                    if len(t):
                        t["markt"], t["periode"], t["stufe"], t["kosten"] = \
                            sym, periode, stufe, kost
                        t["abrechnung"] = "echt"
                        alle.append(t)
                # Die Falle: dieselben Signale, aber mit HA-Preisen abgerechnet
                t = handeln(ha, sig, "12bp")
                if len(t):
                    t["markt"], t["periode"], t["stufe"], t["kosten"] = \
                        sym, periode, stufe, "12bp"
                    t["abrechnung"] = "HA-Preise"
                    alle.append(t)
                nz = int((sig != 0).sum())
                if nz > 10:
                    la = float((sig == 1).sum()) / nz
                    q, bp = zufall(df, nz, la)
                    kontrolle.append({"markt": sym, "periode": periode,
                                      "stufe": stufe, "quote": q, "bp": bp})
        print(f"  {sym} fertig", flush=True)
    out = (pd.concat(alle, ignore_index=True), pd.DataFrame(kontrolle))
    pickle.dump(out, open(cache, "wb"))
    return out


NAMEN = {"H1": "nur 1h-MACD auf HA",
         "H2": "1h + 4h HA gleichgerichtet",
         "H3a": "H2 + Einstieg AM Level",
         "H3b": "H2 + Level als Ziel"}

if __name__ == "__main__":
    print("Rechne (oder lade Cache) ...", flush=True)
    tr, kt = rechne()
    alt, _ = pickle.load(open(S + "liq_macd.pkl", "rb"))
    ohne_btc = [m for m in MAERKTE if m != "btc"]
    echt = tr[tr["abrechnung"] == "echt"]

    for periode, maerkte in (("SUCHE", MAERKTE), ("HOLDOUT", ohne_btc)):
        print("\n" + "=" * 112)
        print(f"MACD AUF HEIKIN ASHI -- {periode} (Fill zum ECHTEN Kurs, 12 bp)")
        print("=" * 112)
        print(f"{'':5s} {'Aufbau':30s} {'n':>6s} {'Treffer':>8s} {'brutto bp':>9s} "
              f"{'netto bp':>9s} {'t':>7s} {'+Mkt':>5s} {'Ø Dauer':>8s}")
        print("-" * 112)
        d = echt[(echt["periode"] == periode.lower()) & (echt["kosten"] == "12bp")
                 & (echt["markt"].isin(maerkte))]
        for st in ("H1", "H2", "H3a", "H3b"):
            t = d[d["stufe"] == st]
            if not len(t):
                continue
            ent = t[t["grund"].isin(["ziel", "stop"])]
            q = (ent["grund"] == "ziel").mean() if len(ent) else np.nan
            x = t["netto_bp"].to_numpy()
            tw = x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
            jm = t.groupby("markt")["netto_bp"].mean()
            print(f"{st:5s} {NAMEN[st]:30s} {len(t):6d} {q*100:7.1f}% "
                  f"{t['brutto_bp'].mean():9.2f} {x.mean():9.2f} {tw:7.2f} "
                  f"{int((jm>0).sum())}/{len(jm)} {t['stunden'].mean():7.1f}h")
        k = kt[(kt["periode"] == periode.lower()) & (kt["markt"].isin(maerkte))]
        print(f"{'H0':5s} {'Zufallseinstieg (Kontrolle)':30s} {'':6s} "
              f"{k['quote'].mean()*100:7.1f}% {'':9s} {k['bp'].mean():9.2f}")

    print("\n" + "=" * 112)
    print("HEIKIN ASHI GEGEN ECHTE KERZEN -- derselbe Aufbau, netto bp (12 bp)")
    print("=" * 112)
    print(f"{'Aufbau':34s} {'echte Kerzen':>14s} {'Heikin Ashi':>13s} "
          f"{'Differenz':>11s} {'Signale echt':>13s} {'Signale HA':>11s}")
    print("-" * 112)
    paare = [("L1", "H1", "nur 1h-MACD"), ("L2", "H2", "1h + 4h gleichgerichtet"),
             ("L3a", "H3a", "+ Einstieg AM Level"), ("L3b", "H3b", "+ Level als Ziel")]
    for periode, maerkte in (("suche", MAERKTE), ("holdout", ohne_btc)):
        print(f"  --- {periode.upper()}")
        for a, hh, name in paare:
            ta = alt[(alt["stufe"] == a) & (alt["periode"] == periode)
                     & (alt["kosten"] == "12bp") & (alt["markt"].isin(maerkte))]
            th = echt[(echt["stufe"] == hh) & (echt["periode"] == periode)
                      & (echt["kosten"] == "12bp") & (echt["markt"].isin(maerkte))]
            if not len(ta) or not len(th):
                continue
            print(f"  {name:32s} {ta['netto_bp'].mean():14.2f} "
                  f"{th['netto_bp'].mean():13.2f} "
                  f"{th['netto_bp'].mean()-ta['netto_bp'].mean():+11.2f} "
                  f"{len(ta):13d} {len(th):11d}")

    print("\n" + "=" * 112)
    print("DIE ABRECHNUNGSFALLE bei GENAU deinem Aufbau")
    print("=" * 112)
    print("Dieselben HA-Signale, einmal zum echten Kurs gefuellt, einmal mit HA-Preisen.")
    print(f"\n{'Aufbau':34s} {'echt gefuellt':>14s} {'mit HA-Preisen':>15s} {'Verzerrung':>12s}")
    print("-" * 112)
    for periode in ("suche", "holdout"):
        print(f"  --- {periode.upper()}")
        for st in ("H1", "H2", "H3a", "H3b"):
            e = tr[(tr["stufe"] == st) & (tr["periode"] == periode)
                   & (tr["abrechnung"] == "echt") & (tr["kosten"] == "12bp")]
            f = tr[(tr["stufe"] == st) & (tr["periode"] == periode)
                   & (tr["abrechnung"] == "HA-Preise")]
            if not len(e) or not len(f):
                continue
            print(f"  {NAMEN[st]:32s} {e['netto_bp'].mean():14.2f} "
                  f"{f['netto_bp'].mean():15.2f} "
                  f"{f['netto_bp'].mean()-e['netto_bp'].mean():+12.2f} bp")

    print("\n" + "=" * 112)
    print("MARGINALER BEITRAG DER BAUSTEINE AUF HA")
    print("=" * 112)
    def mw(st, per, maerkte):
        t = echt[(echt["stufe"] == st) & (echt["periode"] == per)
                 & (echt["kosten"] == "12bp") & (echt["markt"].isin(maerkte))]
        return t["netto_bp"].mean() if len(t) else np.nan
    for a, b in (("H1", "H2"), ("H2", "H3a"), ("H2", "H3b")):
        s = mw(b, "suche", MAERKTE) - mw(a, "suche", MAERKTE)
        h = mw(b, "holdout", ohne_btc) - mw(a, "holdout", ohne_btc)
        print(f"  {a} -> {b}  ({NAMEN[b]:30s}): Suche {s:+7.2f} bp   Holdout {h:+7.2f} bp")
    print("\nFERTIG")
