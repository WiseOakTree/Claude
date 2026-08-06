"""Nebenbefund: Nach einer SEITWAERTSPHASE (168h) liefert der Ausbruch
+141 bp statt +67 bp (p=0,003). Das ist der neunte Filterkandidat.
Getestet wie alle anderen: Holdout und drei ungesehene Assets.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")

def trades(asset):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    c=d["close"].to_numpy(); n=len(d)
    r=np.diff(np.log(c),prepend=np.log(c[0]))
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    out=[]; busy=-1
    for (t,dr,tc,lv) in levels.breakout_events(by,d,min_touch=6):
        if t<busy or t+48>=n or t<168: continue
        busy=t+48
        seg=r[t-168:t]
        er=abs(seg.sum())/np.abs(seg).sum() if np.abs(seg).sum()>0 else 0
        out.append((d.index[t], dr*(c[t+48]/c[t]-1)*1e4-16.0, er))
    return pd.DataFrame(out,columns=["ts","pnl","er"])

print("="*90)
print("NEUNTER FILTERKANDIDAT: Ausbruch nach Seitwaertsphase (168h)")
print("="*90)
print(f"  {'Asset':6s} {'Zeitraum':13s} {'n':>5s} {'ruhig (unteres Drittel)':>24s} "
      f"{'unruhig (oberes)':>19s} {'Differenz':>10s}")
print("  "+"-"*82)
for a in ["btc","eth","sol","xrp"]:
    T=trades(a)
    # Schwelle NUR aus dem BTC-Suchzeitraum -- kein Nachschauen
    if a=="btc":
        thr_lo=T[T.ts<SPLIT].er.quantile(1/3); thr_hi=T[T.ts<SPLIT].er.quantile(2/3)
    for lab,m in (("Suchzeitraum",T.ts<SPLIT),("Holdout",T.ts>=SPLIT),
                  ("gesamt",pd.Series(True,index=T.index))):
        s=T[m]
        if len(s)<25: continue
        lo=s[s.er<=thr_lo].pnl; hi=s[s.er>=thr_hi].pnl
        if len(lo)<8 or len(hi)<8: continue
        print(f"  {a.upper():6s} {lab:13s} {len(s):>5d} {lo.mean():>+14.1f}bp (n={len(lo):>3d}) "
              f"{hi.mean():>+11.1f}bp (n={len(hi):>3d}) {lo.mean()-hi.mean():>+9.1f}")
    print()
print("="*90)
print("Zusammenfassung: nur Holdout und ungesehene Assets")
print("="*90)
dl=[];dh=[]
for a in ["btc","eth","sol","xrp"]:
    T=trades(a)
    s=T[T.ts>=SPLIT] if a=="btc" else T
    lo=s[s.er<=thr_lo].pnl; hi=s[s.er>=thr_hi].pnl
    if len(lo)>=8 and len(hi)>=8:
        dl.append(lo.mean()); dh.append(hi.mean())
        print(f"  {a.upper():6s} ruhig {lo.mean():>+8.1f} bp   unruhig {hi.mean():>+8.1f} bp   "
              f"Differenz {lo.mean()-hi.mean():>+8.1f} bp")
print(f"\n  Mittel: ruhig {np.mean(dl):+.1f} bp | unruhig {np.mean(dh):+.1f} bp | "
      f"Differenz {np.mean(dl)-np.mean(dh):+.1f} bp")
