"""Teil 6: Was die Stellschrauben wirklich bewegen -- Groesse, Haltedauer,
Richtung, Handelsfrequenz. Fuer den Fall, dass die Kombination trotzdem
gehandelt wird."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h, signals
COST=8e-4; btc=bars4h("btc")
L,S=signals(btc,"trend")
print("="*72); print("Handelsfrequenz und Gebuehrenlast auf 4h"); print("="*72)
jahre=(btc.index[-1]-btc.index[0]).days/365.25
for name,(l,s,hold) in {"MACD-Kreuzung allein":(None,None,1),
                        "Trend-Konfluenz, 1 Bar":(L,S,1),
                        "Trend-Konfluenz, 5 Tage halten":(L,S,30)}.items():
    if l is None:
        from msb import macd
        line,sg,_=macd(btc.close); n=int(((line>sg)&(line.shift(1)<=sg.shift(1))).sum()*2)
    else:
        d=np.where(l.to_numpy(),1,np.where(s.to_numpy(),-1,0)); i=0; n=0
        while i<len(d):
            if d[i]!=0: n+=1; i+=hold
            else: i+=1
    print(f"  {name:<32} {n/jahre:>5.0f} Trades/Jahr  = "
          f"{n/jahre*2*COST*100:>4.1f} % Gebuehren p.a. bei 1x")

print("\n"+"="*72); print("Was die Pass-Rate wirklich bewegt (BTC gesamt)"); print("="*72)
def pr(pos):
    c=btc.close.to_numpy(); ret=np.diff(c)/c[:-1]
    turn=np.abs(np.diff(np.concatenate([[0],pos])))[:-1]
    s=pos[:-1]*ret-COST*turn
    day=pd.Series(s,index=btc.index[1:]).resample("1D").apply(lambda x:(1+x).prod()-1).to_numpy()
    ok=tot=0
    for st in range(0,len(day)-30,5):
        e=1.0
        for k in range(st,len(day)):
            e*=(1+day[k])
            if day[k]<-0.03 or e-1<=-0.06: hit=False; break
            if e-1>=0.10: hit=True; break
        else: continue
        ok+=hit; tot+=1
    return ok/tot*100 if tot else 0
def build(l,s,hold,size):
    d=np.where(l.to_numpy(),1,np.where(s.to_numpy(),-1,0))
    pos=np.zeros(len(d)); i=0
    while i<len(d):
        if d[i]!=0: pos[i:i+hold]=d[i]*size; i+=hold
        else: i+=1
    return pos
none=pd.Series(False,index=L.index)
print(f"{'':<30}{'0,25x':>8}{'0,35x':>8}{'0,50x':>8}{'1,00x':>8}")
for nm,(l,s,h) in {"long+short, 5 Tage":(L,S,30),
                   "NUR LONG, 5 Tage":(L,none,30),
                   "long+short, 1 Bar":(L,S,1),
                   "NUR LONG, 2 Tage":(L,none,12)}.items():
    print(f"  {nm:<28}" + "".join(f"{pr(build(l,s,h,sz)):>7.1f}%" for sz in (0.25,0.35,0.5,1.0)))
