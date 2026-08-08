"""Die Ueberlappungskorrektur war falsch angewandt.

n_eff = n / Haltedauer stimmt nur, wenn auf JEDEM Bar ein Signal feuert.
Bei 40 Signalen im Jahr mit 5 Tagen Halten ueberlappen die Trades fast nie
-- trotzdem habe ich durch 30 geteilt. Das ist ein Faktor 5,5 zu streng.

Richtig: effektive Stichprobe = Summe der 'Einzigartigkeit' jedes Trades
(Lopez de Prado). Ein Trade, der sich mit k anderen ueberlappt, zaehlt 1/k.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb")
from msb import bars4h
COST=8e-4; H=30
rng=np.random.default_rng(4711)
btc=bars4h("btc"); r=np.diff(np.log(btc.close.to_numpy())); n=len(r)
jahre=n/(6*365)

def n_eff_uniq(idx, hold, N):
    """Wie viele Trades laufen zu jedem Zeitpunkt gleichzeitig?"""
    conc=np.zeros(N)
    for i in idx: conc[i:i+hold]+=1
    u=[]
    for i in idx:
        seg=conc[i:i+hold]
        seg=seg[seg>0]
        u.append((1.0/seg).mean() if len(seg) else 0.0)
    return max(np.sum(u),2.0)

def t_alt(sig,ret,hold=H):
    """ALT: n_eff = n / Haltedauer"""
    m=np.where(sig!=0)[0]; cum=np.cumsum(ret)
    f=np.full(len(ret),np.nan); f[:-hold]=cum[hold:]-cum[:-hold]
    ok=m[np.isfinite(f[m])]; x=sig[ok]*f[ok]-2*COST
    return x.mean()/(x.std(ddof=1)/np.sqrt(max(len(ok)/hold,2))), x.mean()*1e4, len(ok)

def t_neu(sig,ret,hold=H):
    """NEU: n_eff = Summe der Einzigartigkeit"""
    m=np.where(sig!=0)[0]; cum=np.cumsum(ret)
    f=np.full(len(ret),np.nan); f[:-hold]=cum[hold:]-cum[:-hold]
    ok=m[np.isfinite(f[m])]; x=sig[ok]*f[ok]-2*COST
    ne=n_eff_uniq(ok,hold,len(ret))
    return x.mean()/(x.std(ddof=1)/np.sqrt(ne)), ne

print("="*94)
print("A. FALSCHALARM-KONTROLLE: Edge = 0. Die neue Korrektur darf nicht mehr")
print("   als ~5 % Falschalarme liefern, sonst ist sie zu lasch.")
print("="*94)
print(f"{'Signale/Jahr':>13}{'ALT: t>2':>12}{'NEU: t>2':>12}{'NEU: |t|>2':>13}{'Ø n_eff':>10}{'n':>7}")
for freq in (40,100,250,1000):
    ta=[];tn=[];nes=[]
    for _ in range(300):
        k=int(freq*jahre); idx=rng.choice(n-H,size=k,replace=False)
        s=np.zeros(n); s[idx]=rng.choice([1,-1],size=k)
        a,_,nn=t_alt(s,r); b,ne=t_neu(s,r)
        ta.append(a); tn.append(b); nes.append(ne)
    ta=np.array(ta); tn=np.array(tn)
    print(f"{freq:>13}{(ta>2).mean()*100:>11.1f}%{(tn>2).mean()*100:>11.1f}%"
          f"{(np.abs(tn)>2).mean()*100:>12.1f}%{np.mean(nes):>10.0f}{int(freq*jahre):>7}")

print("\n"+"="*94)
print("B. ERKENNUNGSRATE mit korrigierter Statistik (40 Signale/Jahr, 5 Tage)")
print("="*94)
print(f"{'wahrer Edge':>12}{'gemessen':>11}{'ALT Ø t':>10}{'ALT t>2':>10}"
      f"{'NEU Ø t':>10}{'NEU t>2':>10}")
for edge in (0,10,20,30,50,80,120,200):
    ta=[];tn=[];bb=[]
    for _ in range(300):
        k=int(40*jahre); idx=rng.choice(n-H,size=k,replace=False)
        s=np.zeros(n); s[idx]=rng.choice([1,-1],size=k)
        rr=r.copy()
        for i in idx: rr[i:i+H]+=s[i]*edge/1e4/H
        a,bp,_=t_alt(s,rr); b,_=t_neu(s,rr)
        ta.append(a); tn.append(b); bb.append(bp)
    ta=np.array(ta); tn=np.array(tn)
    print(f"{edge:>10} bp{np.mean(bb):>+10.1f}{np.mean(ta):>10.2f}{(ta>2).mean()*100:>9.0f}%"
          f"{np.mean(tn):>10.2f}{(tn>2).mean()*100:>9.0f}%")

print("\n"+"="*94)
print("C. Ab welcher Edge-Groesse findet die korrigierte Pipeline zuverlaessig?")
print("="*94)
print(f"{'Signale/Jahr':>13}{'Edge fuer 50 % Trefferquote':>30}{'Edge fuer 80 %':>18}")
for freq in (40,100,250,500):
    res={}
    for edge in (20,30,50,80,120,200,300,500):
        tn=[]
        for _ in range(150):
            k=int(freq*jahre)
            if k>n-H: continue
            idx=rng.choice(n-H,size=k,replace=False)
            s=np.zeros(n); s[idx]=rng.choice([1,-1],size=k)
            rr=r.copy()
            for i in idx: rr[i:i+H]+=s[i]*edge/1e4/H
            b,_=t_neu(s,rr); tn.append(b)
        res[edge]=(np.array(tn)>2).mean()
    def schwelle(p):
        for e,v in sorted(res.items()):
            if v>=p: return f"{e} bp"
        return "> 500 bp"
    print(f"{freq:>13}{schwelle(0.5):>30}{schwelle(0.8):>18}")
