"""Isoliert die EINE Frage: Bringt Volumenbestaetigung etwas?

Gleicher Ausbruch, gleiche Parameter, gleiche Kosten -- einziger Unterschied
ist der Volumenfilter. Plus Out-of-Sample-Test der besten Variante.
"""
import sys, warnings, itertools
sys.path.insert(0, "/home/user/Claude/src")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import strategies, engine
from prop_backtester.config import BacktestConfig, CostConfig, RiskConfig, ExecutionConfig

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
h1 = pd.read_csv(D + "btc_1h.csv", index_col=0, parse_dates=True)
def rs(df, r):
    return df if r == "1h" else df.resample(r).agg(
        {"open":"first","high":"max","low":"min","close":"last","volume":"sum"}).dropna()

COSTS = CostConfig(fee_pct=.0004, slippage_pct=.0002, half_spread_pct=.0002,
                   slippage_vol_mult=.05, funding_rate_daily_pct=.00033)

def evaluate(df, sig, risk=.005, win=90):
    cfg = BacktestConfig(initial_balance=10_000, costs=COSTS,
                         risk=RiskConfig(risk_per_trade_pct=risk, stop_bricks=2., max_leverage=5.),
                         execution=ExecutionConfig(mode="close"))
    e = engine.run_backtest(df, sig, cfg).equity["equity_close"].resample("1D").last().ffill().dropna()
    r = e.pct_change().fillna(0).to_numpy()
    passed = tot = 0; R = []
    for s in range(0, len(r) - win):
        w = r[s:s+win]; c = np.cumprod(1+w)
        dd = (c/np.maximum.accumulate(c)-1).min()
        passed += (c[-1]-1 >= .10 and dd >= -.06 and w.min() > -.03); tot += 1
        R.append(c[-1]-1)
    return (passed/max(tot,1)*100, np.median(R)*100 if R else 0, len(sig))

print("=" * 74)
print("A) Direktvergleich: derselbe Ausbruch mit und ohne Volumenfilter")
print("=" * 74)
print(f"{'TF':4s} {'Lookback':>9s} {'ohne Filter':>26s} {'mit Volumen (1.5x)':>26s}")
print(f"{'':4s} {'':>9s} {'Pass':>8s}{'Median':>9s}{'Trades':>9s} {'Pass':>8s}{'Median':>9s}{'Trades':>9s}")
print("-" * 74)
better = 0; total = 0
for tf in ("1h", "4h", "1D"):
    df = rs(h1, tf)
    for lb in (20, 55, 100):
        a = evaluate(df, strategies.donchian(df, lookback=lb))
        b = evaluate(df, strategies.breakout_volume(df, lookback=lb, vol_mult=1.5))
        total += 1; better += b[0] > a[0]
        print(f"{tf:4s} {lb:9d} {a[0]:7.1f}%{a[1]:+8.2f}%{a[2]:9d} {b[0]:7.1f}%{b[1]:+8.2f}%{b[2]:9d}")
print(f"\nVolumenfilter besser in {better}/{total} Faellen")

print("\n" + "=" * 74)
print("B) Out-of-Sample: beste Variante (4h, Lookback 20, 1.5x, Risiko 1 %)")
print("=" * 74)
df = rs(h1, "4h")
half = len(df) // 2
for nm, d in (("1. Haelfte", df.iloc[:half]), ("2. Haelfte", df.iloc[half:]), ("gesamt", df)):
    sig = strategies.breakout_volume(d, lookback=20, vol_mult=1.5)
    p, m, n = evaluate(d, sig, risk=.01)
    print(f"  {nm:11s} ({d.index.min().date()}..{d.index.max().date()})  "
          f"Pass {p:5.1f}%   Median {m:+6.2f}%   {n} Trades")
