"""Wuerde die Vol-Praemie die Challenge bestehen -- wenn es sie bei Kraken gaebe?

Taegliche Mark-to-Market-PnL: Hedge-Gewinn wird schrittweise akkumuliert
(hedge_{j-1} * (S_j - S_{j-1})), nicht gegen den Startkurs gerechnet.
"""
import numpy as np, pandas as pd
from scipy.stats import norm

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
px = pd.read_csv(D + "btc_1h.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
iv = pd.read_csv(D + "dvol_BTC.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
df = pd.DataFrame({"px": px, "iv": iv}).dropna()

def bs(S, K, T, s):
    if T <= 1e-9: return abs(S-K), (1.0 if S > K else -1.0)
    d1 = (np.log(S/K) + .5*s*s*T)/(s*np.sqrt(T)); d2 = d1 - s*np.sqrt(T)
    return (S*norm.cdf(d1)-K*norm.cdf(d2)) + (K*norm.cdf(-d2)-S*norm.cdf(-d1)), norm.cdf(d1)-norm.cdf(-d1)

def daily_pnl(tenor=30, bid_ask_vol=.05, hedge_bp=10):
    out = pd.Series(0.0, index=df.index)
    i = 0
    while i + tenor < len(df):
        S0 = df["px"].iloc[i]; K = S0
        sig0 = df["iv"].iloc[i]/100
        prem, delta = bs(S0, K, tenor/365, sig0*(1-bid_ask_vol))
        hedge = delta                       # Spot-Hedge gegen das Short-Delta
        hedge_pnl = -abs(hedge)*S0*hedge_bp/1e4
        last_mv = 0.0
        S_prev = S0
        for j in range(1, tenor+1):
            S = df["px"].iloc[i+j]
            T = (tenor-j)/365
            hedge_pnl += hedge*(S - S_prev)          # Hedge-Ertrag dieses Schritts
            straddle, dnew = bs(S, K, T, df["iv"].iloc[i+j]/100)
            trade = dnew - hedge
            hedge_pnl -= abs(trade)*S*hedge_bp/1e4
            hedge, S_prev = dnew, S
            mv = prem - straddle + hedge_pnl          # Portfoliowert gegen Start
            out.iloc[i+j] = (mv - last_mv)/S0
            last_mv = mv
        i += tenor
    return out

def challenge(r, win=90, scale=1.0):
    r = (r.dropna()*scale).to_numpy(); passed = tot = 0; R=[]; DD=[]
    for s in range(0, len(r)-win):
        w = r[s:s+win]; eq = np.cumprod(1+w)
        dd = (eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1 >= .10 and dd >= -.06 and w.min() > -.03); tot += 1
        R.append(eq[-1]-1); DD.append(-dd)
    return passed/tot*100, np.median(R)*100, np.median(DD)*100

pnl = daily_pnl()
ann = pnl.mean()*365*100; vol = pnl.std()*np.sqrt(365)*100
print(f"Kontrolle gegen die Monatssimulation: {ann:+.1f} % p.a., {vol:.1f} % Vola, Sharpe {ann/vol:.2f}\n")
print("Delta-gehedgter Short-Straddle gegen die Challenge-Regeln (90-Tage-Fenster)\n")
print(f"{'Hebel auf das Notional':28s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-" * 56)
for lev in (1, 2, 3, 5):
    p, r, d = challenge(pnl, scale=lev)
    print(f"{f'{lev}x Notional':28s} {r:+8.1f}% {d:6.1f}% {p:6.1f}%")
