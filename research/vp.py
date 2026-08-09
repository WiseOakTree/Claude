"""Volume Profile gemessen: POC, Value Area, HVN/LVN.

Profil aus 1h-Bars: Volumen jedes Bars gleichmaessig ueber [low, high]
verteilt (dasselbe Verfahren, das TradingView ohne Tickdaten benutzt).
Rollierendes Fenster, alle 24 Bars neu berechnet.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")
COST=8e-4

def load(sym):
    return pd.read_csv(D+f"{sym}_1h.csv",index_col=0,parse_dates=True)

def profile(h,l,v,lo,hi,nb):
    """Volumen jedes Bars gleichmaessig ueber seine Spanne auf nb Koerbe."""
    edges=np.linspace(lo,hi,nb+1); prof=np.zeros(nb)
    w=(hi-lo)/nb
    for i in range(len(h)):
        a,b=h[i],l[i]
        if not (np.isfinite(a) and np.isfinite(b)): continue
        b0=int(np.clip((min(a,b)-lo)/w,0,nb-1)); b1=int(np.clip((max(a,b)-lo)/w,0,nb-1))
        prof[b0:b1+1]+=v[i]/(b1-b0+1)
    return prof,(edges[:-1]+edges[1:])/2

def value_area(prof,centers,frac=0.70):
    """Vom POC aus nach beiden Seiten wachsen, bis frac des Volumens drin ist."""
    k=int(np.argmax(prof)); tot=prof.sum(); acc=prof[k]; lo=hi=k
    while acc<frac*tot and (lo>0 or hi<len(prof)-1):
        left  = prof[lo-1] if lo>0 else -1
        right = prof[hi+1] if hi<len(prof)-1 else -1
        if right>=left: hi+=1; acc+=prof[hi]
        else:           lo-=1; acc+=prof[lo]
    return centers[k],centers[lo],centers[hi]

def build(sym,W=720,STEP=24,NB=100):
    df=load(sym)
    h=df.high.to_numpy(); l=df.low.to_numpy(); v=df.volume.to_numpy(); c=df.close.to_numpy()
    n=len(df)
    poc=np.full(n,np.nan); val=np.full(n,np.nan); vah=np.full(n,np.nan)
    dens=np.full(n,np.nan)      # Volumen im Korb des aktuellen Kurses, normiert
    for t in range(W,n,STEP):
        s=slice(t-W,t)
        lo,hi=np.nanmin(l[s]),np.nanmax(h[s])
        if not np.isfinite(lo) or hi<=lo: continue
        pr,ct=profile(h[s],l[s],v[s],lo,hi,NB)
        p,a,b=value_area(pr,ct)
        end=min(t+STEP,n)
        poc[t:end]=p; val[t:end]=a; vah[t:end]=b
        w=(hi-lo)/NB
        for u in range(t,end):
            if not np.isfinite(c[u]): continue
            k=int(np.clip((c[u]-lo)/w,0,NB-1))
            dens[u]=pr[k]/pr.mean() if pr.mean()>0 else np.nan
    out=pd.DataFrame({"close":df.close,"poc":poc,"val":val,"vah":vah,"dens":dens},
                     index=df.index)
    out["dist_poc"]=out.close/out.poc-1
    out["va_breite"]=(out.vah-out.val)/out.poc
    out["in_va"]=((out.close>=out.val)&(out.close<=out.vah)).astype(float)
    return out,df

def fwd(c,H):
    a=np.asarray(c); f=np.full(len(a),np.nan); f[:-H]=a[H:]/a[:-H]-1; return f

def tstat(r,H):
    ne=max(len(r)/H,2); return r.mean()/(r.std(ddof=1)/np.sqrt(ne))

H=48
print("="*88)
print("A. POC ALS MAGNET: zieht der Kurs zum Point of Control zurueck?")
print("="*88)
print(f"{'Markt':<6}{'Zeitraum':<16}{'weit UNTER POC':>16}{'weit UEBER POC':>16}{'Spanne':>9}{'t':>7}")
store={}
for sym in ("btc","eth","sol"):
    A,raw=build(sym); store[sym]=(A,raw)
    A["fwd"]=fwd(A.close,H)
    for nm,m in (("Suche 21-24",A.index<SPLIT),("HOLDOUT 25-26",A.index>=SPLIT)):
        g=A[m].dropna(subset=["dist_poc","fwd"])
        if len(g)<500: continue
        q=pd.qcut(g.dist_poc,5,labels=False,duplicates="drop")
        lo=g.fwd[q==0]; hi=g.fwd[q==4]
        r=np.concatenate([lo.to_numpy(),-hi.to_numpy()])-2*COST
        print(f"{sym.upper():<6}{nm:<16}{lo.mean()*100:>+15.2f}%{hi.mean()*100:>+15.2f}%"
              f"{(lo.mean()-hi.mean())*100:>+8.2f}{tstat(r,H):>7.2f}")
    print()
import pickle
pickle.dump({k:(v[0],) for k,v in store.items()},
            open("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/msb/vp.pkl","wb"))
