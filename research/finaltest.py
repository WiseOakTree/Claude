"""FINALER TEST -- White's Reality Check ueber 25 oeffentlich bekannte Regeln.

Frage: Kann ein privater Krypto-Trader mit oeffentlich bekannten Regeln einen
statistisch signifikanten Edge gegenueber einem fairen Zufallsprozess erzielen?

Aufbau nach docs/finaltest_spec.md -- vor der Rechnung festgelegt.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, sys, os, pickle
sys.path.insert(0,"/home/user/Claude/src")
from prop_backtester import levels as LV
V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=8e-4; H=48
MAERKTE=["btc","eth","sol","bnb","xrp","ada","atom","avax","bch",
         "doge","dot","link","ltc","trx"]

# ---------------------------------------------------------------- Indikatoren
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
def rsi(c,n=14):
    d=c.diff(); up=d.clip(lower=0); dn=(-d).clip(lower=0)
    return 100-100/(1+up.ewm(alpha=1/n,adjust=False).mean()/
                      dn.ewm(alpha=1/n,adjust=False).mean().replace(0,np.nan))
def atr(df,n=14):
    tr=pd.concat([df.high-df.low,(df.high-df.close.shift()).abs(),
                  (df.low-df.close.shift()).abs()],axis=1).max(axis=1)
    return tr.ewm(alpha=1/n,adjust=False).mean()
def stoch(df,k=14,d=3):
    ll=df.low.rolling(k).min(); hh=df.high.rolling(k).max()
    K=(100*(df.close-ll)/(hh-ll).replace(0,np.nan)).rolling(d).mean()
    return K,K.rolling(d).mean()
def kreuz(a,b): return (a>b)&(a.shift(1)<=b.shift(1))

def regeln(df, by=None):
    """Alle Regeln -> Serie mit +1 (long), -1 (short), 0 (nichts).
    KANONISCHE Parameter, keine Suche."""
    c,h,l,o,v=df.close,df.high,df.low,df.open,df.volume
    R={}
    ml=ema(c,12)-ema(c,26); ms=ema(ml,9)   # Signallinie auf die MACD-Linie, nicht auf den Preis
    R["MACD 12/26/9"]=np.where(kreuz(ml,ms),1,np.where(kreuz(ms,ml),-1,0))
    rs=rsi(c,14)
    R["RSI 14 (30/70)"]=np.where(kreuz(rs,pd.Series(30,index=c.index)),1,
                        np.where(kreuz(pd.Series(70,index=c.index),rs),-1,0))
    K,D=stoch(df)
    R["Stochastik 14/3/3"]=np.where(kreuz(K,D)&(K<20),1,
                           np.where(kreuz(D,K)&(K>80),-1,0))
    m20=c.rolling(20).mean(); sd=c.rolling(20).std()
    up,lo=m20+2*sd,m20-2*sd
    R["Bollinger-Rueckkehr"]=np.where((c<=lo)&(c.shift(1)>lo.shift(1)),1,
                             np.where((c>=up)&(c.shift(1)<up.shift(1)),-1,0))
    R["Bollinger-Ausbruch"]=np.where((c>=up)&(c.shift(1)<up.shift(1)),1,
                            np.where((c<=lo)&(c.shift(1)>lo.shift(1)),-1,0))
    s50,s200=c.rolling(50).mean(),c.rolling(200).mean()
    R["Goldenes Kreuz 50/200"]=np.where(kreuz(s50,s200),1,np.where(kreuz(s200,s50),-1,0))
    s20=c.rolling(20).mean()
    R["SMA-Kreuzung 20/50"]=np.where(kreuz(s20,s50),1,np.where(kreuz(s50,s20),-1,0))
    for n in (20,55):
        hh=h.rolling(n).max().shift(1); ll=l.rolling(n).min().shift(1)
        R[f"Donchian {n}"]=np.where(c>hh,1,np.where(c<ll,-1,0))
    a=atr(df,14)
    R["ATR-Ausbruch"]=np.where(c>h.shift(1)+a,1,np.where(c<l.shift(1)-a,-1,0))
    mom=c/c.shift(90)-1
    R["Momentum 90"]=np.where(kreuz(mom,pd.Series(0.0,index=c.index)),1,
                      np.where(kreuz(pd.Series(0.0,index=c.index),mom),-1,0))
    R["Momentum-Umkehr 90"]=-R["Momentum 90"]
    tp=(h+l+c)/3; tag=df.index.floor("1D")
    vw=(tp*v).groupby(tag).cumsum()/v.groupby(tag).cumsum()
    R["VWAP-Kreuzung"]=np.where(kreuz(c,vw),1,np.where(kreuz(vw,c),-1,0))
    md=(tp-tp.rolling(20).mean()).abs().rolling(20).mean()
    cci=(tp-tp.rolling(20).mean())/(0.015*md.replace(0,np.nan))
    R["CCI 20 (+-100)"]=np.where(kreuz(cci,pd.Series(-100.0,index=c.index)),1,
                        np.where(kreuz(pd.Series(100.0,index=c.index),cci),-1,0))
    hh14=h.rolling(14).max(); ll14=l.rolling(14).min()
    wr=-100*(hh14-c)/(hh14-ll14).replace(0,np.nan)
    R["Williams %R 14"]=np.where(kreuz(wr,pd.Series(-80.0,index=c.index)),1,
                        np.where(kreuz(pd.Series(-20.0,index=c.index),wr),-1,0))
    plus=(h.diff().clip(lower=0)).ewm(alpha=1/14,adjust=False).mean()
    minus=((-l.diff()).clip(lower=0)).ewm(alpha=1/14,adjust=False).mean()
    dx=100*(plus-minus).abs()/(plus+minus).replace(0,np.nan)
    adx=dx.ewm(alpha=1/14,adjust=False).mean()
    R["ADX>25 + SMA20"]=np.where((adx>25)&kreuz(c,s20),1,
                        np.where((adx>25)&kreuz(s20,c),-1,0))
    ten=(h.rolling(9).max()+l.rolling(9).min())/2
    kij=(h.rolling(26).max()+l.rolling(26).min())/2
    R["Ichimoku 9/26"]=np.where(kreuz(ten,kij),1,np.where(kreuz(kij,ten),-1,0))
    ar_up=h.rolling(25).apply(lambda x: x.argmax(),raw=True)
    ar_dn=l.rolling(25).apply(lambda x: x.argmin(),raw=True)
    R["Aroon 25"]=np.where(kreuz(ar_up,ar_dn),1,np.where(kreuz(ar_dn,ar_up),-1,0))
    mf=tp*v; pos=mf.where(tp>tp.shift(1),0).rolling(14).sum()
    neg=mf.where(tp<tp.shift(1),0).rolling(14).sum()
    mfi=100-100/(1+pos/neg.replace(0,np.nan))
    R["MFI 14 (20/80)"]=np.where(kreuz(mfi,pd.Series(20.0,index=c.index)),1,
                        np.where(kreuz(pd.Series(80.0,index=c.index),mfi),-1,0))
    obv=(np.sign(c.diff())*v).fillna(0).cumsum()
    R["OBV-Trend"]=np.where(kreuz(obv,obv.rolling(20).mean()),1,
                    np.where(kreuz(obv.rolling(20).mean(),obv),-1,0))
    ke=ema(c,20); ka=atr(df,10)
    R["Keltner-Ausbruch"]=np.where(c>ke+2*ka,1,np.where(c<ke-2*ka,-1,0))
    hac=(o+h+l+c)/4
    R["Heikin-Ashi-Wechsel"]=np.where(kreuz(hac,hac.shift(1)),1,
                             np.where(kreuz(hac.shift(1),hac),-1,0))
    out={k:pd.Series(np.asarray(x,dtype=float),index=c.index) for k,x in R.items()}
    if by is not None:
        d=np.zeros(len(c))
        for t,dirn,_,_ in LV.breakout_events(by,df,min_touch=6): d[t]=dirn
        out["S/R-Ausbruch (Projekt)"]=pd.Series(d,index=c.index)
        d2=np.zeros(len(c))
        for t,dirn,_,_ in LV.bounce_events(by,df,min_touch=6):
            if dirn==1: d2[t]=-1
        out["Gegen-Bounce (Projekt)"]=pd.Series(d2,index=c.index)
    return out

# --------------------------------------------------------------- Auswertung
CACHE="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/finaltest.pkl"
if os.path.exists(CACHE):
    daten=pickle.load(open(CACHE,"rb"))
else:
    daten={}
    for sym in MAERKTE:
        df=pd.read_csv(V+f"{sym}_1h.csv",index_col=0,parse_dates=True)
        by=LV.build_levels(df)
        c=df.close.to_numpy(); n=len(c)
        f=np.full(n,np.nan); f[:-H]=c[H:]/c[:-H]-1
        R=regeln(df,by)
        daten[sym]={"f":f,"n":n,"sig":{k:v.to_numpy() for k,v in R.items()}}
        print(f"  {sym.upper()}: {n:,} Bars, {len(R)} Regeln",flush=True)
    pickle.dump(daten,open(CACHE,"wb"))

NAMEN=sorted(next(iter(daten.values()))["sig"].keys())
def kennzahl(sig_pro_markt):
    """gepoolte mittlere Netto-Rendite je Trade, in bp"""
    ges=[]
    for sym,d in daten.items():
        s=sig_pro_markt[sym]; f=d["f"]
        m=(s!=0)&np.isfinite(f)
        if m.sum()==0: continue
        ges.append(s[m]*f[m]-2*COST)
    if not ges: return np.nan,0
    x=np.concatenate(ges); return x.mean()*1e4, len(x)

print("\n"+"="*92)
print("BEOBACHTET: 25 oeffentlich bekannte Regeln, 14 Maerkte, 16 bp Kosten")
print("="*92)
print(f"{'Regel':<28}{'Trades':>10}{'bp je Trade':>14}")
beob={}
for nm in NAMEN:
    bp,n=kennzahl({s:daten[s]["sig"][nm] for s in daten})
    beob[nm]=bp
    print(f"{nm:<28}{n:>10,}{bp:>+13.2f}")
best=max(v for v in beob.values() if np.isfinite(v))
bester=[k for k,v in beob.items() if v==best][0]
print(f"\n  BESTE REGEL: {bester}  mit {best:+.2f} bp je Trade")
pickle.dump({"beob":beob,"best":best,"bester":bester},
            open("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/ft_beob.pkl","wb"))

# ===================================================================
#  WHITE'S REALITY CHECK
# ===================================================================
print("\n"+"="*92)
print("REALITY CHECK: das Maximum der 25 Regeln gegen das Maximum von 25")
print("Zufallsregeln mit gleicher Anzahl, Haltedauer und Long/Short-Quote")
print("="*92)
rng=np.random.default_rng(20260808)
# Profil je Regel und Markt: Anzahl Signale und Long-Anteil
profil={}
for nm in NAMEN:
    profil[nm]={}
    for sym,d in daten.items():
        s=d["sig"][nm]; m=s!=0
        profil[nm][sym]=(int(m.sum()), float((s[m]>0).mean()) if m.sum() else 0.5)

def zufalls_kennzahl(nm):
    ges=[]
    for sym,d in daten.items():
        k,pl=profil[nm][sym]
        if k==0: continue
        f=d["f"]; n=d["n"]
        gueltig=np.where(np.isfinite(f))[0]
        if len(gueltig)<k: continue
        idx=rng.choice(gueltig,size=k,replace=False)
        richt=np.where(rng.random(k)<pl,1.0,-1.0)
        ges.append(richt*f[idx]-2*COST)
    if not ges: return np.nan
    return np.concatenate(ges).mean()*1e4

RUNDEN=2000
max_null=np.empty(RUNDEN)
einzel_null={nm:np.empty(RUNDEN) for nm in NAMEN}
for b in range(RUNDEN):
    werte={nm:zufalls_kennzahl(nm) for nm in NAMEN}
    for nm in NAMEN: einzel_null[nm][b]=werte[nm]
    max_null[b]=np.nanmax(list(werte.values()))
    if (b+1)%400==0: print(f"  {b+1} Runden",flush=True)

p_fw=float(np.mean(max_null>=best))
print(f"\n  beobachtetes Maximum:        {best:+.2f} bp  ({bester})")
print(f"  Zufalls-Maximum Median:      {np.median(max_null):+.2f} bp")
print(f"  Zufalls-Maximum 95. Perzentil:{np.percentile(max_null,95):+.2f} bp")
print(f"  Zufalls-Maximum Spanne:      {max_null.min():+.2f} .. {max_null.max():+.2f} bp")
print(f"\n  FAMILIENWEISER p-WERT:       {p_fw:.4f}")
print(f"  URTEIL: {'EDGE NACHGEWIESEN' if p_fw<0.05 else 'KEIN nachweisbarer Edge'}")

print("\n"+"="*92)
print("EINZELBEFUNDE (unkorrigiert) und Romano-Wolf-Schrittabstieg")
print("="*92)
print(f"{'Regel':<28}{'bp':>9}{'p einzeln':>12}{'p familienweise':>18}")
sortiert=sorted([n for n in NAMEN if np.isfinite(beob[n])],
                key=lambda n:-beob[n])
verbleibend=list(sortiert)
for nm in sortiert:
    p_e=float(np.mean(einzel_null[nm]>=beob[nm]))
    mx=np.nanmax(np.column_stack([einzel_null[k] for k in verbleibend]),axis=1)
    p_rw=float(np.mean(mx>=beob[nm]))
    print(f"{nm:<28}{beob[nm]:>+8.2f}{p_e:>12.4f}{p_rw:>18.4f}")
    if nm in verbleibend: verbleibend.remove(nm)
    if len(verbleibend)==0: break
