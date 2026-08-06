"""Endstand mit Wochenzyklen -- gegen statischen UND trailenden Boden."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("condor.py").read().split('print("="*94)')[0])
X0,W0,STOP,T0=0.05,0.025,0.50,5
sc=np.sqrt(T0/21); X,W=X0*sc,W0*sc
out=[]; i=0
while i+T0<len(d):
    S=d.px.iloc[i]; atm=d.iv.iloc[i]/100; T=T0/252
    Kp,Kc=S*(1-X),S*(1+X); Lp,Lc=S*(1-X-W),S*(1+X+W)
    pr=lambda K,t: bsprice(S,K,T,iv_at(atm,np.log(K/S),0.7),t)
    cr=(pr(Kp,"p")+pr(Kc,"c"))-(pr(Lp,"p")+pr(Lc,"c"))-S*4e-4
    ST=d.px.iloc[i+T0]; L=0.0
    if ST<Kp: L=min(Kp-ST,Kp-Lp)
    elif ST>Kc: L=min(ST-Kc,Lc-Kc)
    out.append(max((cr-L)/S,-STOP*(W*S-cr)/S)); i+=T0
x=np.array(out); PY=252/T0; PUFFER=0.06
stopl=abs(x.min())
ann=(1+pd.Series(x)).prod()**(PY/len(x))-1
print("="*92)
print(f"ENDSTAND: Wochen-Condor, Strangle +-{X*100:.1f} %, Fluegel {W*100:.1f} %, Stop 50 %")
print(f"  {ann*100:+.2f} % p.a. je Einheit Nominal | Sharpe "
      f"{x.mean()/x.std()*np.sqrt(PY):.2f} | schlechtester Zyklus {x.min()*100:.3f} %")
print("="*92)

def sim(s,dd,mode,periods):
    su=[];re=[]
    for st in range(0,len(s)-periods):
        e=1.0;hi=1.0;a=True
        for k in range(st,st+periods):
            e*=(1+s[k])
            floor=(1-dd) if mode=="static" else (hi-dd)
            if mode=="trail": hi=max(hi,e)
            if e<=floor: a=False;break
        su.append(a);re.append(e-1 if a else -dd)
    return np.array(su).mean()*100, np.array(re).mean()*100

P=int(PY)
print(f"  {'Nominal':>8s} {'Stopverl.':>10s} {'% Puffer':>9s} "
      f"{'STATISCH ueberl./p.a.':>23s} {'TRAILING ueberl./p.a.':>23s} {'3 Konten $':>12s}")
print("  "+"-"*88)
for N in [4,6,8,10,12]:
    v=stopl*N
    if v>PUFFER: 
        print(f"  {N:>7d}x {v*100:>9.2f}% {v/PUFFER*100:>8.0f}%   -- Puffer gesprengt --")
        continue
    sa,ra=sim(x*N,PUFFER,"static",P)
    sb,rb=sim(x*N,PUFFER,"trail",P)
    print(f"  {N:>7d}x {v*100:>9.2f}% {v/PUFFER*100:>8.0f}% "
          f"{sa:>13.1f}% /{ra:>+7.1f}% {sb:>13.1f}% /{rb:>+7.1f}% {ra*3000:>11,.0f} $")
print(f"""
  -> Die letzten beiden Spaltenpaare sind der ganze Unterschied.
     STATISCH: das Geschaeft funktioniert.
     TRAILING: es funktioniert nicht -- bei keiner Groesse.""")
