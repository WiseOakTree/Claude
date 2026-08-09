"""Simuliert einen delta-gehedgten Short-Straddle: Wie viel ist die VRP wert?

Verkauft monatlich einen 30-Tage-ATM-Straddle zum DVOL-Preis, hedged taeglich
delta-neutral mit Spot. Das ist die saubere Ernte der Volatilitaetspraemie.
"""
import numpy as np, pandas as pd
from scipy.stats import norm

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
px = pd.read_csv(D + "btc_1h.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
iv = pd.read_csv(D + "dvol_BTC.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
df = pd.DataFrame({"px": px, "iv": iv}).dropna()

def bs(S, K, T, s):
    """Straddle-Preis und Delta (r=0)."""
    if T <= 1e-9:
        return abs(S - K), (1.0 if S > K else -1.0)
    d1 = (np.log(S / K) + 0.5 * s * s * T) / (s * np.sqrt(T))
    d2 = d1 - s * np.sqrt(T)
    call = S * norm.cdf(d1) - K * norm.cdf(d2)
    put = K * norm.cdf(-d2) - S * norm.cdf(-d1)
    return call + put, (norm.cdf(d1) - norm.cdf(-d1))

def run(tenor=30, vega_notional=1.0, bid_ask_vol=0.0, hedge_cost_bp=0.0):
    """Rollierende Short-Straddles. Rendite als Anteil des Spot-Notionals."""
    dates = df.index
    pnls, starts = [], []
    i = 0
    while i + tenor < len(dates):
        S0 = df["px"].iloc[i]
        sig = df["iv"].iloc[i] / 100.0
        sell_sig = sig * (1 - bid_ask_vol)     # wir verkaufen zum Bid
        K = S0
        prem, delta = bs(S0, K, tenor / 365, sell_sig)
        cash = prem                              # eingenommene Praemie
        hedge = delta                            # Spot-Hedge neutralisiert das Short-Delta
        cash -= hedge * S0
        cash -= abs(hedge) * S0 * hedge_cost_bp / 1e4
        for j in range(1, tenor + 1):
            S = df["px"].iloc[i + j]
            T = (tenor - j) / 365
            _, delta_new = bs(S, K, T, sig)      # Hedge zur laufenden IV
            want = delta_new
            trade = want - hedge
            cash -= trade * S
            cash -= abs(trade) * S * hedge_cost_bp / 1e4
            hedge = want
        ST = df["px"].iloc[i + tenor]
        payoff = abs(ST - K)                     # was wir bei Ausuebung zahlen
        cash += hedge * ST - abs(hedge) * ST * hedge_cost_bp / 1e4
        cash -= payoff
        pnls.append(cash / S0)                   # relativ zum Spot-Notional
        starts.append(dates[i])
        i += tenor
    return pd.Series(pnls, index=starts)

print("Short-Straddle, 30 Tage, taeglich delta-gehedgt (PnL je 1 BTC Notional)\n")
hdr = f"{'Szenario':38s} {'n':>3s} {'Median':>8s} {'Mittel':>8s} {'Trefferq':>9s} {'Sharpe':>7s} {'Worst':>8s}"
print(hdr); print("-" * len(hdr))
for name, kw in (
    ("ideal (keine Reibung)",            dict()),
    ("Vol-Spread 5 % (realistisch)",     dict(bid_ask_vol=0.05)),
    ("Vol-Spread 5 % + 10 bp Hedge",     dict(bid_ask_vol=0.05, hedge_cost_bp=10)),
    ("Vol-Spread 10 % + 16 bp Hedge",    dict(bid_ask_vol=0.10, hedge_cost_bp=16)),
):
    r = run(**kw)
    sh = r.mean() / r.std() * np.sqrt(12)
    print(f"{name:38s} {len(r):3d} {r.median()*100:+7.2f}% {r.mean()*100:+7.2f}% "
          f"{(r>0).mean()*100:8.0f}% {sh:7.2f} {r.min()*100:+7.2f}%")

r = run(bid_ask_vol=0.05, hedge_cost_bp=10)
eq = (1 + r).cumprod()
dd = (eq / eq.cummax() - 1).min()
print(f"\nRealistischer Fall: Gesamt {(eq.iloc[-1]-1)*100:+.1f} % ueber {len(r)} Monate, "
      f"max. Drawdown {dd*100:.1f} %")
print("Schlechteste 5 Monate:", ", ".join(f"{v*100:+.1f}%" for v in r.nsmallest(5)))
