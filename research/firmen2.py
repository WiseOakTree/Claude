import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
SP=pd.read_csv("straddle_SP500.csv",index_col=0,parse_dates=True).iloc[:,0].to_numpy()
def sim(x,dd,mode,days=252,step=3):
    surv=[];rets=[]
    for st in range(0,len(x)-days,step):
        e=1.0;hi=1.0;alive=True
        for k in range(st,st+days):
            e*=(1+x[k]); floor=(1.0-dd) if mode=="static" else (hi-dd)
            if mode!="static": hi=max(hi,e)
            if e<=floor: alive=False;break
        surv.append(alive);rets.append(e-1 if alive else -dd)
    s=np.array(surv);r=np.array(rets)
    return s.mean()*100,r.mean()*100,((s)&(r>=.20)).mean()*100

print("="*86)
print("3) Rettet weniger Hebel den TRAILING-Drawdown?")
print("="*86)
print(f"  {'':6s} " + " ".join(f"{d*100:>5.0f}% DD" for d in [0.03,0.05,0.08,0.10]))
print(f"  {'Hebel':6s} " + " ".join(f"{'ueberl./>=20%':>10s}" for _ in range(4)))
print("  "+"-"*54)
for L in [0.5,1,1.5,2,3]:
    row=f"  {L:>5.1f}x "
    for dd in [0.03,0.05,0.08,0.10]:
        s,_,p=sim(SP*L,dd,"eod"); row+=f"  {s:>4.0f}%/{p:>3.0f}% "
    print(row)
print("\n  -> Trailing bestraft den ERFOLG: jedes neue Hoch hebt den Boden mit.")
print("     Weniger Hebel hilft nur begrenzt, weil auch die Rendite mitschrumpft.")

print()
print("="*86)
print("4) Der Haken, der in keiner Anbieterliste steht: NACKTE Optionen")
print("="*86)
print("""  Ein Short-Straddle ist eine NACKTE Short-Option -- unbegrenztes Risiko.
  Nahezu alle Prop-Firmen verbieten das. Erlaubt sind definierte Risiken
  (Iron Condor, Credit Spread). Das aendert die Zahlen.

  Naeherung: Iron Condor = Short-Straddle mit gekappter Verlustseite.
  Die Fluegel kosten Praemie, begrenzen aber den Schwanz.""")
print()
print(f"  {'Variante':34s} {'p.a.':>8s} {'Vol':>7s} {'Sharpe':>8s} {'schlecht.Tag':>13s}")
print("  "+"-"*74)
def stats(x,n):
    a=(1+pd.Series(x)).prod()**(252/len(x))-1
    print(f"  {n:34s} {a*100:>+7.1f}% {x.std()*np.sqrt(252)*100:>6.1f}% "
          f"{x.mean()/x.std()*np.sqrt(252):>8.2f} {x.min()*100:>+12.2f}%")
stats(SP,"Short-Straddle (nackt)")
for keep,cap in [(0.70,0.020),(0.55,0.012),(0.40,0.008)]:
    ic=np.clip(SP,-cap,None)*keep
    stats(ic,f"Iron Condor (~{keep*100:.0f}% Praemie, Kappe {cap*100:.1f}%)")

print()
print("="*86)
print("5) Iron Condor auf einem STATISCHEN Drawdown -- was ist erreichbar?")
print("="*86)
ic=np.clip(SP,-0.012,None)*0.55
print(f"  {'Drawdown':>9s} {'bester Hebel':>13s} {'ueberlebt':>10s} {'Ø p.a.':>9s} {'>=20 %':>9s}")
print("  "+"-"*56)
for dd in [0.03,0.04,0.06,0.08,0.10]:
    best=(-99,None,None,None)
    for L in [2,3,4,5,6,8,10]:
        s,r,p=sim(ic*L,dd,"static")
        if p>best[0]: best=(p,L,s,r)
    print(f"  {dd*100:>8.0f}% {best[1]:>12d}x {best[2]:>9.1f}% {best[3]:>+8.1f}% {best[0]:>8.1f}%")
