"""MACD + Stochastik + Bollinger auf 4h -- genau die Kombination, die der
Nutzer handeln will. Beide gaengigen Lesarten, einzeln und in Konfluenz.

Suchzeitraum 2021-03..2024-12, Holdout 2025-01..2026-06 (nie benutzt fuer
diese Familie). Kosten: 8 bp je Seite = 16 bp je Roundtrip (Kraken-Prop).
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, itertools

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST_SIDE = 8e-4          # 8 bp je Seite

def bars4h(sym):
    d = pd.read_csv(D + f"{sym}_1h.csv", index_col=0, parse_dates=True)
    return d.resample("4h").agg({"open":"first","high":"max","low":"min",
                                 "close":"last","volume":"sum"}).dropna()

# ---------- Indikatoren (Standard-Definitionen) ----------
def macd(c, f=12, s=26, sig=9):
    line = c.ewm(span=f, adjust=False).mean() - c.ewm(span=s, adjust=False).mean()
    signal = line.ewm(span=sig, adjust=False).mean()
    return line, signal, line - signal

def stoch(df, k=14, d=3, smooth=3):
    ll = df.low.rolling(k).min(); hh = df.high.rolling(k).max()
    raw = 100 * (df.close - ll) / (hh - ll).replace(0, np.nan)
    K = raw.rolling(smooth).mean()
    return K, K.rolling(d).mean()

def boll(c, p=20, n=2.0):
    m = c.rolling(p).mean(); sd = c.rolling(p).std()
    return m - n*sd, m, m + n*sd, (c - (m - n*sd)) / (2*n*sd).replace(0, np.nan)

# ---------- Signale ----------
def signals(df, reading, mf=12, ms=26, msig=9, sk=14, sd=3, bp=20, bn=2.0,
            os_=20, ob=80):
    c = df.close
    line, sig, hist = macd(c, mf, ms, msig)
    K, Dl = stoch(df, sk, sd)
    lo, mid, up, pctb = boll(c, bp, bn)

    if reading == "reversion":
        # Klassisch: Bandberuehrung + ueberverkauft + MACD dreht
        L = (c <= lo) & (K < os_) & (hist > hist.shift(1))
        S = (c >= up) & (K > ob) & (hist < hist.shift(1))
    elif reading == "trend":
        # Trendlesart: MACD bullisch, ueber Mittelband, Stoch kreuzt hoch
        kx_up = (K > Dl) & (K.shift(1) <= Dl.shift(1))
        kx_dn = (K < Dl) & (K.shift(1) >= Dl.shift(1))
        L = (line > sig) & (c > mid) & kx_up
        S = (line < sig) & (c < mid) & kx_dn
    # Einzelindikatoren zum Vergleich
    elif reading == "macd_only":
        L = (line > sig) & (line.shift(1) <= sig.shift(1))
        S = (line < sig) & (line.shift(1) >= sig.shift(1))
    elif reading == "stoch_only":
        L = (K > os_) & (K.shift(1) <= os_)
        S = (K < ob) & (K.shift(1) >= ob)
    elif reading == "boll_only":
        L = (c <= lo) & (c.shift(1) > lo.shift(1))
        S = (c >= up) & (c.shift(1) < up.shift(1))
    return L.fillna(False), S.fillna(False)

# ---------- Auswertung mit Ueberlappungskorrektur ----------
def evaluate(df, L, S, hold):
    c = df.close.to_numpy()
    fwd = np.full(len(c), np.nan)
    fwd[:-hold] = c[hold:] / c[:-hold] - 1
    d = np.where(L.to_numpy(), 1, np.where(S.to_numpy(), -1, 0))
    m = (d != 0) & np.isfinite(fwd)
    if m.sum() < 10: return None
    r = d[m] * fwd[m] - 2*COST_SIDE          # Ein- und Ausstieg
    n_eff = max(len(r) / hold, 2)            # Ueberlappung
    t = r.mean() / (r.std(ddof=1) / np.sqrt(n_eff)) if r.std() > 0 else 0
    return dict(n=int(m.sum()), bp=r.mean()*1e4, t=t,
                hit=(r > 0).mean()*100, n_eff=n_eff)

SPLIT = "2025-01-01"
readings = ["macd_only", "stoch_only", "boll_only", "reversion", "trend"]

print("=" * 78)
print("BTC 4h  --  Suchzeitraum 2021-03 .. 2024-12")
print("=" * 78)
btc = bars4h("btc")
tr = btc[btc.index < SPLIT]; ho = btc[btc.index >= SPLIT]
print(f"{'Lesart':<12} {'Halten':>7} {'Signale':>8} {'bp/Trade':>10} {'t':>7} {'Treffer':>8}")
best = {}
for rd in readings:
    L, S = signals(tr, rd)
    for hold in (1, 6, 12, 30):     # 4h, 1 Tag, 2 Tage, 5 Tage
        r = evaluate(tr, L, S, hold)
        if r is None: continue
        star = ""
        if rd not in best or r["bp"] > best[rd][1]["bp"]:
            best[rd] = (hold, r)
        print(f"{rd:<12} {hold*4:>5}h {r['n']:>8} {r['bp']:>+9.1f} {r['t']:>7.2f} {r['hit']:>7.1f}%")
    print()
