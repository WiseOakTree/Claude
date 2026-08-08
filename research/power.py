"""Ist meine Methodik zu streng? Der einzige ehrliche Test: einen BEKANNTEN
Edge in echte Daten einbauen und schauen, ob die Pipeline ihn findet.

Wenn sie einen echten Edge von realistischer Groesse uebersieht, sind alle
Negativbefunde dieses Projekts wertlos.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h
COST=8e-4; H=30       # 5 Tage auf 4h-Bars
rng=np.random.default_rng(20260808)

btc=bars4h("btc"); c=btc.close.to_numpy()
r=np.diff(np.log(c))
n=len(r)
print(f"Grundlage: {n:,} echte 4h-Renditen, Vol {r.std()*np.sqrt(6*365)*100:.0f} % p.a.\n")

def pipeline(sig, ret, cost=COST, hold=H):
    """GENAU die Auswertung, die ich im ganzen Projekt benutzt habe:
    Signal -> Halten -> Kosten -> Ueberlappungskorrektur -> t."""
    m=sig!=0
    if m.sum()<20: return None
    fwd=np.full(len(ret),np.nan)
    cum=np.cumsum(ret)
    fwd[:-hold]=cum[hold:]-cum[:-hold]
    ok=m&np.isfinite(fwd)
    x=sig[ok]*fwd[ok]-2*cost
    ne=max(ok.sum()/hold,2)
    return dict(n=int(ok.sum()), bp=x.mean()*1e4,
                t=x.mean()/(x.std(ddof=1)/np.sqrt(ne)))

print("="*88)
print("A. ERKENNUNGSRATE: Signal mit eingebautem Edge, 200 Wiederholungen")
print("="*88)
print(f"{'wahrer Edge':>12}{'Signale/Jahr':>14}{'gemessen':>11}{'Ø t':>8}"
      f"{'t>2':>8}{'t>1,5':>8}{'bp>0':>8}")
jahre=n/(6*365)
for edge_bp in (0,10,20,30,50,80,120,200):
    for freq in (40,):
        tt=[]; bb=[]
        for _ in range(200):
            k=int(freq*jahre)
            idx=rng.choice(n-H, size=k, replace=False)
            s=np.zeros(n); s[idx]=rng.choice([1,-1],size=k)
            rr=r.copy()
            # Edge einbauen: nach jedem Signal in Signalrichtung verteilt
            for i in idx:
                rr[i:i+H]+=s[i]*edge_bp/1e4/H
            out=pipeline(s,rr)
            tt.append(out["t"]); bb.append(out["bp"])
        tt=np.array(tt); bb=np.array(bb)
        print(f"{edge_bp:>10} bp{freq:>14}{np.mean(bb):>+10.1f}{np.mean(tt):>8.2f}"
              f"{(tt>2).mean()*100:>7.0f}%{(tt>1.5).mean()*100:>7.0f}%{(bb>0).mean()*100:>7.0f}%")

print("\n"+"="*88)
print("B. Wie viele Signale braucht man, um 30 bp nachzuweisen?")
print("="*88)
print(f"{'Signale/Jahr':>14}{'Jahre':>8}{'n gesamt':>11}{'Ø t':>8}{'Anteil t>2':>12}")
for freq in (20,40,100,250,500,1000):
    tt=[]
    for _ in range(150):
        k=int(freq*jahre)
        if k>n-H: continue
        idx=rng.choice(n-H,size=k,replace=False)
        s=np.zeros(n); s[idx]=rng.choice([1,-1],size=k)
        rr=r.copy()
        for i in idx: rr[i:i+H]+=s[i]*30/1e4/H
        o=pipeline(s,rr)
        if o: tt.append(o["t"])
    tt=np.array(tt)
    print(f"{freq:>14}{jahre:>8.1f}{int(freq*jahre):>11}{tt.mean():>8.2f}{(tt>2).mean()*100:>11.0f}%")

print("\n"+"="*88)
print("C. Wie stark bremst die Ueberlappungskorrektur? (30 bp Edge, 40 Signale/J)")
print("="*88)
tt_korr=[]; tt_ohne=[]
for _ in range(200):
    k=int(40*jahre); idx=rng.choice(n-H,size=k,replace=False)
    s=np.zeros(n); s[idx]=rng.choice([1,-1],size=k)
    rr=r.copy()
    for i in idx: rr[i:i+H]+=s[i]*30/1e4/H
    m=s!=0; cum=np.cumsum(rr); fwd=np.full(n,np.nan); fwd[:-H]=cum[H:]-cum[:-H]
    ok=m&np.isfinite(fwd); x=s[ok]*fwd[ok]-2*COST
    tt_korr.append(x.mean()/(x.std(ddof=1)/np.sqrt(max(ok.sum()/H,2))))
    tt_ohne.append(x.mean()/(x.std(ddof=1)/np.sqrt(ok.sum())))
print(f"  MIT Ueberlappungskorrektur (was ich benutze): Ø t = {np.mean(tt_korr):.2f}   "
      f"t>2 in {np.mean(np.array(tt_korr)>2)*100:.0f} % der Faelle")
print(f"  OHNE Korrektur (naiv):                        Ø t = {np.mean(tt_ohne):.2f}   "
      f"t>2 in {np.mean(np.array(tt_ohne)>2)*100:.0f} % der Faelle")
print(f"  Faktor: {np.mean(tt_ohne)/np.mean(tt_korr):.2f}x")
