"""Mehrere 100k-Konten parallel gegen EIN Konto mit mehr Hebel.

Der Kern: Bei N Konten waechst der PUFFER mit N mit. Bei Hebel nicht.
Zusaetzlich geprueft: Bringt es etwas, die Verfallszyklen zu versetzen?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("condor.py").read().split('print("="*94)')[0])
PUFFER=0.06

# Beste Konfiguration aus dem Sweep
X,W,STOP=0.05,0.025,0.50
r,cr,st,ml=condor(X,W,skew=0.7,stop=STOP)
stopl=STOP*(W-cr)
x=r.to_numpy()
ann=(1+r).prod()**(12/len(r))-1
print("="*92)
print(f"Basis: Strangle +-{X*100:.0f} %, Fluegel {W*100:.1f} %, Stop {STOP*100:.0f} %")
print(f"  {ann*100:+.2f} % p.a. je Einheit Nominal, Stopverlust {stopl*100:.2f} % des Nominals")
print("="*92)

def sim(series,dd,months=12,step=1):
    s=[];ret=[]
    for st_ in range(0,len(series)-months,step):
        e=1.0;a=True
        for k in range(st_,st_+months):
            e*=(1+series[k])
            if e<=1-dd: a=False;break
        s.append(a);ret.append(e-1 if a else -dd)
    return np.array(s),np.array(ret)

print()
print("="*92)
print("1) DER KERNVERGLEICH: gleiche Gesamtposition, anders verteilt")
print("="*92)
print(f"  {'Aufbau':>28s} {'Gesamt-Nominal':>15s} {'Puffer':>9s} {'Stopverl.':>10s} "
      f"{'% Puffer':>9s} {'ueberlebt':>10s} {'Ø $ Jahr':>11s}")
print("  "+"-"*84)
for label,N,L in [("1 Konto, 4x",1,4),("1 Konto, 8x",1,8),("1 Konto, 12x",1,12),
                  ("2 Konten je 4x",2,4),("3 Konten je 4x",3,4),
                  ("3 Konten je 6x",3,6)]:
    tot_notional=N*L
    puffer=N*PUFFER
    v=stopl*L                       # je Konto, in % dieses Kontos
    s,rr=sim(x*L,PUFFER)
    surv=s.mean()
    # bei N Konten: alle gleichzeitig betroffen -> Ueberleben identisch je Konto
    dollars=rr.mean()*100000*N
    print(f"  {label:>28s} {tot_notional:>14d}x {puffer*100:>8.0f}% {v*100:>9.2f}% "
          f"{v/PUFFER*100:>8.0f}% {surv*100:>9.1f}% {dollars:>10,.0f} $")

print("""
  -> Lies die vierte und fuenfte Spalte. Bei 3 Konten je 4x hast du
     DASSELBE Gesamt-Nominal wie bei 1 Konto mit 12x -- aber der
     Stopverlust misst sich gegen 6 % je Konto statt gegen 6 % insgesamt.
     Das ist der ganze Unterschied.""")

print()
print("="*92)
print("2) Was bei 1 Konto mit 12x passiert")
print("="*92)
for L in [4,8,12]:
    v=stopl*L
    s,rr=sim(x*L,PUFFER)
    flag="  KONTO WEG NACH EINEM STOPP" if v>=PUFFER else ""
    print(f"  {L:>2d}x Hebel: Stopverlust {v*100:>5.2f} % gegen {PUFFER*100:.0f} % Puffer "
          f"= {v/PUFFER*100:>3.0f} %   ueberlebt {s.mean()*100:>5.1f} %{flag}")

print()
print("="*92)
print("3) Der Haken: die Konten sind PERFEKT korreliert")
print("="*92)
s,rr=sim(x*4,PUFFER)
p1=s.mean()
print(f"""  Dieselbe Strategie auf N Konten heisst: ein schlechter Monat trifft
  ALLE gleichzeitig. Es gibt keine Diversifikation des Ereignisrisikos.

    P(ein Konto ueberlebt das Jahr)      {p1*100:.1f} %
    P(alle 3 ueberleben)                 {p1*100:.1f} %   <- identisch, nicht {p1**3*100:.1f} %
    P(mindestens 1 von 3 ueberlebt)      {p1*100:.1f} %   <- ebenfalls identisch

  Parallele Konten schuetzen NICHT vor dem Ereignis.
  Sie schuetzen vor der GROESSE. Das ist der Unterschied zwischen
  "ich habe 3x soviel Puffer" und "ich habe 3 unabhaengige Wetten".""")

print()
print("="*92)
print("4) Echte Diversifikation: die Verfallszyklen VERSETZEN")
print("="*92)
print("  Konto A startet Woche 1, Konto B Woche 2, Konto C Woche 3.")
print("  Damit ist nie das gesamte Kapital an einem Verfall exponiert.\n")
def condor_off(offset):
    """Wie condor(), aber der erste Zyklus startet um `offset` Tage versetzt."""
    dts=d.index; out=[]; i=offset; T0=21
    while i+T0<len(d):
        S=d.px.iloc[i]; atm=d.iv.iloc[i]/100; T=T0/252
        Kp,Kc=S*(1-X), S*(1+X); Lp,Lc=S*(1-X-W), S*(1+X+W)
        pr=lambda K,t: bsprice(S,K,T,iv_at(atm,np.log(K/S),0.7),t)
        credit=(pr(Kp,"p")+pr(Kc,"c"))-(pr(Lp,"p")+pr(Lc,"c"))-S*1.0/1e4*4
        ST=d.px.iloc[i+T0]; loss=0.0
        if ST<Kp: loss=min(Kp-ST,Kp-Lp)
        elif ST>Kc: loss=min(ST-Kc,Lc-Kc)
        pnl=(credit-loss)/S
        maxl=(W*S-credit)/S
        out.append(max(pnl,-STOP*maxl)); i+=T0
    return np.array(out)
legs=[condor_off(o) for o in (0,7,14)]
n=min(len(l) for l in legs)
sync=np.mean([l[:n] for l in legs],axis=0)          # gleiche Reihe 3x = identisch
stag=np.mean([legs[k][:n] for k in range(3)],axis=0) # versetzt
print(f"  {'':26s} {'Vol p.a.':>9s} {'Sharpe':>8s} {'schlecht. Zyklus':>18s}")
print("  "+"-"*64)
print(f"  {'1 Zyklus (synchron)':26s} {legs[0][:n].std()*np.sqrt(12)*100:>8.2f}% "
      f"{legs[0][:n].mean()/legs[0][:n].std()*np.sqrt(12):>8.2f} {legs[0][:n].min()*100:>17.2f}%")
print(f"  {'3 versetzte Zyklen':26s} {stag.std()*np.sqrt(12)*100:>8.2f}% "
      f"{stag.mean()/stag.std()*np.sqrt(12):>8.2f} {stag.min()*100:>17.2f}%")
print(f"""
  -> Versetzte Zyklen senken die Volatilitaet um
     {(1-stag.std()/legs[0][:n].std())*100:.0f} % und heben den Sharpe.
     DAS ist echte Diversifikation -- nicht die Anzahl der Konten,
     sondern die Streuung ueber die Verfallstermine.""")
