"""Die kombinierte Bauform: N Konten, jedes mit versetzten Tranchen."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("condor.py").read().split('print("="*94)')[0])
PUFFER=0.06; X,W,STOP=0.05,0.025,0.50

def cyc(offset,T0=21):
    out=[]; i=offset
    while i+T0<len(d):
        S=d.px.iloc[i]; atm=d.iv.iloc[i]/100; T=T0/252
        Kp,Kc=S*(1-X),S*(1+X); Lp,Lc=S*(1-X-W),S*(1+X+W)
        pr=lambda K,t: bsprice(S,K,T,iv_at(atm,np.log(K/S),0.7),t)
        cr=(pr(Kp,"p")+pr(Kc,"c"))-(pr(Lp,"p")+pr(Lc,"c"))-S*4e-4
        ST=d.px.iloc[i+T0]; L=0.0
        if ST<Kp: L=min(Kp-ST,Kp-Lp)
        elif ST>Kc: L=min(ST-Kc,Lc-Kc)
        out.append(max((cr-L)/S, -STOP*(W*S-cr)/S)); i+=T0
    return np.array(out)

legs=[cyc(o) for o in (0,7,14)]; n=min(len(l) for l in legs)
solo=legs[0][:n]
stag=np.mean([l[:n] for l in legs],axis=0)

def sim(s,dd,months=12):
    su=[];re=[]
    for st in range(0,len(s)-months):
        e=1.0;a=True
        for k in range(st,st+months):
            e*=(1+s[k])
            if e<=1-dd: a=False;break
        su.append(a);re.append(e-1 if a else -dd)
    return np.array(su).mean()*100, np.array(re).mean()*100

print("="*94)
print("DIE KOMBINIERTE BAUFORM")
print("="*94)
print(f"  {'Aufbau':>34s} {'schlecht. Zyklus':>17s} {'% Puffer':>9s} "
      f"{'ueberlebt':>10s} {'Ø p.a.':>8s} {'$ / Jahr':>11s}")
print("  "+"-"*88)
best=None
for name,series,N in [("1 Konto, 1 Tranche",solo,1),("1 Konto, 3 Tranchen",stag,1),
                      ("3 Konten, 1 Tranche",solo,3),("3 Konten, 3 Tranchen",stag,3)]:
    for L in [4,5,6,7]:
        worst=abs(series.min())*L
        if worst>PUFFER*0.95: continue
        su,re=sim(series*L,PUFFER)
        tot=re*1000*N
        line=f"  {name+f', {L}x':>34s} {series.min()*L*100:>16.2f}% {worst/PUFFER*100:>8.0f}% "\
             f"{su:>9.1f}% {re:>+7.1f}% {tot:>10,.0f} $"
        print(line)
        if best is None or (su>=99.9 and tot>best[0]): best=(tot,name,L,su,re,worst)
    print()

print("="*94)
print("EMPFEHLUNG")
print("="*94)
tot,name,L,su,re,worst=best
print(f"""  {name}, {L}x je Konto

    Ø Rendite je Konto      {re:+.1f} % p.a.
    Ueberlebensrate         {su:.1f} %
    schlechtester Zyklus    {worst/L*100:.2f} % des Nominals -> {worst*100:.2f} % des Kontos
                            = {worst/PUFFER*100:.0f} % des 6.000-$-Puffers
    GESAMT auf 3 Konten     {tot:,.0f} $ im Jahr (100 % Split)
""")
print("="*94)
print("Die Kosten, ehrlich")
print("="*94)
print(f"""  3 Evaluierungen bei ~400 $ und 90,9 % Bestehensquote:
    erwartete Kosten         ~1.320 $
    erwartete Dauer          ~142 Tage (parallel, nicht nacheinander)

  Laufende Kosten je Konto (Kommissionen bereits im Modell):
    4 Legs je Zyklus, 12 Zyklen im Jahr, {L} Kontrakteinheiten
    -> bereits in den {re:+.1f} % enthalten (1 bp je Leg)

  Erwartungswert im ersten Jahr: {tot:,.0f} $ minus 1.320 $ = {tot-1320:,.0f} $""")
