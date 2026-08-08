"""NACHGELAGERTE Diagnostik zum Gewinner des finalen Tests.

Wichtig: Das vorregistrierte Urteil steht (p = 0,0170). Diese Rechnungen
aendern es NICHT -- sie sagen nur, wie viel man darauf geben sollte.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, pickle, sys
sys.path.insert(0,"/home/user/Claude/src")
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=8e-4; H=48
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")
MAERKTE=["btc","eth","sol","bnb","xrp","ada","atom","avax","bch",
         "doge","dot","link","ltc","trx"]
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
def atr(df,n):
    tr=pd.concat([df.high-df.low,(df.high-df.close.shift()).abs(),
                  (df.low-df.close.shift()).abs()],axis=1).max(axis=1)
    return tr.ewm(alpha=1/n,adjust=False).mean()
def keltner(df,ne=20,mult=2.0,na=10):
    c=df.close; ke=ema(c,ne); ka=atr(df,na)
    return np.where(c>ke+mult*ka,1.0,np.where(c<ke-mult*ka,-1.0,0.0))
def n_eff(st,hold,N):
    conc=np.zeros(N)
    for i in st: conc[i:i+hold]+=1
    u=[]
    for i in st:
        s=conc[i:i+hold]; s=s[s>0]; u.append((1.0/s).mean() if len(s) else 0)
    return max(np.sum(u),2.0)

D={}
for sym in MAERKTE:
    df=pd.read_csv(V+f"{sym}_1h.csv",index_col=0,parse_dates=True)
    c=df.close.to_numpy(); n=len(c)
    f=np.full(n,np.nan); f[:-H]=c[H:]/c[:-H]-1
    D[sym]=(df,f,n)

print("="*88)
print("1. HAELT ES OUT-OF-SAMPLE? (Suche 2021-24 gegen Holdout 2025-26)")
print("="*88)
def bewerte(maske_zeit=None,ne=20,mult=2.0,na=10):
    ges=[];starts=[];Ns=[]
    for sym,(df,f,n) in D.items():
        s=keltner(df,ne,mult,na)
        m=(s!=0)&np.isfinite(f)
        if maske_zeit is not None:
            m=m&maske_zeit(df.index)
        if m.sum()==0: continue
        ges.append(s[m]*f[m]-2*COST)
        starts.append((np.where(m)[0],n))
    if not ges: return None
    x=np.concatenate(ges)
    ne_ges=sum(n_eff(st,H,N) for st,N in starts)
    t=x.mean()/(x.std(ddof=1)/np.sqrt(ne_ges))
    return x.mean()*1e4, t, len(x), ne_ges
for lab,mz in (("gesamt",None),
               ("Suche 2021-24",lambda i:(i<SPLIT).to_numpy()),
               ("HOLDOUT 2025-26",lambda i:(i>=SPLIT).to_numpy())):
    bp,t,n,nef=bewerte(mz)
    print(f"  {lab:<20}{n:>9,} Trades{bp:>+9.2f} bp   t = {t:>5.2f}   n_eff = {nef:,.0f}")

print("\n"+"="*88)
print("2. EINZELNE MAERKTE (gesamt)")
print("="*88)
print(f"  {'Markt':<8}{'Trades':>9}{'bp':>9}{'Suche':>10}{'HOLDOUT':>10}")
pos=0
for sym,(df,f,n) in D.items():
    s=keltner(df); m=(s!=0)&np.isfinite(f)
    x=s[m]*f[m]-2*COST
    tr=m&(df.index<SPLIT).to_numpy(); ho=m&(df.index>=SPLIT).to_numpy()
    a=(s[tr]*f[tr]-2*COST).mean()*1e4 if tr.sum() else np.nan
    b=(s[ho]*f[ho]-2*COST).mean()*1e4 if ho.sum() else np.nan
    pos+= x.mean()>0
    print(f"  {sym.upper():<8}{m.sum():>9,}{x.mean()*1e4:>+8.2f}{a:>+10.2f}{b:>+10.2f}")
print(f"\n  positiv in {pos} von {len(D)} Maerkten")

print("\n"+"="*88)
print("3. PARAMETEREMPFINDLICHKEIT (nachgelagert -- NICHT Teil des Tests)")
print("="*88)
print(f"  {'EMA':>5}{'Mult':>7}{'ATR':>6}{'Trades':>10}{'bp':>9}{'t':>8}")
for ne in (10,20,30):
    for mult in (1.5,2.0,2.5):
        for na in (10,20):
            r=bewerte(None,ne,mult,na)
            if r: print(f"  {ne:>5}{mult:>7.1f}{na:>6}{r[2]:>10,}{r[0]:>+8.2f}{r[1]:>8.2f}")

print("\n"+"="*88)
print("4. WAS BEDEUTET +6,08 bp WIRTSCHAFTLICH?")
print("="*88)
df,f,n=D["btc"]; s=keltner(df)
jahre=(df.index[-1]-df.index[0]).days/365.25
# echte Positionswechsel statt Signalzahl
pos_ser=pd.Series(s).replace(0,np.nan).ffill().fillna(0)
wechsel=(pos_ser.diff().abs()>0).sum()
print(f"  BTC: {int((s!=0).sum()):,} Signal-Bars, aber nur "
      f"{wechsel:,} echte Positionswechsel in {jahre:.1f} Jahren")
print(f"       = {wechsel/jahre:,.0f} Wechsel im Jahr")
print(f"  Bei +6,08 bp je gehaltener 48-h-Position und {wechsel/jahre:,.0f} Positionen:")
print(f"       rund {6.08e-4*wechsel/jahre*100:,.1f} % im Jahr bei 1x Nominal (brutto der Ueberlappung)")
