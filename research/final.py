"""Die echte Kette zeigt: breitere Fluegel haben ein VIEL besseres
Kredit/Risiko-Verhaeltnis. Das habe ich vorher nicht ausgereizt.
Vollstaendiger Sweep mit Stop, bewertet gegen den 6-%-Puffer.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("condor.py").read().split('print("="*94)')[0])
PUFFER=0.06

def sim(x,dd,months=12,step=1):
    s=[];r=[]
    for st in range(0,len(x)-months,step):
        e=1.0;a=True
        for k in range(st,st+months):
            e*=(1+x[k])
            if e<=1-dd: a=False;break
        s.append(a);r.append(e-1 if a else -dd)
    s=np.array(s);r=np.array(r)
    return s.mean()*100,r.mean()*100,((s)&(r>=.20)).mean()*100

print("="*96)
print("Vollstaendiger Sweep mit Stop bei 50 % des Maximalverlusts")
print("  (50 % statt 35 % -- konservativer, siehe Bestes-von-N-Warnung)")
print("="*96)
print(f"  {'Strangle':>9s} {'Fluegel':>8s} {'Kredit':>8s} {'max.Verl':>9s} {'Kr/Risiko':>10s} "
      f"{'p.a.':>7s} {'Sharpe':>7s} {'Stopverl.':>10s}")
print("  "+"-"*80)
cands=[]
for x in [0.02,0.025,0.03,0.04,0.05]:
    for w in [0.008,0.015,0.025,0.035]:
        r,cr,st,ml=condor(x,w,skew=0.7,stop=0.50)
        ann=(1+r).prod()**(12/len(r))-1
        sh=r.mean()/r.std()*np.sqrt(12)
        stopl=0.50*(w-cr)
        cands.append((sh,ann,x,w,cr,w-cr,stopl,r))
        print(f"  {x*100:>8.1f}% {w*100:>7.1f}% {cr*100:>7.3f}% {(w-cr)*100:>8.2f}% "
              f"{cr/(w-cr):>10.2f} {ann*100:>+6.2f}% {sh:>7.2f} {stopl*100:>9.2f}%")

print()
print("="*96)
print("Die drei besten nach Sharpe -- gegen den 6-%-Puffer")
print("="*96)
cands.sort(reverse=True,key=lambda t:t[0])
for sh,ann,x,w,cr,ml,stopl,r in cands[:3]:
    print(f"\n  Strangle +-{x*100:.1f} %, Fluegel {w*100:.1f} %  "
          f"(Sharpe {sh:.2f}, {ann*100:+.2f} % p.a. je Einheit Nominal)")
    print(f"    {'Nominal':>9s} {'Stopverlust':>12s} {'Anteil Puffer':>14s} "
          f"{'ueberlebt':>10s} {'Ø p.a.':>9s} {'$ auf 100k':>12s}")
    for N in [4,6,8,10,12]:
        v=stopl*N
        if v>PUFFER: continue
        a,b,c=sim(r.to_numpy()*N,PUFFER)
        print(f"    {N:>8d}x {v*100:>11.2f}% {v/PUFFER*100:>13.0f}% "
              f"{a:>9.1f}% {b:>+8.1f}% {b*1000:>11,.0f} $")
