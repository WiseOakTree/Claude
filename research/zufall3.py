"""Was gibt REINER ZUFALL unter anderen Regelwerken?
Null Drift, null Kosten, Volatilitaet je Regelwerk optimiert.
Damit ist es die Untergrenze fuer "wie leicht ist diese Challenge ohne Koennen".
"""
import numpy as np
rng=np.random.default_rng(11)
def sim(tgt,dd,day,vol,drift=0.0,n=25000,maxd=365):
    sd=vol/np.sqrt(365); mu=drift/365
    r=rng.normal(mu,sd,size=(n,maxd)); eq=np.ones(n); done=np.zeros(n,int)
    for i in range(maxd):
        if (done==0).sum()==0: break
        x=r[:,i]; live=done==0
        if day is not None:
            done[live&(x<-day)]=3; live=done==0
        eq[live]*=(1+x[live]); done[live&(eq<=1-dd)]=2; live=done==0
        done[live&(eq>=1+tgt)]=1
    return (done==1).mean()*100
VOLS=[.08,.10,.12,.15,.20,.25,.30,.40]
RULES=[("Kraken Starter",.10,.06,.03),
       ("Kraken, aber 5 % Tageslimit",.10,.06,.05),
       ("Kraken, aber kein Tageslimit",.10,.06,None),
       ("6 % Ziel / 6 % DD / 3 %",.06,.06,.03),
       ("6 % Ziel / 10 % DD / 5 %",.06,.10,.05),
       ("8 % Ziel / 10 % DD / kein Tag",.08,.10,None),
       ("Zwei-Phasen-Typ 8%+5% / 10 % DD",.13,.10,.05)]
print("="*84)
print("REINER ZUFALL unter verschiedenen Regelwerken (Vol optimiert, kein Drift)")
print("="*84)
print(f"  {'Regelwerk':32s} {'beste Vol':>10s} {'BESTANDEN':>11s} {'theor. Ruin':>12s}")
print("  "+"-"*68)
for name,tgt,dd,day in RULES:
    best=max((sim(tgt,dd,day,v),v) for v in VOLS)
    ruin=dd/(dd+tgt)*100
    print(f"  {name:32s} {best[1]*100:>9.0f}% {best[0]:>10.1f}% {ruin:>11.1f}%")
print()
print("  'theor. Ruin' = DD/(DD+Ziel): der Wert ohne Tageslimit und ohne Drift.")
print("  Er haengt NUR vom Verhaeltnis Ziel zu Drawdown ab -- nicht vom Koennen.")
