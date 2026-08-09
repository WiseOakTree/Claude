"""Die entscheidende Frage: WELCHES Regelwerk erlaubt 20-30 % im Jahr?
Beide Strategien, alle Kombinationen aus Tageslimit und Drawdown-Boden.
Positionsgroesse je Zelle optimiert.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
O="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/"

def sr():
    d=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=6)
    n=len(d); pos=np.zeros(n); busy=-1
    for (t,dr,_,_) in ev:
        if t<busy: continue
        pos[t:t+48]=dr; busy=t+48
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float); held=w.shift(1)
    return ((1+(held*h-8/1e4*held.diff().abs().fillna(0)).dropna()).resample("1D").prod()-1).dropna().to_numpy()

STR=pd.read_csv(O+"straddle_daily.csv",index_col=0,parse_dates=True).iloc[:,0].to_numpy()
SR=sr()

def score(x,day_lim,dd):
    """Anteil Jahre, die ueberleben UND >=20 % machen; plus Mittelwert."""
    ok=0; tot=0; rets=[]
    for st in range(0,len(x)-365,5):
        e=1.0; alive=True
        for k in range(st,st+365):
            if day_lim is not None and x[k]<-day_lim: alive=False;break
            e*=(1+x[k])
            if e<=1-dd: alive=False;break
        tot+=1; rets.append(e-1 if alive else -dd)
        if alive and e-1>=0.20: ok+=1
    return ok/tot*100, np.mean(rets)*100

print("="*92)
print("WELCHES REGELWERK ERLAUBT 20-30 % IM JAHR?")
print("  Je Zelle: beste Positionsgroesse aus 0,25x-3,0x")
print("="*92)
LEVS=[0.25,0.35,0.5,0.75,1.0,1.5,2.0,3.0]
RULES=[("Kraken-Typ: 3 % Tag / 6 % DD",0.03,0.06),
       ("3 % Tag / 10 % DD",0.03,0.10),
       ("5 % Tag / 6 % DD",0.05,0.06),
       ("5 % Tag / 10 % DD",0.05,0.10),
       ("kein Tageslimit / 6 % DD",None,0.06),
       ("kein Tageslimit / 10 % DD",None,0.10),
       ("kein Tageslimit / 20 % DD",None,0.20),
       ("EIGENES KAPITAL (kein Limit)",None,0.95)]
for name,dl,dd in RULES:
    print(f"\n  {name}")
    print(f"    {'Strategie':22s} {'beste Groesse':>13s} {'Jahre mit >=20 %':>18s} {'Ø Rendite':>11s}")
    for sn,x in [("S/R-Ausbruch BTC",SR),("Short-Straddle",STR)]:
        best=(-1,None,None)
        for L in LEVS:
            p,m=score(x*L,dl,dd)
            if p>best[0]: best=(p,L,m)
        flag="  <-- ZIEL" if best[0]>=50 else ""
        print(f"    {sn:22s} {best[1]:>12.2f}x {best[0]:>17.1f}% {best[2]:>+10.1f}%{flag}")
