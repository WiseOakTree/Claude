"""Teil 4: Ist der SOL-Befund systematisch? Value-Area-Ausbruch auf 14 Maerkten.

Sauber als Mehrfachtest behandelt: Verteilung ueber alle Maerkte, gepoolter
Effekt, und Vergleich gegen das, was Zufall liefern wuerde.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, os

D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4; H=48
W,STEP,NB=720,24,100

def profile_fast(h,l,v,lo,hi,nb):
    """Differenzarray statt Schleife -- gleiches Ergebnis, ~50x schneller."""
    w=(hi-lo)/nb
    b0=np.clip(((np.minimum(h,l)-lo)/w).astype(int),0,nb-1)
    b1=np.clip(((np.maximum(h,l)-lo)/w).astype(int),0,nb-1)
    share=v/(b1-b0+1)
    diff=np.zeros(nb+1)
    np.add.at(diff,b0, share)
    np.add.at(diff,b1+1,-share)
    prof=np.cumsum(diff)[:nb]
    return prof,(np.linspace(lo,hi,nb+1)[:-1]+np.linspace(lo,hi,nb+1)[1:])/2

def value_area(prof,centers,frac=0.70):
    k=int(np.argmax(prof)); tot=prof.sum(); acc=prof[k]; lo=hi=k
    while acc<frac*tot and (lo>0 or hi<len(prof)-1):
        left  = prof[lo-1] if lo>0 else -1
        right = prof[hi+1] if hi<len(prof)-1 else -1
        if right>=left: hi+=1; acc+=prof[hi]
        else:           lo-=1; acc+=prof[lo]
    return centers[k],centers[lo],centers[hi]

def va_breakout(sym):
    df=pd.read_csv(D+f"{sym}_1h.csv",index_col=0,parse_dates=True)
    h=df.high.to_numpy(); l=df.low.to_numpy(); v=df.volume.to_numpy(); c=df.close.to_numpy()
    n=len(df)
    if n<W+500: return None
    val=np.full(n,np.nan); vah=np.full(n,np.nan)
    for t in range(W,n,STEP):
        s=slice(t-W,t)
        lo,hi=np.nanmin(l[s]),np.nanmax(h[s])
        if not np.isfinite(lo) or hi<=lo: continue
        pr,ct=profile_fast(h[s],l[s],v[s],lo,hi,NB)
        if pr.sum()<=0: continue
        _,a,b=value_area(pr,ct)
        e=min(t+STEP,n); val[t:e]=a; vah[t:e]=b
    f=np.full(n,np.nan); f[:-H]=c[H:]/c[:-H]-1
    up=np.r_[False, (c[1:]>vah[1:])&(c[:-1]<=vah[:-1])]
    dn=np.r_[False, (c[1:]<val[1:])&(c[:-1]>=val[:-1])]
    d=np.where(up,1,np.where(dn,-1,0))
    m=(d!=0)&np.isfinite(f)
    return pd.DataFrame({"ts":df.index[m],"ret":d[m]*f[m]-2*COST})

SYMS=["btc","eth","sol","ada","atom","avax","bch","bnb","doge","dot","link","ltc","trx","xrp"]
rows=[]; pool_tr=[]; pool_ho=[]
print("="*92)
print("VALUE-AREA-AUSBRUCH AUF 14 MAERKTEN (1h, 48 h halten, nach Kosten)")
print("="*92)
print(f"{'Markt':<7}{'n Suche':>9}{'bp Suche':>11}{'t':>7}{'   |':>4}{'n HOLD':>8}{'bp HOLDOUT':>12}{'t':>7}{'  beide +':>10}")
for s in SYMS:
    try: E=va_breakout(s)
    except Exception as ex: print(f"{s.upper():<7}  Fehler: {ex}"); continue
    if E is None or len(E)<100: continue
    a=E[E.ts<SPLIT].ret; b=E[E.ts>=SPLIT].ret
    if len(a)<50 or len(b)<50: continue
    ta_=a.mean()/(a.std(ddof=1)/np.sqrt(max(len(a)/H,2)))
    tb_=b.mean()/(b.std(ddof=1)/np.sqrt(max(len(b)/H,2)))
    both = a.mean()>0 and b.mean()>0
    pool_tr.append(a); pool_ho.append(b)
    rows.append(dict(sym=s,na=len(a),ba=a.mean()*1e4,ta=ta_,nb=len(b),bb=b.mean()*1e4,tb=tb_,both=both))
    print(f"{s.upper():<7}{len(a):>9}{a.mean()*1e4:>+10.1f}{ta_:>7.2f}{'   |':>4}"
          f"{len(b):>8}{b.mean()*1e4:>+11.1f}{tb_:>7.2f}{('   JA' if both else '   -'):>10}")

R=pd.DataFrame(rows)
PT=pd.concat(pool_tr); PH=pd.concat(pool_ho)
tp=PT.mean()/(PT.std(ddof=1)/np.sqrt(max(len(PT)/H,2)))
th=PH.mean()/(PH.std(ddof=1)/np.sqrt(max(len(PH)/H,2)))
print("\n"+"="*92)
print("GEPOOLT UEBER ALLE MAERKTE -- der eigentliche Test")
print("="*92)
print(f"  Suchzeitraum 2021-24 : {len(PT):>6} Trades   {PT.mean()*1e4:>+7.1f} bp   t = {tp:>5.2f}")
print(f"  HOLDOUT 2025-26      : {len(PH):>6} Trades   {PH.mean()*1e4:>+7.1f} bp   t = {th:>5.2f}")
print(f"\n  Maerkte gesamt                 : {len(R)}")
print(f"  positiv im Suchzeitraum        : {(R.ba>0).sum()} ({(R.ba>0).mean()*100:.0f} %)")
print(f"  positiv im Holdout             : {(R.bb>0).sum()} ({(R.bb>0).mean()*100:.0f} %)")
print(f"  in BEIDEN positiv              : {R.both.sum()}")
print(f"  bei Zufall erwartet (25 %)     : {len(R)*0.25:.1f}")
from scipy.stats import binomtest
print(f"  p (Binomialtest gegen 25 %)    : {binomtest(int(R.both.sum()),len(R),0.25,'greater').pvalue:.3f}")
print(f"\n  Korrelation Suche <-> Holdout je Markt: {R.ba.corr(R.bb):+.3f}")
print(f"  (positiv = wer damals gut war, ist es weiter; ~0 = Zufall)")
R.to_csv("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb/va14.csv",index=False)
