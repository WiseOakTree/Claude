"""Frage 3: Wie viel Risiko?   Frage 4: Wenn man falsch lag -- warum?"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=16e-4
d=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
c=d["close"].to_numpy(); h=d["high"].to_numpy(); l=d["low"].to_numpy(); n=len(d); idx=d.index
ret=pd.Series(c,index=idx).pct_change().fillna(0)

print("="*84)
print("FRAGE 3: Wie viel Risiko?  (10.000 $ Konto)")
print("="*84)
print(f"  {'Groesse':>8s} {'Nominal':>9s} {'Ø Tag':>8s} {'schlecht.Tag':>13s} "
      f"{'Tage < -3 %':>12s} {'Tage < -2 %':>12s}")
print("  "+"-"*66)
by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
ev=levels.breakout_events(by,d,min_touch=6)
pos=np.zeros(n); busy=-1; trades=[]
for (t,dr,tc,lv) in ev:
    if t<busy: continue
    pos[t:t+48]=dr; busy=t+48; trades.append((t,dr,tc,lv))
w0=pd.Series(np.clip(pos,-1,1),index=idx).astype(float)
for lev in [0.25,0.35,0.50,1.00]:
    w=w0*lev; held=w.shift(1)
    s=(held*ret-COST*held.diff().abs().fillna(0)).dropna()
    dd=((1+s).resample("1D").prod()-1).dropna()
    print(f"  {lev:>7.2f}x {lev*10000:>8.0f}$ {dd.mean()*10000:>+7.0f}$ "
          f"{dd.min()*100:>12.2f}% {(dd<-.03).mean()*100:>11.2f}% {(dd<-.02).mean()*100:>11.2f}%")
print("\n  Kraken bricht ab bei -3 % an einem Tag (-300 $) oder -6 % gesamt (-600 $).")

print()
print("="*84)
print(f"FRAGE 4: Wenn man falsch lag -- warum?   ({len(trades)} Trades, 48h)")
print("="*84)
rows=[]
atr=pd.Series(np.maximum(h-l,np.abs(h-np.roll(c,1)))).rolling(14).mean().to_numpy()
ma=pd.Series(c).rolling(200).mean().to_numpy()
vq=pd.Series(atr/c).rolling(500).rank(pct=True).to_numpy()
for (t,dr,tc,lv) in trades:
    if t+48>=n or np.isnan(ma[t]) or np.isnan(vq[t]): continue
    pnl=dr*(c[t+48]/c[t]-1)-COST
    rows.append(dict(t=t, gewinn=pnl>0, pnl=pnl*1e4, richtung=dr,
        stunde=idx[t].hour, wochentag=idx[t].dayofweek,
        trend_mit=int(np.sign(c[t]-ma[t])==dr),         # Bruch in Trendrichtung?
        vol_hoch=int(vq[t]>0.5), beruehrungen=tc,
        pen=abs(c[t]-lv)/atr[t], alter=np.nan))
f=pd.DataFrame(rows)
print(f"  Trefferquote gesamt: {f.gewinn.mean()*100:.1f} %   "
      f"Ø {f.pnl.mean():+.1f} bp   Median {f.pnl.median():+.1f} bp")
print(f"  Ø Gewinn {f[f.gewinn].pnl.mean():+.0f} bp   "
      f"Ø Verlust {f[~f.gewinn].pnl.mean():+.0f} bp")
print()
def split(name, mask, labA, labB):
    a=f[mask]; b=f[~mask]
    if len(a)<20 or len(b)<20: return
    t,p=stats.ttest_ind(a.pnl,b.pnl)
    print(f"  {name:26s} {labA:>16s} {a.pnl.mean():>+7.1f}bp ({a.gewinn.mean()*100:.0f}%,n={len(a)})"
          f" | {labB:>10s} {b.pnl.mean():>+7.1f}bp ({b.gewinn.mean()*100:.0f}%,n={len(b)})  p={p:.3f}")
print("  Was unterscheidet Gewinner von Verlierern?")
print("  "+"-"*78)
split("Richtung",            f.richtung>0, "LONG","SHORT")
split("Bruch mit Trend?",    f.trend_mit==1, "mit Trend","gegen")
split("Volatilitaet",        f.vol_hoch==1, "hoch","niedrig")
split("Beruehrungen",        f.beruehrungen>=8, ">=8","6-7")
split("Durchdringung",       f.pen>=0.25, ">=0,25 ATR","knapp")
split("Uhrzeit 19-22 UTC",   f.stunde.isin([19,20,21,22]), "abends","sonst")
split("Wochenende",          f.wochentag>=5, "Sa/So","Mo-Fr")
print()
print("  Die groessten Einzelverluste:")
print("  "+"-"*78)
for _,r in f.nsmallest(6,"pnl").iterrows():
    print(f"    {idx[int(r.t)]:%Y-%m-%d %H:%M}  {'LONG ' if r.richtung>0 else 'SHORT'} "
          f"{r.pnl:>+8.0f} bp   {'mit' if r.trend_mit else 'gegen'} Trend, "
          f"Vol {'hoch' if r.vol_hoch else 'niedrig'}, {int(r.beruehrungen)} Beruehrungen")
