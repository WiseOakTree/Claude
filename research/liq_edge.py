"""Sagt die Buchtiefe am Level etwas ueber Ausbruch und Stops?"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels, liquidity

O="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
lm=liquidity.LiquidityMap(pd.read_csv(O+"liqmap_search.csv.gz"), window_days=7)
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
df=full[(full.index>=pd.Timestamp("2023-01-08",tz="UTC"))&
        (full.index<pd.Timestamp("2025-01-01",tz="UTC"))].copy()
c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy()
n=len(df); idx=df.index
by=levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)
bo=levels.breakout_events(by, df, min_touch=6)
print(f"Ausbrueche im Liquiditaetszeitraum: {len(bo)}\n")

rows=[]
for (t,d,tc,lvl) in bo:
    if t+24>=n: continue
    when=idx[t]
    depth = lm.at(lvl, when, width_pct=0.3)
    ref   = lm.at(c[t], when, width_pct=0.3)
    void  = lm.void_ratio(lvl, when, direction=d, width_pct=0.3, gap_pct=0.5)
    if not (np.isfinite(depth) and np.isfinite(ref) and ref>0): continue
    fwd24 = (c[t+24]/c[t]-1)*d*1e4
    # schlechteste Gegenbewegung in 24h (fuer die Stop-Frage)
    seg_l, seg_h = l[t:t+24].min(), h[t:t+24].max()
    adverse = ((c[t]-seg_l)/c[t] if d>0 else (seg_h-c[t])/c[t])*1e4
    rows.append((depth/ref, void, fwd24, adverse, tc))
E=pd.DataFrame(rows, columns=["rel_depth","void","fwd24","adverse","touches"]).dropna()
print(f"auswertbar: {len(E)}\n")

def qtab(col, label):
    print("="*76); print(label); print("="*76)
    E["q"]=pd.qcut(E[col], 4, labels=False, duplicates="drop")
    print(f"  {'Quartil':>9s} {'n':>6s} {'Effekt 24h':>13s} {'Gegenbewegung':>16s}")
    print("  "+"-"*48)
    for q in sorted(E.q.dropna().unique()):
        g=E[E.q==q]
        print(f"  {int(q)+1:9d} {len(g):6d} {g.fwd24.mean():+11.1f} bp {g.adverse.mean():14.1f} bp")
    a=E[E.q==E.q.min()].fwd24; b=E[E.q==E.q.max()].fwd24
    _,p=stats.ttest_ind(a,b,equal_var=False)
    ic,pi=stats.spearmanr(E[col], E.fwd24)
    print(f"\n  Q4-Q1: {b.mean()-a.mean():+.1f} bp (p={p:.3f})   "
          f"Rangkorrelation {ic:+.3f} (p={pi:.3f})")

qtab("rel_depth", "1) Tiefe AM Level -- bricht ein duennes Level heftiger?")
print()
qtab("void", "2) Loch HINTER dem Level -- faellt der Kurs schneller durch?")

print("\n"+"="*76)
print("3) Stop-Platzierung: wie weit laeuft es typischerweise gegen einen?")
print("="*76)
print(f"  Median-Gegenbewegung in 24 h: {E.adverse.median():.0f} bp")
for q in (0.5,0.75,0.9,0.95):
    print(f"  {q*100:.0f}%-Quantil: {E.adverse.quantile(q):6.0f} bp "
          f"({E.adverse.quantile(q)/100:.2f} %)")
print(f"\n  {'Stop-Abstand':>13s} {'wird geholt':>13s} {'verbleibende Trades':>21s}")
print("  "+"-"*50)
for stop_bp in (50, 100, 150, 200, 300, 500):
    hit=(E.adverse>stop_bp).mean()
    surv=E[E.adverse<=stop_bp]
    print(f"  {stop_bp:11d} bp {hit*100:12.1f}% {len(surv):15d} "
          f"(Effekt {surv.fwd24.mean():+.0f} bp)")
print("\n  Hinweis: Trades OHNE Stop haben den Effekt "
      f"{E.fwd24.mean():+.1f} bp bei {len(E)} Faellen.")

print("\n"+"="*76)
print("4) Haengt die noetige Stop-Weite von der Liquiditaet ab?")
print("="*76)
E["dq"]=pd.qcut(E.rel_depth, 3, labels=["duenn","mittel","dick"], duplicates="drop")
print(f"  {'Tiefe':>8s} {'Median-Gegenbew.':>18s} {'90%-Quantil':>14s}")
print("  "+"-"*42)
for k in ("duenn","mittel","dick"):
    g=E[E.dq==k]
    if len(g)>10:
        print(f"  {k:>8s} {g.adverse.median():15.0f} bp {g.adverse.quantile(.9):11.0f} bp")
