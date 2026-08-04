"""Heikin Ashi -- drei Anwendungen, sauber gegen echte Preise abgerechnet.

DIE FALLE: HA_close = (O+H+L+C)/4 ist kein handelbarer Preis. Signale duerfen
auf HA berechnet werden, der Fill MUSS zum echten Schlusskurs erfolgen.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=16e-4

def heikin_ashi(df):
    """HA-Kerzen. Rekursiv, aber ausschliesslich aus Vergangenheit + Gegenwart."""
    o,h,l,c = (df[x].to_numpy(float) for x in ("open","high","low","close"))
    n=len(df)
    ha_c=(o+h+l+c)/4.0
    ha_o=np.empty(n); ha_o[0]=(o[0]+c[0])/2.0
    for i in range(1,n):
        ha_o[i]=(ha_o[i-1]+ha_c[i-1])/2.0
    ha_h=np.maximum.reduce([h,ha_o,ha_c])
    ha_l=np.minimum.reduce([l,ha_o,ha_c])
    return pd.DataFrame({"open":ha_o,"high":ha_h,"low":ha_l,"close":ha_c,
                         "volume":df["volume"].to_numpy(float)}, index=df.index)

def challenge(s):
    d=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
    p=f=cn=0
    for st in range(0,len(d)-1):
        eq=1.0; done=None
        for i in range(st,min(st+365,len(d))):
            r=d[i]
            if r<-.03: done="f";break
            eq*=(1+r)
            if eq<=.94: done="f";break
            if eq-1>=.10: done="p";break
        if done=="p": p+=1
        elif done=="f": f+=1
        else: cn+=1
    tot=p+f+cn
    return p/tot*100 if tot else 0

def eff(ev, c, n, hz=24):
    seen={}
    for (t,d,_,_) in ev:
        b=t//hz
        if b not in seen and t+hz<n: seen[b]=(c[t+hz]/c[t]-1)*d
    a=np.array(list(seen.values()))*1e4
    if len(a)<15: return np.nan,np.nan
    _,p=stats.ttest_1samp(a,0); return a.mean(),p

def series(ev, df, hold, lev):
    c=df["close"].to_numpy(); n=len(df)
    ret=pd.Series(c,index=df.index).pct_change().fillna(0)
    pos=np.zeros(n)
    for (t,d,_,_) in ev: pos[t:min(t+hold,n)]+=d
    w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
    held=w.shift(1)
    return held*ret-COST*held.diff().abs().fillna(0)

def analyse(df, label):
    """df sind IMMER die echten Kerzen -- HA wird nur fuer Signale benutzt."""
    ha=heikin_ashi(df)
    c=df["close"].to_numpy(); n=len(df)
    print("="*88); print(label); print("="*88)
    print(f"{'Variante':38s} {'Ereign.':>8s} {'Effekt 24h':>12s} {'p':>7s} {'Pass 0,5x':>10s}")
    print("-"*88)

    # A) Referenz: Level auf ECHTEN Kerzen
    by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,df,min_touch=6)
    e,p=eff(ev,c,n)
    print(f"{'Referenz: Level auf echten Kerzen':38s} {len(ev):8d} {e:+9.1f} bp {p:7.3f} "
          f"{challenge(series(ev,df,48,0.5)):9.1f}%")

    # B) Level auf HA-Kerzen gebaut, Fill zum echten Schluss
    by_ha=levels.build_levels(ha,width=8,tol_atr=0.5,max_age=1000)
    ev_ha=levels.breakout_events(by_ha,ha,min_touch=6)
    e,p=eff(ev_ha,c,n)     # Ausgang mit ECHTEN Preisen gemessen
    print(f"{'Level auf HA-Kerzen':38s} {len(ev_ha):8d} {e:+9.1f} bp {p:7.3f} "
          f"{challenge(series(ev_ha,df,48,0.5)):9.1f}%")

    # C) HA-Richtung als Filter auf die echten Signale
    ha_up = (ha["close"] > ha["open"]).to_numpy()
    ev_f=[(t,d,tc,lv) for (t,d,tc,lv) in ev if (d>0)==ha_up[t]]
    e,p=eff(ev_f,c,n)
    print(f"{'echte Level + HA-Richtungsfilter':38s} {len(ev_f):8d} {e:+9.1f} bp {p:7.3f} "
          f"{challenge(series(ev_f,df,48,0.5)):9.1f}%")

    # D) klassische HA-Trendfolge (Farbwechsel), Fill echt
    flip=np.zeros(n,dtype=int)
    for i in range(1,n):
        if ha_up[i]!=ha_up[i-1]: flip[i]= 1 if ha_up[i] else -1
    ev_t=[(i,int(flip[i]),0,c[i]) for i in range(n) if flip[i]!=0]
    e,p=eff(ev_t,c,n)
    print(f"{'klassische HA-Trendfolge (Farbwechsel)':38s} {len(ev_t):8d} {e:+9.1f} bp {p:7.3f} "
          f"{challenge(series(ev_t,df,48,0.5)):9.1f}%")

    # E) Warnung: derselbe HA-Trade mit HA-PREISEN abgerechnet (falsch!)
    hc=ha["close"].to_numpy()
    seen={}
    for (t,d,_,_) in ev_t:
        b=t//24
        if b not in seen and t+24<n: seen[b]=(hc[t+24]/hc[t]-1)*d
    a=np.array(list(seen.values()))*1e4
    print(f"{'  ^ dasselbe, mit HA-Preisen gerechnet':38s} {len(ev_t):8d} {a.mean():+9.1f} bp "
          f"{'  (FALSCH)':>7s}")
    print()

for nm,fn in (("BTC (Suchzeitraum)","btc_1h.csv"),("ETH (gesamt)","eth_1h.csv"),
               ("SOL (frisch)","sol_1h.csv"),("XRP (frisch)","xrp_1h.csv")):
    d=pd.read_csv(V+fn,index_col=0,parse_dates=True)
    if nm.startswith("BTC"): d=d[d.index<pd.Timestamp("2025-01-01",tz="UTC")]
    analyse(d, nm)
