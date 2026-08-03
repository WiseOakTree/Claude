"""HOLDOUT -- 2025-01 bis 2026-06. Wird genau einmal ausgefuehrt.

Vorab festgelegt (aus dem Suchzeitraum, ohne Blick auf diese Daten):
  Parameter  8 / 0,5 / 1000, >=6 Beruehrungen   (Suchlauf hat nichts Besseres gefunden)
  Richtung   Ausbruch                            (Bounce war systematisch negativ)
  Halten     24 h, kein Stop                     (Stops halfen der Pass-Rate nicht)
  Groesse    1,0x primaer; 0,5x als Nachpruefung der frueher veroeffentlichten Zahl
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")
COST=16e-4

def evaluate(df, label):
    c=df["close"].to_numpy(); n=len(df)
    ret=pd.Series(c,index=df.index).pct_change().fillna(0)
    by=levels.build_levels(df, width=8, tol_atr=0.5, max_age=1000)
    bo=levels.breakout_events(by, df, min_touch=6)
    bn=levels.bounce_events(by, df, min_touch=6, zone_atr=0.25)
    def eff(ev, hz=24):
        seen={}
        for (t,d,_,_) in ev:
            b=t//hz
            if b not in seen and t+hz<n: seen[b]=(c[t+hz]/c[t]-1)*d
        a=np.array(list(seen.values()))*1e4
        if len(a)<15: return len(ev), np.nan, np.nan
        _,p=stats.ttest_1samp(a,0)
        return len(ev), a.mean(), p
    def series(ev, hold, lev):
        pos=np.zeros(n)
        for (t,d,_,_) in ev: pos[t:min(t+hold,n)]+=d
        w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
        held=w.shift(1)
        return held*ret - COST*held.diff().abs().fillna(0)
    def challenge(s):
        d=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
        p=f=cn=0; dur=[]
        for st in range(0,len(d)-1):
            eq=1.0; done=None
            for i in range(st,min(st+365,len(d))):
                r=d[i]
                if r<-.03: done="f";break
                eq*=(1+r)
                if eq<=.94: done="f";break
                if eq-1>=.10: done="p";dur.append(i-st+1);break
            if done=="p": p+=1
            elif done=="f": f+=1
            else: cn+=1
        tot=p+f+cn
        return (p/(p+f)*100 if p+f else 0, p/tot*100, cn/tot*100,
                np.median(dur) if dur else np.nan)
    print("="*84)
    print(f"{label}   ({df.index.min().date()} .. {df.index.max().date()}, {n} Bars)")
    print("="*84)
    for nm, ev in (("Ausbruch", bo), ("Bounce", bn)):
        cnt, e, p = eff(ev)
        etxt = f"{e:+.1f} bp (p={p:.3f})" if np.isfinite(e) else "zu wenige"
        print(f"  {nm:9s}: {cnt:4d} Ereignisse, Effekt 24h {etxt}")
    print(f"\n  {'Variante':28s} {'Quote':>8s} {'Untergr.':>10s} {'offen':>8s} {'Dauer':>8s}")
    print("  "+"-"*66)
    for nm, ev, hold, lev in (("Ausbruch 24h, 1,0x", bo,24,1.0),
                              ("Ausbruch 24h, 0,5x", bo,24,0.5),
                              ("Ausbruch 48h, 0,5x", bo,48,0.5),
                              ("Bounce   24h, 1,0x", bn,24,1.0)):
        q,u,cn,dur = challenge(series(ev,hold,lev))
        dtxt=f"{dur:.0f} T" if np.isfinite(dur) else "—"
        print(f"  {nm:28s} {q:7.1f}% {u:9.1f}% {cn:7.1f}% {dtxt:>8s}")
    print()

evaluate(full[full.index<SPLIT].copy(),  "SUCHZEITRAUM (bekannt, hier optimiert)")
evaluate(full[full.index>=SPLIT].copy(), "HOLDOUT (bisher unangetastet)")
