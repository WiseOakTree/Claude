"""XGBoost als Filter -- korrigierter Aufbau.

  * keine Zeilen wegen fehlender Werte verwerfen (XGBoost kann NaN)
  * trainiert wird auf der GROSSEN Menge (>=4 Beruehrungen), angewandt auf die
    gehandelte Teilmenge (>=6)
  * Nullmodell mit 20 Wiederholungen fuer ein belastbares Rauschmass
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

def purged_cv(X, y, t, seed=None, n_folds=6, embargo=24, min_train=250):
    """Out-of-fold-Vorhersagen. seed != None mischt die Ziele (Nullmodell)."""
    o = np.argsort(t); X, y, t = X[o], y[o], t[o]
    if seed is not None:
        y = np.random.default_rng(seed).permutation(y)
    n = len(y)
    bounds = np.linspace(min_train, n, n_folds + 1).astype(int)
    pred = np.full(n, np.nan)
    for k in range(n_folds):
        lo, hi = bounds[k], bounds[k+1]
        if hi <= lo: continue
        tr = t < (t[lo] - embargo)
        if tr.sum() < min_train: continue
        m = xgb.XGBRegressor(**PARAMS); m.fit(X[tr], y[tr])
        pred[lo:hi] = m.predict(X[lo:hi])
    ok = np.isfinite(pred)
    return pred[ok], y[ok], t[ok]

def lift(pred, y, q=0.5):
    return y[pred >= np.quantile(pred, 1-q)].mean() - y.mean()

D = pd.read_csv(M+"feat_btc_t4.csv", parse_dates=["time"])
S = D[D.time < "2025-01-01"].reset_index(drop=True)
X = S[FEATURES].to_numpy(float); y = S["y"].to_numpy(float); t = S["t"].to_numpy()
print("="*80)
print(f"Trainingsmenge: {len(S)} Ausbrueche (>=4 Ber.), Suchzeitraum, Basis {y.mean():+.1f} bp")
print("="*80)

p, yy, tt = purged_cv(X, y, t)
print(f"\nOut-of-fold-Vorhersagen: {len(yy)}")
print(f"  {'Auswahl':18s} {'n':>6s} {'Ergebnis':>11s} {'Vorsprung':>11s}")
print("  " + "-"*50)
print(f"  {'alle':18s} {len(yy):6d} {yy.mean():+10.1f} bp {0.0:+10.1f} bp")
for q,nm in ((0.5,"beste Haelfte"),(0.3,"beste 30 %"),(0.2,"beste 20 %")):
    thr=np.quantile(p,1-q); sel=yy[p>=thr]
    print(f"  {nm:18s} {len(sel):6d} {sel.mean():+10.1f} bp {sel.mean()-yy.mean():+10.1f} bp")
ic,pv = stats.spearmanr(p, yy)
print(f"  Rangkorrelation Vorhersage/Ausgang: {ic:+.3f} (p={pv:.3f})")

print("\n" + "="*80)
print("Nullmodell: dieselbe Prozedur mit GEMISCHTEN Zielen (20 Wiederholungen)")
print("="*80)
nl=[]
for s in range(20):
    pn, yn, _ = purged_cv(X, y, t, seed=1000+s)
    nl.append(lift(pn, yn))
nl=np.array(nl)
real = lift(p, yy)
print(f"  Rauschniveau: {nl.mean():+.1f} bp  (Streuung {nl.std():.1f}, "
      f"Spanne {nl.min():+.1f} .. {nl.max():+.1f})")
print(f"  Echtes Modell: {real:+.1f} bp")
z=(real-nl.mean())/max(nl.std(),1e-9)
print(f"  -> {z:+.1f} Standardabweichungen ueber dem Rauschen  "
      f"({'signifikant' if z>2 else 'NICHT signifikant'})")
print(f"  Anteil der Nullmodelle, die das echte schlagen: {(nl>=real).mean()*100:.0f} %")

print("\n" + "="*80)
print("Angewandt auf die tatsaechlich gehandelte Menge (>=6 Beruehrungen)")
print("="*80)
mask6 = S["touches"].to_numpy()[np.argsort(t)] >= 6
mask6 = mask6[np.isin(np.sort(t), tt)]
if mask6.sum() > 30:
    y6, p6 = yy[mask6], p[mask6]
    print(f"  {len(y6)} Ereignisse, Basis {y6.mean():+.1f} bp")
    for q,nm in ((0.5,"beste Haelfte"),(0.3,"beste 30 %")):
        sel=y6[p6>=np.quantile(p6,1-q)]
        print(f"  {nm:18s} n={len(sel):4d}  {sel.mean():+8.1f} bp  "
              f"Vorsprung {sel.mean()-y6.mean():+7.1f} bp")

print("\n" + "="*80)
print("Welche Merkmale nutzt das Modell ueberhaupt?")
print("="*80)
m = xgb.XGBRegressor(**PARAMS); m.fit(X, y)
imp = pd.Series(m.feature_importances_, index=FEATURES).sort_values(ascending=False)
for k,v in imp.head(8).items(): print(f"  {k:16s} {v:.3f}")
