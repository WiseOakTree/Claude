"""Teil 3: Die beste Lesart out-of-sample, auf ETH, ohne Kosten -- und die
Pass-Rate unter den echten Kraken-Regeln."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, signals, macd, stoch, boll, SPLIT
COST=8e-4

def ev(df,L,S,hold,cost=COST):
    c=df.close.to_numpy(); f=np.full(len(c),np.nan); f[:-hold]=c[hold:]/c[:-hold]-1
    d=np.where(L.to_numpy(),1,np.where(S.to_numpy(),-1,0)); m=(d!=0)&np.isfinite(f)
    if m.sum()<10: return None
    r=d[m]*f[m]-2*cost; ne=max(m.sum()/hold,2)
    return dict(n=int(m.sum()),bp=r.mean()*1e4,t=r.mean()/(r.std(ddof=1)/np.sqrt(ne)),
                hit=(r>0).mean()*100)

print("="*78); print("Die Trend-Lesart (12/26/9, Stoch 14/3, BB 20/2, 5 Tage halten)")
print("="*78)
print(f"{'Markt':<10} {'Zeitraum':<20} {'n':>5} {'bp/Trade':>10} {'t':>7} {'Treffer':>8}")
for sym in ("btc","eth","sol"):
    df=bars4h(sym); tr=df[df.index<SPLIT]; ho=df[df.index>=SPLIT]
    for name,seg in (("Suche 21-24",tr),("HOLDOUT 25-26",ho)):
        L,S=signals(seg,"trend"); r=ev(seg,L,S,30)
        if r: print(f"{sym.upper():<10} {name:<20} {r['n']:>5} {r['bp']:>+9.1f} "
                    f"{r['t']:>7.2f} {r['hit']:>7.1f}%")
    print()

print("="*78); print("Sind es die Kosten oder gibt es keinen Edge? (BTC, ganze Historie)")
print("="*78)
btc=bars4h("btc")
for rd in ("trend","macd_only","stoch_only","boll_only"):
    L,S=signals(btc,rd)
    for hold in (6,30):
        a=ev(btc,L,S,hold,cost=0); b=ev(btc,L,S,hold,cost=COST)
        if a: print(f"  {rd:<11} {hold*4:>4}h  ohne Kosten {a['bp']:>+7.1f} bp "
                    f"(t={a['t']:>5.2f})   mit Kosten {b['bp']:>+7.1f} bp")
    print()

print("="*78); print("Pass-Rate unter den echten Kraken-Regeln (10 % Ziel, 6 % statisch,")
print("3 % Tageslimit, kein Zeitlimit) -- Trend-Lesart, 5 Tage halten")
print("="*78)
def passrate(df,L,S,hold,size):
    c=df.close.to_numpy(); pos=np.zeros(len(c)); i=0
    d=np.where(L.to_numpy(),1,np.where(S.to_numpy(),-1,0))
    while i<len(c):
        if d[i]!=0:
            pos[i:i+hold]=d[i]; i+=hold
        else: i+=1
    ret=np.diff(c)/c[:-1]; held=pos[:-1]
    turn=np.abs(np.diff(np.concatenate([[0],pos])))[:-1]
    s=held*ret*size - COST*turn*size
    eq=np.cumprod(1+s); idx=df.index[1:]
    # rollierende Starts, kein Zeitlimit -> erster Treffer von Ziel/Barriere
    day=pd.Series(s,index=idx).resample("1D").apply(lambda x:(1+x).prod()-1)
    dr=day.to_numpy(); n=len(dr); ok=0; tot=0
    for st in range(0,n-30,5):
        e=1.0; peak=1.0; hit=None
        for k in range(st,n):
            e*=(1+dr[k])
            if dr[k]<-0.03: hit=False; break
            if e-1<=-0.06: hit=False; break
            if e-1>=0.10: hit=True; break
        if hit is not None: ok+=hit; tot+=1
    return ok/tot*100 if tot else 0, tot
for size in (0.35,0.5,1.0,2.0):
    L,S=signals(btc,"trend")
    pr,tot=passrate(btc,L,S,30,size)
    print(f"  Groesse {size:>4.2f}x Nominal   Pass-Rate {pr:>5.1f} %   ({tot} Starts)")
print("\n  Vergleich: reiner Zufall bei diesen Regeln = DD/(DD+Ziel) = 37,5 %")
print("  Vergleich: S/R-Ausbruch bei 0,35x                        = 53,8 %")
