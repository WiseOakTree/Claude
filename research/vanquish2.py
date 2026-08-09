"""Die Evaluierung selbst: Bestehenswahrscheinlichkeit und erwartete Kosten."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
SP=pd.read_csv("straddle_SP500.csv",index_col=0,parse_dates=True).iloc[:,0].to_numpy()
ic=np.clip(SP,-0.008,None)*0.40      # enger Condor -- die tragbare Variante

def eval_pass(x,target,dd,cap_days=252):
    p=f=c=0; dur=[]
    for st in range(0,len(x)-60,2):
        e=1.0; out=None
        for i in range(st,min(st+cap_days,len(x))):
            e*=(1+x[i])
            if e<=1-dd: out="f";break
            if e-1>=target: out="p";dur.append(i-st);break
        if out=="p":p+=1
        elif out=="f":f+=1
        else:c+=1
    t=p+f+c
    return p/t*100, (np.median(dur) if dur else np.nan), c/t*100

print("="*88)
print("Die Evaluierung: Bestehenswahrscheinlichkeit je Hebel")
print("  (Enger Iron Condor, Kappe 0,8 %, Ziel 8 %, EOD-Drawdown 6 %)")
print("="*88)
print(f"  {'Hebel':>6s} {'max. Einzelverl.':>17s} {'bestanden':>10s} "
      f"{'Median Dauer':>13s} {'unaufgeloest':>13s}")
print("  "+"-"*64)
for L in [1,1.5,2,2.5,3,4]:
    p,d,c=eval_pass(ic*L,0.08,0.06)
    print(f"  {L:>5.1f}x {0.008*L*100:>16.1f}% {p:>9.1f}% "
          f"{d:>12.0f}T {c:>12.1f}%")

print()
print("="*88)
print("Erwartete Gesamtkosten bis zum gefundeten Konto")
print("="*88)
p3,_,_=eval_pass(ic*3,0.08,0.06)
p3/=100
print(f"  Bestehenswahrscheinlichkeit je Versuch (3x): {p3*100:.0f} %")
print(f"  {'Versuche':>9s} {'P(gefunded)':>12s} {'Ø Einsatz bei 400 $':>21s}")
print("  "+"-"*46)
for n in [1,2,3,4]:
    pn=1-(1-p3)**n
    exp=sum(400*(1-p3)**k for k in range(n))
    print(f"  {n:>9d} {pn*100:>11.1f}% {exp:>20.0f} $")
print(f"\n  (naive Unabhaengigkeit -- in Wirklichkeit clustern Fehlschlaege,")
print(f"   siehe spielregeln.md. Rechne mit dem oberen Rand der Kosten.)")

print()
print("="*88)
print("ENDRECHNUNG: Was bleibt realistisch uebrig?")
print("="*88)
def sim(x,dd,days=252,step=3):
    s=[];r=[]
    for st in range(0,len(x)-days,step):
        e=1.0;a=True
        for k in range(st,st+days):
            e*=(1+x[k])
            if e<=1-dd: a=False;break
        s.append(a);r.append(e-1 if a else -dd)
    s=np.array(s);r=np.array(r); return s.mean()*100,r.mean()*100,((s)&(r>=.20)).mean()*100
print(f"  {'Hebel':>6s} {'Puffer-Anteil':>14s} {'ueberlebt':>10s} {'Ø p.a.':>9s} "
      f"{'>=20 %':>8s} {'Ø $ auf 100k':>14s}")
print("  "+"-"*68)
for L in [2,2.5,3,4]:
    s,r,p=sim(ic*L,0.06)
    print(f"  {L:>5.1f}x {0.008*L/0.06*100:>13.0f}% {s:>9.1f}% {r:>+8.1f}% "
          f"{p:>7.1f}% {r*1000:>13,.0f} $")
print("\n  100 % Profit-Split -> der Bruttobetrag ist der Nettobetrag.")
