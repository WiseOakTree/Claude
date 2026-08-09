"""Volumenbestaetigter Ausbruch + MACD gegen die Challenge-Regeln.

Zwei Familien, die im urspruenglichen 120er-Suchlauf FEHLTEN.
Gleiche Methodik: Walk-Forward, 90-Tage-Fenster, echte Kraken-Prop-Kosten,
execution.mode='close' (look-ahead-frei).
"""
import sys, itertools, warnings
sys.path.insert(0, "/home/user/Claude/src")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import strategies, engine
from prop_backtester.config import (BacktestConfig, CostConfig, RiskConfig,
                                    ExecutionConfig)

D = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
h1 = pd.read_csv(D + "btc_1h.csv", index_col=0, parse_dates=True)

def resample(df, rule):
    if rule == "1h": return df
    return df.resample(rule).agg({"open": "first", "high": "max", "low": "min",
                                  "close": "last", "volume": "sum"}).dropna()

# echte Kraken-Prop-Konditionen
COSTS = CostConfig(fee_pct=0.0004, slippage_pct=0.0002, half_spread_pct=0.0002,
                   slippage_vol_mult=0.05, funding_rate_daily_pct=0.00033)

def challenge(eq, win_days=90, bar_h=1):
    """Pass-Rate ueber rollierende 90-Tage-Fenster auf der Equity-Kurve."""
    e = eq["equity_close"].resample("1D").last().ffill().dropna()
    r = e.pct_change().fillna(0).to_numpy()
    passed = tot = 0; R = []; DD = []
    for s in range(0, len(r) - win_days):
        w = r[s:s + win_days]
        c = np.cumprod(1 + w)
        dd = (c / np.maximum.accumulate(c) - 1).min()
        passed += (c[-1] - 1 >= .10 and dd >= -.06 and w.min() > -.03); tot += 1
        R.append(c[-1] - 1); DD.append(-dd)
    if not tot: return 0, 0, 0, 0
    return passed / tot * 100, np.median(R) * 100, max(DD) * 100, tot

GRID = {
    "macd": [dict(fast=f, slow=s, signal=9) for f, s in
             ((12, 26), (8, 21), (19, 39), (5, 35))],
    "breakout_volume": [dict(lookback=lb, vol_mult=vm) for lb, vm in
                        itertools.product((20, 55, 100), (1.2, 1.5, 2.0, 3.0))],
}

rows = []
for tf in ("1h", "4h", "1D"):
    df = resample(h1, tf)
    for name, params in GRID.items():
        gen = strategies.REGISTRY[name]
        for p in params:
            for risk in (0.003, 0.005, 0.01):
                sig = gen(df, **p)
                if len(sig) < 5: continue
                cfg = BacktestConfig(initial_balance=10_000, costs=COSTS,
                                     risk=RiskConfig(risk_per_trade_pct=risk,
                                                     stop_bricks=2.0, max_leverage=5.0),
                                     execution=ExecutionConfig(mode="close"))
                res = engine.run_backtest(df, sig, cfg)
                pr, med, wdd, n = challenge(res.equity)
                rows.append(dict(tf=tf, strat=name, **p, risk=risk, trades=len(sig),
                                 pass_rate=pr, median=med, worst_dd=wdd, n=n))

out = pd.DataFrame(rows).sort_values("pass_rate", ascending=False)
out.to_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/ta_results.csv", index=False)
print(f"Kombinationen getestet: {len(out)}\n")
print("Beste 12 nach Pass-Rate:")
cols = ["tf", "strat", "lookback", "vol_mult", "fast", "slow", "risk", "trades",
        "pass_rate", "median", "worst_dd"]
cols = [c for c in cols if c in out.columns]
print(out[cols].head(12).to_string(index=False, float_format=lambda v: f"{v:.2f}"))
print("\nJe Familie das Beste:")
for s, g in out.groupby("strat"):
    b = g.iloc[0]
    print(f"  {s:18s} Pass {b.pass_rate:5.1f}%   Median {b['median']:+6.2f}%   "
          f"worstDD {b.worst_dd:5.1f}%   ({b.tf}, {int(b.trades)} Trades)")
print(f"\nAnteil mit Pass-Rate >= 50 %: {(out.pass_rate >= 50).mean()*100:.1f} %")
print(f"Anteil mit positivem Median:  {(out['median'] > 0).mean()*100:.1f} %")
print(f"Median-Rendite ueber alle Kombinationen: {out['median'].median():+.2f} %")
