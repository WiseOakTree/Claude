"""Wie weit kommt man mit NULL Edge?

Drei Ebenen:
 1) Theoretisch: Zufallsprozess ohne Drift, ohne Kosten. Ruin-Problem mit
    zusaetzlicher Tagesverlustschranke. Volatilitaet durchgesweept.
 2) Empirisch: BTC einfach halten, Positionsgroesse durchgesweept.
    (Kosten fallen EINMAL an, nicht je Roundtrip -- das ist der Trick.)
 3) Zufallseinstiege mit gleicher Handelsfrequenz wie S/R -- kostet echtes Geld.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

TGT, DD, DAY = .10, .06, .03
rng = np.random.default_rng(7)

def sim_gbm(vol_ann, drift_ann=0.0, n=40000, maxd=365):
    """Taegliche Renditen, Normal. Gibt Pass-Rate und Anteil je Abbruchgrund."""
    sd = vol_ann/np.sqrt(365); mu = drift_ann/365
    r = rng.normal(mu, sd, size=(n, maxd))
    eq = np.ones(n); done = np.zeros(n, dtype=int)   # 0 offen 1 pass 2 dd 3 tag
    for i in range(maxd):
        live = done==0
        if not live.any(): break
        x = r[:,i]
        hit_day = live & (x < -DAY)
        done[hit_day] = 3
        live = done==0
        eq[live] *= (1+x[live])
        done[live & (eq <= 1-DD)] = 2
        live = done==0
        done[live & (eq >= 1+TGT)] = 1
    return (done==1).mean()*100, (done==2).mean()*100, (done==3).mean()*100, (done==0).mean()*100

print("="*86)
print("1) OBERGRENZE FUER REINEN ZUFALL -- kein Drift, keine Kosten, 365 Tage")
print("="*86)
print(f"  {'Jahresvol':>10s} {'BESTANDEN':>11s} {'am DD':>8s} {'am Tageslimit':>15s} {'offen':>8s}")
print("  "+"-"*58)
best=(0,None)
for v in [.05,.10,.15,.20,.25,.30,.40,.50,.70,1.00]:
    p,d,t,o = sim_gbm(v)
    if p>best[0]: best=(p,v)
    print(f"  {v*100:>9.0f}% {p:>10.1f}% {d:>7.1f}% {t:>14.1f}% {o:>7.1f}%")
print(f"\n  -> Optimum bei {best[1]*100:.0f}% Jahresvol: {best[0]:.1f}%")
print("     Ohne Tageslimit waere die Ruin-Schranke 6/(6+10) = 37,5 %.")

print()
print("="*86)
print("2) EMPIRISCH: BTC EINFACH HALTEN -- Positionsgroesse durchgesweept")
print("="*86)
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
d=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
dret=((1+h).resample("1D").prod()-1).dropna().to_numpy()

def passrate(dd, lev, cost=16e-4, cap=365):
    """cost faellt EINMAL beim Einstieg an."""
    p=f=c=0
    for st in range(0,len(dd)-30):
        e=1.0-cost*lev; done=None
        for i in range(st,min(st+cap,len(dd))):
            x=dd[i]*lev
            if x<-DAY: done="f";break
            e*=(1+x)
            if e<=1-DD: done="f";break
            if e>=1+TGT: done="p";break
        if done=="p":p+=1
        elif done=="f":f+=1
        else:c+=1
    t=p+f+c
    return p/t*100, c/t*100

print(f"  {'Groesse':>8s} {'Jahresvol':>10s} {'BESTANDEN':>11s} {'unaufgeloest':>13s}")
print("  "+"-"*46)
volb=dret.std()*np.sqrt(365)*100
bh=(0,None)
for lev in [0.15,0.25,0.35,0.50,0.70,1.00,1.30]:
    p,c=passrate(dret,lev)
    if p>bh[0]: bh=(p,lev)
    print(f"  {lev:>7.2f}x {volb*lev:>9.0f}% {p:>10.1f}% {c:>12.1f}%")
print(f"\n  -> Bestes Halten: {bh[1]:.2f}x mit {bh[0]:.1f}%")

print()
print("="*86)
print("3) ZUFALLSEINSTIEGE -- gleiche Frequenz wie S/R, aber Muenzwurf-Richtung")
print("="*86)
c_=d["close"].to_numpy(); n=len(d)
print(f"  {'Groesse':>8s} {'BESTANDEN (Median ueber 40 Ziehungen)':>38s}")
print("  "+"-"*48)
for lev in [0.5,1.0]:
    outs=[]
    for seed in range(40):
        rg=np.random.default_rng(seed)
        pos=np.zeros(n)
        for t in rg.choice(np.arange(50,n-50), size=775, replace=False):
            pos[t:t+48] += rg.choice([-1,1])
        w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)*lev
        held=w.shift(1); s=held*h-16e-4*held.diff().abs().fillna(0)
        dd2=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
        outs.append(passrate(dd2,1.0,cost=0.0)[0])
    print(f"  {lev:>7.2f}x {np.median(outs):>37.1f}%")
