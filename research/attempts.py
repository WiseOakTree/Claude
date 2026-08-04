"""Die Spielregel, die man selbst aendern kann: die Anzahl der Versuche.

Kein Zeitlimit + 85 $ Einsatz je Versuch = die Challenge ist ein
Wiederholungsspiel, kein Einzelschuss. Empirisch gerechnet, damit die
Korrelation aufeinanderfolgender Versuche (gleiches Marktregime) drinsteckt.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=16e-4

def daily(asset, hold=48, lev=0.5, min_touch=6):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=min_touch)
    c=d["close"].to_numpy(); n=len(d)
    ret=pd.Series(c,index=d.index).pct_change().fillna(0)
    pos=np.zeros(n)
    for (t,dr,_,_) in ev: pos[t:min(t+hold,n)]+=dr
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)*lev
    held=w.shift(1); s=held*ret-COST*held.diff().abs().fillna(0)
    return ((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()

def one_attempt(dd, st, cap=365):
    """Rueckgabe: ('p'|'f'|'c', Dauer in Tagen)."""
    e=1.0
    for i in range(st, min(st+cap, len(dd))):
        r=dd[i]
        if r<-.03: return "f", i-st+1
        e*=(1+r)
        if e<=.94: return "f", i-st+1
        if e-1>=.10: return "p", i-st+1
    return "c", min(cap, len(dd)-st)

def chain(dd, st, N, cap=365):
    """N Versuche nacheinander. Gibt (bestanden?, verbrauchte Versuche, Tage)."""
    cur=st; used=0; days=0
    for k in range(N):
        if cur>=len(dd)-30: break
        out,dur=one_attempt(dd,cur,cap); used+=1; days+=dur
        if out=="p": return True, used, days
        if out=="c": return None, used, days      # unaufgeloest -> konservativ
        cur+=dur
    return False, used, days

print("="*90)
print("Die Spielregel, die dir gehoert: WIE OFT du antrittst")
print("="*90)
for asset in ["btc","eth","sol","xrp"]:
    dd=daily(asset)
    print(f"\n{asset.upper()}  ({len(dd)} Handelstage)")
    p1=None
    print(f"  {'Versuche':>9s} {'bestanden':>10s} {'naiv unabh.':>12s} "
          f"{'Einsatz':>9s} {'Ø Dauer':>9s} {'zensiert':>9s}")
    print("  "+"-"*66)
    for N in (1,2,3,5,8):
        res=[chain(dd,st,N) for st in range(0,len(dd)-60)]
        ok=sum(1 for r in res if r[0] is True)
        no=sum(1 for r in res if r[0] is False)
        cen=sum(1 for r in res if r[0] is None)
        tot=ok+no+cen
        rate=ok/tot*100
        if N==1: p1=rate/100
        naive=(1-(1-p1)**N)*100
        used=np.mean([r[1] for r in res]); days=np.mean([r[2] for r in res])
        print(f"  {N:>9d} {rate:>9.1f}% {naive:>11.1f}% {used*85:>8.0f}$ "
              f"{days:>8.0f}T {cen/tot*100:>8.1f}%")
