"""Der entscheidende Test: Filter auf ungesehene Daten anwenden.

Trainiert EINMAL auf dem Suchzeitraum (BTC, 2021-03..2024-12).
Angewandt auf:
  (a) BTC-Holdout 2025-01..2026-06  -- dritte Nutzung, entsprechend abgewertet
  (b) ETH gesamt                    -- anderes Asset, unabhaengig
"""
import sys, warnings; sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/ml")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import xgboost as xgb
from scipy import stats
from features import FEATURES

M="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/ml/"
PARAMS = dict(max_depth=3, n_estimators=150, learning_rate=0.05,
              subsample=0.8, colsample_bytree=0.7, min_child_weight=20,
              reg_lambda=5.0, reg_alpha=1.0, objective="reg:squarederror",
              verbosity=0, n_jobs=4)

D = pd.read_csv(M+"feat_btc_t4.csv", parse_dates=["time"])
TR = D[D.time < "2025-01-01"]
model = xgb.XGBRegressor(**PARAMS)
model.fit(TR[FEATURES].to_numpy(float), TR["y"].to_numpy(float))
print(f"Trainiert auf {len(TR)} Ausbruechen (BTC, Suchzeitraum)\n")

def evaluate(df, label, touch_min=None):
    d = df if touch_min is None else df[df.touches >= touch_min]
    if len(d) < 40:
        print(f"{label}: nur {len(d)} Ereignisse -- zu wenige"); return
    p = model.predict(d[FEATURES].to_numpy(float))
    y = d["y"].to_numpy(float)
    print("="*78); print(f"{label}   ({len(d)} Ereignisse)"); print("="*78)
    print(f"  {'Auswahl':18s} {'n':>6s} {'Ergebnis':>11s} {'Vorsprung':>12s}")
    print("  "+"-"*50)
    print(f"  {'alle (ungefiltert)':18s} {len(y):6d} {y.mean():+10.1f} bp {0.0:+11.1f} bp")
    for q,nm in ((0.5,"beste Haelfte"),(0.3,"beste 30 %"),(0.2,"beste 20 %")):
        sel=y[p>=np.quantile(p,1-q)]
        print(f"  {nm:18s} {len(sel):6d} {sel.mean():+10.1f} bp {sel.mean()-y.mean():+11.1f} bp")
    ic,pv = stats.spearmanr(p,y)
    print(f"  Rangkorrelation: {ic:+.3f} (p={pv:.3f})"
          + ("   <-- haelt" if ic>0 and pv<0.05 else "   <-- haelt NICHT"))
    print()

B = pd.read_csv(M+"feat_btc_t4.csv", parse_dates=["time"])
evaluate(B[B.time>="2025-01-01"], "BTC-HOLDOUT 2025-01..2026-06 (dritte Nutzung)")
evaluate(B[B.time>="2025-01-01"], "BTC-HOLDOUT, nur >=6 Beruehrungen", touch_min=6)
E = pd.read_csv(M+"feat_eth_t4.csv", parse_dates=["time"])
evaluate(E, "ETH gesamt (anderes Asset)")
evaluate(E, "ETH, nur >=6 Beruehrungen", touch_min=6)
