"""Ist GENAU die Signalklasse schlecht, die den Nutzer getroffen hat?

Nicht die ganze Rollenlogik aendern, sondern nur die Signale herausnehmen,
bei denen der Kurs kurz zuvor auf der anderen Seite des Levels war.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels
from prop_backtester.renko import wilder_atr

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
COST=16e-4; HZ=24

def analyse(df, label, lookback=24):
    c=df["close"].to_numpy(); n=len(df)
    atr=wilder_atr(df,14).to_numpy()
    ret=pd.Series(c,index=df.index).pct_change().fillna(0)
    by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,df,min_touch=6)
    tagged=[]
    for (t,d,tc,lvl) in ev:
        lo=max(0,t-lookback)
        frac_beyond = (c[lo:t] > lvl).mean() if d<0 else (c[lo:t] < lvl).mean()
        pen = abs(c[t]-lvl)/atr[t] if np.isfinite(atr[t]) and atr[t]>0 else np.nan
        # "von der falschen Seite": vor dem Signal ueberwiegend JENSEITS des Ziels
        wrong = frac_beyond < 0.5
        tagged.append((t,d,tc,lvl,wrong,pen))
    def eff(sub):
        seen={}
        for (t,d,_,_,_,_) in sub:
            b=t//HZ
            if b not in seen and t+HZ<n: seen[b]=(c[t+HZ]/c[t]-1)*d
        a=np.array(list(seen.values()))*1e4
        if len(a)<15: return np.nan,np.nan,len(a)
        _,p=stats.ttest_1samp(a,0); return a.mean(),p,len(a)
    def passr(sub, lev=0.5, hold=24):
        pos=np.zeros(n)
        for (t,d,_,_,_,_) in sub: pos[t:min(t+hold,n)]+=d
        w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
        held=w.shift(1); s=held*ret-COST*held.diff().abs().fillna(0)
        dd=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
        p=f=cn=0
        for st in range(0,len(dd)-1):
            eq=1.0; done=None
            for i in range(st,min(st+365,len(dd))):
                r=dd[i]
                if r<-.03: done="f";break
                eq*=(1+r)
                if eq<=.94: done="f";break
                if eq-1>=.10: done="p";break
            if done=="p": p+=1
            elif done=="f": f+=1
            else: cn+=1
        tot=p+f+cn
        return p/tot*100
    print("="*80); print(label); print("="*80)
    groups = {
        "alle Signale": tagged,
        "Kurs kam von der RICHTIGEN Seite": [x for x in tagged if not x[4]],
        "Kurs kam von der FALSCHEN Seite":  [x for x in tagged if x[4]],
    }
    print(f"  {'Gruppe':36s} {'n':>6s} {'Effekt':>11s} {'p':>7s} {'Pass':>8s}")
    print("  "+"-"*70)
    for nm,g in groups.items():
        e,p,ne=eff(g)
        pr=passr(g) if len(g)>20 else np.nan
        etxt=f"{e:+8.1f} bp" if np.isfinite(e) else "     —    "
        ptxt=f"{p:7.3f}" if np.isfinite(p) else "      —"
        prtxt=f"{pr:7.1f}%" if np.isfinite(pr) else "      —"
        print(f"  {nm:36s} {len(g):6d} {etxt} {ptxt} {prtxt}")
    return tagged

t1=analyse(full[full.index<pd.Timestamp("2025-01-01",tz="UTC")].copy(), "SUCHZEITRAUM 2021-03..2024-12")
print()
t2=analyse(full[full.index>=pd.Timestamp("2025-01-01",tz="UTC")].copy(), "HOLDOUT 2025-01..2026-06 (zweite Nutzung)")
