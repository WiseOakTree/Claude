"""Positionsgroesse mit den ECHTEN Condor-Zahlen -- Risikobudget zuerst."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("condor.py").read().split('print("="*94)')[0])

PUFFER=0.06
print("="*92)
print("Die ehrliche Endrechnung: echter Condor, echter Skew, kein Hedge")
print("="*92)
r,cr,st,ml=condor(0.05,0.015,skew=0.7,stop=0.35)
maxl=0.015-cr                                   # Maximalverlust je Einheit Nominal
stopl=0.35*maxl
ann=(1+r).prod()**(12/len(r))-1
print(f"""  Konfiguration: Strangle +-5 %, Fluegel 1,5 %, Stop bei 35 % vom Maximalverlust
    Kredit je Zyklus      {cr*100:.3f} % des Nominals  ({cr/st*100:.1f} % der Straddle-Praemie)
    Maximalverlust        {maxl*100:.2f} % -- durch den Stop gekappt auf {stopl*100:.2f} %
    schlechtester Monat   {r.min()*100:.2f} %
    Rendite p.a.          {ann*100:+.2f} %   Sharpe {r.mean()/r.std()*np.sqrt(12):.2f}
""")
print(f"  {'Nominal':>9s} {'Verlust je Stopp':>17s} {'Anteil Puffer':>14s} {'Rendite p.a.':>13s} "
      f"{'schlecht. Monat':>16s}")
print("  "+"-"*76)
for N in [1,2,3,4,5,6,8,10]:
    v=stopl*N
    print(f"  {N:>8d}x {v*100:>16.2f}% {v/PUFFER*100:>13.0f}% {ann*N*100:>+12.1f}% "
          f"{r.min()*N*100:>15.2f}%")

print()
print("="*92)
print("Jahres-Simulation gegen den 6-%-Boden")
print("="*92)
x=r.to_numpy()
def sim(x,dd,months=12,step=1):
    s=[];ret=[]
    for st_ in range(0,len(x)-months,step):
        e=1.0;a=True
        for k in range(st_,st_+months):
            e*=(1+x[k])
            if e<=1-dd: a=False;break
        s.append(a);ret.append(e-1 if a else -dd)
    s=np.array(s);ret=np.array(ret)
    return s.mean()*100,ret.mean()*100,((s)&(ret>=.20)).mean()*100
print(f"  {'Nominal':>9s} {'ueberlebt':>10s} {'Ø p.a.':>9s} {'>=20 %':>8s} {'$ auf 100k':>12s}")
print("  "+"-"*54)
for N in [2,4,6,8,10,12]:
    a,b,c=sim(x*N,PUFFER)
    print(f"  {N:>8d}x {a:>9.1f}% {b:>+8.1f}% {c:>7.1f}% {b*1000:>11,.0f} $")

print()
print("="*92)
print("VERGLEICH: was meine Naeherung behauptete gegen das echte Modell")
print("="*92)
print(f"""  {'':34s} {'Naeherung':>12s} {'echt':>12s}
  {'-'*60}
  {'Anteil der Straddle-Praemie':34s} {'40-55 %':>12s} {'4-11 %':>12s}
  {'Rendite p.a. auf Nominal':34s} {'+6,2 %':>12s} {'+2,4 %':>12s}
  {'Sharpe':34s} {'2,55':>12s} {'2,38':>12s}
  {'Delta-Drag enthalten':34s} {'NEIN':>12s} {'ja':>12s}
  {'Skew enthalten':34s} {'NEIN':>12s} {'ja':>12s}

  -> Der Sharpe haelt. Die RENDITE je Einheit Nominal ist weniger
     als die Haelfte. Das muss ueber mehr Nominal aufgeholt werden,
     und dafuer ist der 6.000-$-Puffer die Bremse.""")
