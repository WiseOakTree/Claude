"""Zwei Fragen:
 A) War 2k -> 100k -> 0 Pech, oder war es der Normalfall?
 B) Sind 20-30 % p.a. auf einem gefundeten 100k-Konto erreichbar?
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"

print("="*88)
print("A) War die Achterbahn Pech? Simulation eines gehebelten Muenzwurfs")
print("="*88)
print("   Start 2.000 $, taeglich gehandelt, Trefferquote knapp ueber 50 %,")
print("   Einsatz als Anteil des Kontos (so handelt man, wenn es laeuft).")
print()
rng=np.random.default_rng(42)
print(f"  {'Hebel':>7s} {'Einsatz/Tag':>12s} {'erreicht 100k':>14s} {'endet unter 1k':>15s} "
      f"{'BEIDES':>9s} {'Median Ende':>12s}")
print("  "+"-"*74)
N=20000; DAYS=400
for lev,frac in [(5,0.30),(10,0.30),(10,0.50),(20,0.50),(20,0.80)]:
    # taegliche Rendite: Muenzwurf mit 51 % Trefferquote, Amplitude = frac*lev*3%
    amp=frac*lev*0.03
    win=rng.random((N,DAYS))<0.51
    r=np.where(win,amp,-amp)
    eq=2000*np.cumprod(1+np.clip(r,-0.99,None),axis=1)
    peak=np.maximum.accumulate(eq,axis=1)
    hit100=(peak>=100000).any(axis=1)
    ende=eq[:,-1]
    ruin=(eq<1000).any(axis=1)
    both=hit100&ruin
    print(f"  {lev:>6d}x {frac*100:>11.0f}% {hit100.mean()*100:>13.1f}% "
          f"{ruin.mean()*100:>14.1f}% {both.mean()*100:>8.1f}% {np.median(ende):>11,.0f}$")
print()
print("  Lies die Spalte BEIDES: Wer 100k erreicht, verliert es fast immer wieder.")
print("  Das ist kein Pech und kein Fehler im Ausstieg -- es ist die Mathematik")
print("  eines gehebelten Prozesses mit winzigem Edge. Der Pfad MUSS so aussehen.")

print()
print("="*88)
print("B) 20-30 % p.a. auf einem gefundeten 100.000-$-Konto")
print("="*88)
print("   Regeln nach Funding: 6 % statischer Drawdown (Boden 94.000 $),")
print("   3 % Tagesverlust. 12-Monats-Fenster, alle Startpunkte.")
print()

def sr_daily(asset="btc", side_bp=8.0, hold=48):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=6)
    n=len(d); pos=np.zeros(n); busy=-1
    for (t,dr,_,_) in ev:
        if t<busy: continue
        pos[t:t+hold]=dr; busy=t+hold
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)
    held=w.shift(1)
    return ((1+(held*h-side_bp/1e4*held.diff().abs().fillna(0)).dropna()).resample("1D").prod()-1).dropna()

base=sr_daily()
print(f"  {'Groesse':>8s} {'Jahresvol':>10s} {'ueberlebt':>10s} {'Ø Rendite':>11s} "
      f"{'>=20 %':>8s} {'20-30 %':>9s} {'ueberlebt & >=20 %':>19s}")
print("  "+"-"*80)
d=base.to_numpy()
for lev in [0.25,0.35,0.50,0.75,1.00,1.50]:
    x=d*lev
    surv=[];rets=[]
    for st in range(0,len(x)-365):
        e=1.0; alive=True
        for i in range(st,st+365):
            if x[i]<-.03: alive=False;break
            e*=(1+x[i])
            if e<=.94: alive=False;break
        surv.append(alive); rets.append(e-1 if alive else -0.06)
    surv=np.array(surv); rets=np.array(rets)
    ok20=(surv)&(rets>=.20); ok2030=(surv)&(rets>=.20)&(rets<=.35)
    print(f"  {lev:>7.2f}x {x.std()*np.sqrt(365)*100:>9.1f}% {surv.mean()*100:>9.1f}% "
          f"{rets.mean()*100:>+10.1f}% {ok20.mean()*100:>7.1f}% {ok2030.mean()*100:>8.1f}% "
          f"{ok20.mean()*100:>18.1f}%")
print()
print("  'ueberlebt' = 12 Monate ohne 3-%-Tag und ohne Boden bei 94.000 $.")
print("  Bei Scheitern ist die Rendite als -6 % gewertet (Konto weg).")
