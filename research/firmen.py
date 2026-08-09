"""Die vier Anbieter gegen die Strategie gerechnet.

Der entscheidende Unterschied steht NICHT im Tageslimit -- der ist bei allen
vier weg. Er steht in der DRAWDOWN-MECHANIK:
  statisch      Boden fix ab Start
  EOD-trailing  Boden folgt dem Tagesschluss-Hoch
  Intraday-tr.  Boden folgt dem laufenden Hoch (Apex)
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

SP=pd.read_csv("straddle_SP500.csv",index_col=0,parse_dates=True).iloc[:,0].to_numpy()

def sim(x, dd, mode, days=252, step=3):
    """mode: 'static' | 'eod' | 'intra'. Rueckgabe (Ueberlebensrate, Ø Rendite, Anteil>=20%)."""
    surv=[]; rets=[]
    for st in range(0,len(x)-days,step):
        e=1.0; hi=1.0; alive=True
        for k in range(st,st+days):
            r=x[k]
            if mode=="intra":
                # Naeherung: das laufende Hoch liegt um die halbe Tagesspanne
                # ueber dem Schluss, wenn der Tag negativ endete
                hi=max(hi, e*(1+max(r,0)*1.0) if r>0 else e)
                e*=(1+r)
                floor=hi-dd
                hi=max(hi,e)
            else:
                e*=(1+r)
                floor=(1.0-dd) if mode=="static" else (hi-dd)
                if mode=="eod": hi=max(hi,e)
            if e<=floor: alive=False;break
        surv.append(alive); rets.append(e-1 if alive else -dd)
    s=np.array(surv); r=np.array(rets)
    return s.mean()*100, r.mean()*100, ((s)&(r>=.20)).mean()*100

print("="*94)
print("1) DIE DRAWDOWN-MECHANIK IST DER GANZE UNTERSCHIED")
print("   S&P-500-Straddle, 3x Hebel, kein Tageslimit bei allen")
print("="*94)
print(f"  {'Drawdown':>9s}  {'STATISCH (Vanquish live)':>34s}  {'EOD-TRAILING (MFF)':>30s}")
print(f"  {'':>9s}  {'ueberlebt':>10s} {'Ø p.a.':>9s} {'>=20 %':>9s}  "
      f"{'ueberlebt':>10s} {'Ø p.a.':>9s} {'>=20 %':>9s}")
print("  "+"-"*88)
for dd in [0.02,0.03,0.04,0.05,0.06,0.08,0.10]:
    a=sim(SP*3,dd,"static"); b=sim(SP*3,dd,"eod")
    print(f"  {dd*100:>8.0f}%  {a[0]:>9.1f}% {a[1]:>+8.1f}% {a[2]:>8.1f}%  "
          f"{b[0]:>9.1f}% {b[1]:>+8.1f}% {b[2]:>8.1f}%")

print()
print("="*94)
print("2) DIE ZAHL, DIE IN DEINER LISTE FEHLT: wie GROSS ist der Drawdown?")
print("="*94)
print("""  Typische Futures-Prop-Konten (100.000 $ Nominal):
    Apex 100k        ~3.000 $ trailing   =  3,0 %
    MFF 100k         ~2.000-3.000 $      =  2-3 %
    TradeDay 100k    ~2.000-4.000 $      =  2-4 %
    Kraken Prop      6 % statisch

  -> Futures-Props sind beim Drawdown ENGER als Kraken, nicht weiter.
     Das kein-Tageslimit-Argument wird davon teilweise wieder aufgefressen.""")
print()
print("  Was das bedeutet -- bester Hebel je Drawdown-Groesse (statisch):")
print(f"  {'Drawdown':>9s} {'bester Hebel':>13s} {'ueberlebt':>10s} {'Ø p.a.':>9s} {'>=20 %':>9s}")
print("  "+"-"*56)
for dd in [0.02,0.03,0.04,0.06,0.08,0.10]:
    best=(-99,None,None,None)
    for L in [1,2,3,4,5,6,8]:
        s,r,p=sim(SP*L,dd,"static")
        if p>best[0]: best=(p,L,s,r)
    print(f"  {dd*100:>8.0f}% {best[1]:>12d}x {best[2]:>9.1f}% {best[3]:>+8.1f}% {best[0]:>8.1f}%")
