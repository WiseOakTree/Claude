"""Teil 4: Die Kontrolle. Kommt die Pass-Rate von 50,5 % aus den Indikatoren
oder aus dem BTC-Aufwaertsdrift?"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, signals
COST=8e-4
btc=bars4h("btc")
L,S=signals(btc,"trend")
print(f"Long-Signale:  {L.sum():>4}   Short-Signale: {S.sum():>4}   "
      f"Long-Anteil {L.sum()/(L.sum()+S.sum())*100:.1f} %")

def passrate_from_pos(df,pos,turn_cost=True):
    c=df.close.to_numpy(); ret=np.diff(c)/c[:-1]; held=pos[:-1]
    turn=np.abs(np.diff(np.concatenate([[0],pos])))[:-1] if turn_cost else 0
    s=held*ret-COST*turn
    day=pd.Series(s,index=df.index[1:]).resample("1D").apply(lambda x:(1+x).prod()-1).to_numpy()
    n=len(day); ok=tot=0
    for st in range(0,n-30,5):
        e=1.0
        for k in range(st,n):
            e*=(1+day[k])
            if day[k]<-0.03 or e-1<=-0.06: hit=False; break
            if e-1>=0.10: hit=True; break
        else: continue
        ok+=hit; tot+=1
    return ok/tot*100 if tot else 0,tot

def build(L,S,hold,size):
    d=np.where(L.to_numpy(),1,np.where(S.to_numpy(),-1,0))
    pos=np.zeros(len(d)); i=0
    while i<len(d):
        if d[i]!=0: pos[i:i+hold]=d[i]*size; i+=hold
        else: i+=1
    return pos

print("\n" + "="*70)
print("Kontrollen bei 0,35x Nominal, gleiche Regeln")
print("="*70)
rows=[]
pr,_=passrate_from_pos(btc,build(L,S,30,0.35));            rows.append(("MACD+Stoch+BB (Trend)",pr))
pr,_=passrate_from_pos(btc,build(L,S,30,0.35)*0+0.35);     rows.append(("Nur long, immer drin",pr))
pr,_=passrate_from_pos(btc,build(L,pd.Series(False,index=S.index),30,0.35))
rows.append(("Nur die Long-Signale",pr))
pr,_=passrate_from_pos(btc,build(pd.Series(False,index=L.index),S,30,0.35))
rows.append(("Nur die Short-Signale",pr))
# Zufallssignale gleicher Anzahl
rng=np.random.default_rng(7); zs=[]
for _ in range(200):
    idx=rng.choice(len(L),size=int(L.sum()+S.sum()),replace=False)
    d=np.zeros(len(L)); d[idx]=rng.choice([1,-1],size=len(idx))
    pos=np.zeros(len(d)); i=0
    while i<len(d):
        if d[i]!=0: pos[i:i+30]=d[i]*0.35; i+=30
        else: i+=1
    p,_=passrate_from_pos(btc,pos); zs.append(p)
rows.append((f"200x Zufall gleicher Anzahl (Median)",float(np.median(zs))))
for k,v in rows: print(f"  {k:<38} {v:>5.1f} %")
print(f"\n  Zufallsverteilung: 5 %-Quantil {np.percentile(zs,5):.1f} %   "
      f"95 %-Quantil {np.percentile(zs,95):.1f} %")
print(f"  Perzentil der Indikator-Strategie darin: "
      f"{(np.array(zs) < rows[0][1]).mean()*100:.0f}.")
