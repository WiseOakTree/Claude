"""Die entscheidende Kontrolle: Liegt es am LEVEL oder nur an der
vorangegangenen Abwaertsbewegung?

Gegen-Bounce-Short = Kurs faellt in eine Unterstuetzung, schliesst knapp
darueber, wir gehen SHORT. Das koennte einfach Abwaerts-Fortsetzung sein.
Kontrolle: Bars mit GLEICHER Vorbewegung, aber OHNE Level in der Naehe.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys
sys.path.insert(0,"/home/user/Claude/src")
from prop_backtester import levels as LV
D="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC"); COST=8e-4; H=48

def n_eff(st,hold,N):
    conc=np.zeros(N)
    for i in st: conc[i:i+hold]+=1
    u=[]
    for i in st:
        s=conc[i:i+hold]; s=s[s>0]; u.append((1.0/s).mean() if len(s) else 0)
    return max(np.sum(u),2.0)
def stat(ii,rets,N):
    x=np.asarray(rets); ne=n_eff(np.asarray(ii),H,N)
    return x.mean()*1e4, x.mean()/(x.std(ddof=1)/np.sqrt(ne)), len(x)

df=pd.read_csv(D+"btc_1h.csv",index_col=0,parse_dates=True)
by=LV.build_levels(df); c=df.close.to_numpy(); N=len(c)
f=np.full(N,np.nan); f[:-H]=c[H:]/c[:-H]-1
atr=LV.wilder_atr(df,14).to_numpy()
vor=np.full(N,np.nan); vor[12:]=(c[12:]-c[:-12])/atr[12:]      # Vorbewegung in ATR

ev=LV.bounce_events(by,df,min_touch=6)
# Unterstuetzungs-Bounces (d=+1) -> wir gehen SHORT
sup=[t for t,d,_,_ in ev if d==1 and np.isfinite(f[t]) and np.isfinite(vor[t])]
print("="*92)
print("A. GEGEN-BOUNCE-SHORT nach Unterstuetzungs-Bounce (der ganze Effekt)")
print("="*92)
for nm,sel in (("Suche 21-24",[t for t in sup if df.index[t]<SPLIT]),
               ("HOLDOUT 25-26",[t for t in sup if df.index[t]>=SPLIT])):
    bp,t_,n=stat(sel,[-f[t]-2*COST for t in sel],N)
    print(f"  {nm:<16}{n:>5} Signale{bp:>+9.1f} bp   t = {t_:>5.2f}   "
          f"Ø Vorbewegung {np.mean([vor[t] for t in sel]):+.2f} ATR")

print("\n"+"="*92)
print("B. KONTROLLE: Bars mit GLEICHER Vorbewegung, aber KEIN Level in der Naehe")
print("="*92)
# Level-Naehe je Bar bestimmen
nah=np.zeros(N,bool)
for t in range(N):
    for (price,kind,tou,_) in by.get(t,()):
        if tou>=6 and abs(c[t]-price)<0.5*atr[t]: nah[t]=True; break
print(f"  Bars mit einem >=6er-Level in Reichweite: {nah.mean()*100:.1f} %")
rng=np.random.default_rng(7)
for nm,sel in (("Suche 21-24",[t for t in sup if df.index[t]<SPLIT]),
               ("HOLDOUT 25-26",[t for t in sup if df.index[t]>=SPLIT])):
    lo,hi=np.percentile([vor[t] for t in sel],[10,90])
    zeit = (df.index<SPLIT) if nm.startswith("Suche") else (df.index>=SPLIT)
    kand=np.where(zeit & ~nah & np.isfinite(f) & np.isfinite(vor)
                  & (vor>=lo) & (vor<=hi))[0]
    bps=[]; ts=[]
    for _ in range(200):
        pick=rng.choice(kand,size=min(len(sel),len(kand)),replace=False)
        bp,t_,_=stat(pick,[-f[t]-2*COST for t in pick],N)
        bps.append(bp); ts.append(t_)
    echt_bp,echt_t,_=stat(sel,[-f[t]-2*COST for t in sel],N)
    print(f"  {nm:<16} echt {echt_bp:>+7.1f} bp (t {echt_t:.2f})   "
          f"Kontrolle Median {np.median(bps):>+7.1f} bp   "
          f"5-95 %: {np.percentile(bps,5):+.0f}..{np.percentile(bps,95):+.0f}   "
          f"p = {(np.array(bps)>=echt_bp).mean():.3f}")

print("\n"+"="*92)
print("C. UND DASSELBE OHNE LEVEL-BEDINGUNG: reine Abwaerts-Fortsetzung")
print("="*92)
for nm,zeit in (("Suche 21-24",df.index<SPLIT),("HOLDOUT 25-26",df.index>=SPLIT)):
    for lo_,hi_,lab in ((-99,-1.0,"Vorbewegung < -1 ATR"),(-1.0,-0.3,"-1 bis -0,3 ATR")):
        sel=np.where(zeit&np.isfinite(f)&np.isfinite(vor)&(vor>=lo_)&(vor<hi_))[0]
        if len(sel)<100: continue
        sel=rng.choice(sel,size=min(600,len(sel)),replace=False)
        bp,t_,n=stat(sel,[-f[t]-2*COST for t in sel],N)
        print(f"  {nm:<16}{lab:<24}{n:>5}{bp:>+9.1f} bp   t = {t_:>5.2f}")
