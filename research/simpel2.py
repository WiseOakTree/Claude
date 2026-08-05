"""Die Vermutung: Es gibt gar keine "Strategien". Es gibt nur EFFEKTIVE
VOLATILITAET und KOSTEN. Wenn das stimmt, muss die Pass-Rate jeder Variante
allein aus ihrer Jahresvol vorhersagbar sein -- unabhaengig davon, welcher
Indikator sie erzeugt hat.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/simpel.py").read().split('VARIANTS=[')[0])

VAR=[("Basis 0,5x",dict()),("Basis 0,25x",dict(lev=0.25)),("Basis 1,0x",dict(lev=1.0)),
     ("1 Position",dict(one_at_a_time=True)),("1 Pos, 0,25x",dict(one_at_a_time=True,lev=0.25)),
     ("nur long",dict(long_only=True)),("nur long 1,0x",dict(long_only=True,lev=1.0)),
     ("24h halten",dict(hold=24)),(">=10 Beruehr.",dict(min_touch=10)),
     (">=10, 1,0x",dict(min_touch=10,lev=1.0)),(">=10, 3,0x",dict(min_touch=10,lev=3.0)),
     ("1 Pos+long+>=10",dict(one_at_a_time=True,long_only=True,min_touch=10))]

rows=[]
print("="*94)
print("Sagt die effektive Volatilitaet die Pass-Rate voraus?  (BTC, ganze Historie)")
print("="*94)
print(f"  {'Variante':18s} {'Zeit im Markt':>13s} {'Jahresvol':>10s} "
      f"{'Kosten p.a.':>12s} {'Pass':>7s} {'Zufall @Vol':>12s}")
print("  "+"-"*76)
# Referenzkurve reiner Zufall
rng=np.random.default_rng(5)
def zuf(vol,n=15000,maxd=365):
    sd=vol/np.sqrt(365); r=rng.normal(0,sd,size=(n,maxd))
    eq=np.ones(n); done=np.zeros(n,int)
    for i in range(maxd):
        if (done==0).sum()==0: break
        x=r[:,i]; live=done==0
        done[live&(x<-.03)]=3; live=done==0
        eq[live]*=(1+x[live]); done[live&(eq<=.94)]=2; live=done==0
        done[live&(eq>=1.10)]=1
    return (done==1).mean()*100

for name,kw in VAR:
    s,_=build("btc",**kw); s=s.dropna()
    d=((1+s).resample("1D").prod()-1).dropna().to_numpy()
    vol=d.std()*np.sqrt(365)*100
    # Kosten: Turnover * COST, annualisiert
    lev=kw.get("lev",0.5)
    kw2=dict(kw); s0,_=build("btc",**kw2)
    yrs=(s.index[-1]-s.index[0]).days/365.25
    # Turnoveranteil grob: Kostenanteil der Gesamtrendite
    h=pd.Series(pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)["close"].to_numpy(),
                index=s0.index if len(s0)==len(s0) else None)
    tim=(s!=0).mean()*100
    p=pr(d); z=zuf(vol/100)
    rows.append((vol,p))
    print(f"  {name:18s} {tim:>12.0f}% {vol:>9.1f}% {'':>12s} {p:>6.1f}% {z:>11.1f}%")

v=np.array([r[0] for r in rows]); q=np.array([r[1] for r in rows])
print(f"\n  Korrelation Jahresvol <-> Pass-Rate ueber alle Varianten: {np.corrcoef(v,q)[0,1]:+.2f}")
print(f"  Varianten mit 12-20 % Vol: Pass {q[(v>=12)&(v<=20)].mean():.1f}%")
print(f"  Varianten unter 8 % Vol:   Pass {q[v<8].mean():.1f}%")
print(f"  Varianten ueber 30 % Vol:  Pass {q[v>30].mean():.1f}%")
