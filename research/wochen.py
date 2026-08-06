"""Die Konsistenzregel zwingt zu MEHR Trades, nicht zu weniger.
Bei 12 Zyklen im Jahr traegt jeder Gewinner ~10 % -- ein guter reisst die
30-%-Marke. Bei 52 Wochenzyklen sind es ~2 %. SPX hat Wochenverfalle.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("condor.py").read().split('print("="*94)')[0])
X,W,STOP=0.05,0.025,0.50

def run(T0):
    out=[]; i=0
    while i+T0<len(d):
        S=d.px.iloc[i]; atm=d.iv.iloc[i]/100; T=T0/252
        # Strikes an die Laufzeit anpassen: gleiche Trefferwahrscheinlichkeit
        sc=np.sqrt(T0/21)
        xx,ww=X*sc, W*sc
        Kp,Kc=S*(1-xx),S*(1+xx); Lp,Lc=S*(1-xx-ww),S*(1+xx+ww)
        pr=lambda K,t: bsprice(S,K,T,iv_at(atm,np.log(K/S),0.7),t)
        cred=(pr(Kp,"p")+pr(Kc,"c"))-(pr(Lp,"p")+pr(Lc,"c"))-S*4e-4
        ST=d.px.iloc[i+T0]; L=0.0
        if ST<Kp: L=min(Kp-ST,Kp-Lp)
        elif ST>Kc: L=min(ST-Kc,Lc-Kc)
        out.append(max((cred-L)/S, -STOP*(ww*S-cred)/S)); i+=T0
    return np.array(out), xx, ww

print("="*92)
print("WOCHEN- GEGEN MONATSZYKLEN -- was macht die Konsistenzregel?")
print("="*92)
print(f"  {'Laufzeit':>10s} {'Zyklen/J':>9s} {'Strikes':>9s} {'p.a.':>8s} {'Sharpe':>7s} "
      f"{'bester Trade: Median':>21s} {'>30 %':>8s}")
print("  "+"-"*80)
for T0,lab in [(5,"1 Woche"),(10,"2 Wochen"),(21,"1 Monat"),(42,"2 Monate")]:
    x,xx,ww=run(T0)
    per_year=252/T0
    ann=(1+pd.Series(x)).prod()**(per_year/len(x))-1
    sh=x.mean()/x.std()*np.sqrt(per_year)
    n=int(round(per_year))
    rr=[]
    for st in range(0,len(x)-n):
        w=x[st:st+n]; t=w.sum()
        if t>0: rr.append(w.max()/t*100)
    rr=np.array(rr)
    print(f"  {lab:>10s} {per_year:>8.0f} {'+-'+f'{xx*100:.1f}'+'%':>9s} {ann*100:>+7.2f}% "
          f"{sh:>7.2f} {np.median(rr):>20.1f}% {(rr>30).mean()*100:>7.1f}%")

print("""
  -> Kuerzere Zyklen loesen die Konsistenzregel: mehr Trades heisst,
     dass kein einzelner die 30-%-Marke reissen kann.
     Und der Sharpe steigt mit, weil oefter abgerechnet wird.""")

print()
print("="*92)
print("Die andere Loesung: spaeter auszahlen")
print("="*92)
x,_,_=run(21)
print(f"  {'Sammelzeitraum':>18s} {'Median bester Trade':>21s} {'Anteil ueber 30 %':>19s}")
print("  "+"-"*62)
for M,lab in [(3,"3 Monate"),(6,"6 Monate"),(12,"12 Monate"),(24,"24 Monate")]:
    rr=[]
    for st in range(0,len(x)-M):
        w=x[st:st+M]; t=w.sum()
        if t>0: rr.append(w.max()/t*100)
    rr=np.array(rr)
    print(f"  {lab:>18s} {np.median(rr):>20.1f}% {(rr>30).mean()*100:>18.1f}%")
print("""
  -> Wer monatlich auszahlen will, reisst die Regel in 100 % der Faelle.
     Wer zwei Jahre sammelt, in 3 %. Aber dann ist es kein Einkommen mehr.
     Die Wochenzyklen sind die bessere Loesung.""")
