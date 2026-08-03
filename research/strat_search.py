"""Strategietest auf dem SUCHZEITRAUM: alter Standard vs. neue Parameter, Bounce vs Ausbruch."""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
full=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)
df=full[full.index < pd.Timestamp("2025-01-01",tz="UTC")].copy()
c=df["close"].to_numpy(); n=len(df)
ret=pd.Series(c,index=df.index).pct_change().fillna(0)
COST=16e-4

def series_from(events, hold, invert=False):
    pos=np.zeros(n)
    for (t,d,_,_) in events:
        dd = -d if invert else d
        pos[t:min(t+hold,n)] += dd
    return pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)

def challenge(w, lev):
    held=(w*lev).shift(1)
    s=held*ret - COST*held.diff().abs().fillna(0)
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

CONFIGS = {
    "alt  (8 / 0,5 / 1000)":  dict(width=8,  tol_atr=0.5, max_age=1000),
    "neu (12 / 0,5 / 2000)":  dict(width=12, tol_atr=0.5, max_age=2000),
}
print("="*90)
print("Suchzeitraum 2021-03 .. 2024-12 | Untergrenze = offene Versuche als gescheitert")
print("="*90)
print(f"{'Konfiguration':26s} {'Art':>9s} {'Halten':>7s} {'Groesse':>8s} {'Quote':>8s} {'Untergr.':>10s} {'Dauer':>8s}")
print("-"*90)
for nm, kw in CONFIGS.items():
    by = levels.build_levels(df, **kw)
    bo = levels.breakout_events(by, df, min_touch=6)
    bn = levels.bounce_events(by, df, min_touch=6, zone_atr=0.25)
    for art, ev in (("Ausbruch", bo), ("Bounce", bn)):
        for hold in (24, 48):
            w = series_from(ev, hold)
            for lev in (1.0, 0.5):
                q,u,cn,dur = challenge(w, lev)
                dtxt=f"{dur:.0f} T" if np.isfinite(dur) else "—"
                print(f"{nm:26s} {art:>9s} {hold:6d}h {lev:7.2f}x {q:7.1f}% {u:9.1f}% {dtxt:>8s}")
    # Bounce invertiert = an der Unterstuetzung SHORTEN
    w = series_from(bn, 48, invert=True)
    q,u,cn,dur = challenge(w, 0.5)
    print(f"{nm:26s} {'Bounce-inv':>9s} {48:6d}h {0.5:7.2f}x {q:7.1f}% {u:9.1f}% "
          f"{f'{dur:.0f} T' if np.isfinite(dur) else '—':>8s}")
