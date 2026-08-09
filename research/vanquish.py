"""KORREKTUR. Mein Hebel-Sweep war falsch gedacht.

Bei definierten Spreads ist nicht das Nominal die Bindung, sondern der
MAXIMALVERLUST je Zyklus gegen einen Puffer von 6.000 $. Ein 6x-Hebel auf
100.000 $ Nominal bedeutet einen Maximalverlust, der den Puffer uebersteigt --
das Konto ist nach EINEM Ereignis weg.

Richtig gerechnet: Risikobudget zuerst, Hebel danach.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
SP=pd.read_csv("straddle_SP500.csv",index_col=0,parse_dates=True).iloc[:,0].to_numpy()

PUFFER=0.06          # 6.000 $ auf 100.000 $
print("="*92)
print("KORREKTUR: Der Hebel wird vom RISIKOBUDGET bestimmt, nicht vom Nominal")
print("="*92)
print(f"""  Konto 100.000 $, statischer Boden bei 94.000 $ -> Puffer 6.000 $.
  Ein Iron Condor mit Kappe c (Anteil des Nominals) und Hebel L
  verliert im Ereignisfall  c * L  des Kontos.

  {'Kappe':>7s} {'Hebel':>7s} {'Verlust je Ereignis':>21s} {'Anteil des Puffers':>20s}""")
print("  "+"-"*60)
for cap in [0.008,0.012,0.020]:
    for L in [1,2,3,6]:
        v=cap*L
        flag="  KONTO WEG" if v>=PUFFER else ""
        print(f"  {cap*100:>6.1f}% {L:>6d}x {v*100:>20.1f}% {v/PUFFER*100:>19.0f}%{flag}")
print("\n  -> Meine 6-8x waren nicht konservativ falsch, sondern strukturell falsch.")

print()
print("="*92)
print("Richtig: Wie viel Hebel traegt ein 6.000-$-Puffer wirklich?")
print("="*92)
def sim(x,dd,days=252,step=3):
    surv=[];rets=[]
    for st in range(0,len(x)-days,step):
        e=1.0;alive=True
        for k in range(st,st+days):
            e*=(1+x[k])
            if e<=1-dd: alive=False;break
        surv.append(alive);rets.append(e-1 if alive else -dd)
    s=np.array(surv);r=np.array(rets)
    return s.mean()*100,r.mean()*100,((s)&(r>=.20)).mean()*100

print(f"  {'Kappe':>7s} {'Hebel':>6s} {'max. Einzelverlust':>19s} {'ueberlebt':>10s} "
      f"{'Ø p.a.':>9s} {'>=20 %':>8s} {'Urteil':>22s}")
print("  "+"-"*86)
for cap,keep in [(0.008,0.40),(0.012,0.55),(0.020,0.70)]:
    ic=np.clip(SP,-cap,None)*keep
    for L in [1,1.5,2,2.5,3,4]:
        v=cap*L
        s,r,p=sim(ic*L,PUFFER)
        if v>=PUFFER*0.8: urteil="1 Ereignis = Ende"
        elif v>=PUFFER*0.4: urteil="1 Ereignis = halber Puffer"
        else: urteil="tragbar"
        print(f"  {cap*100:>6.1f}% {L:>5.1f}x {v*100:>18.1f}% {s:>9.1f}% "
              f"{r:>+8.1f}% {p:>7.1f}% {urteil:>22s}")
    print()

print("="*92)
print("Die Konsistenzregel: passt die Strategie?  (kein Tag > 30-40 % des Gewinns)")
print("="*92)
ic=np.clip(SP,-0.012,None)*0.55
res=[]
for st in range(0,len(ic)-252,5):
    w=ic[st:st+252]
    tot=w.sum()
    if tot<=0: continue
    res.append(w.max()/tot*100)
res=np.array(res)
print(f"  Anteil des BESTEN Tages am Jahresgewinn:")
print(f"    Median {np.median(res):.1f} %   90. Perzentil {np.percentile(res,90):.1f} %   "
      f"Maximum {res.max():.1f} %")
print(f"    Jahre ueber 30 %: {(res>30).mean()*100:.1f} %   ueber 40 %: {(res>40).mean()*100:.1f} %")
print("\n  -> Optionsverkauf verdient ueber Theta, also gleichmaessig.")
print("     Die Konsistenzregel ist fuer diese Strategie KEIN Problem.")
