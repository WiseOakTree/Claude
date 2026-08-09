"""Unabhaengige Validierung auf ETH -- ein nie verwendetes Asset."""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
COST=16e-4; HZ=24

def run(path, label):
    df=pd.read_csv(path,index_col=0,parse_dates=True)
    c=df["close"].to_numpy(); n=len(df)
    ret=pd.Series(c,index=df.index).pct_change().fillna(0)
    by=levels.build_levels(df,width=8,tol_atr=0.5,max_age=1000)
    print("="*76); print(f"{label}   ({df.index.min().date()} .. {df.index.max().date()})")
    print("="*76)
    for mt in (4,6,8):
        ev=levels.breakout_events(by,df,min_touch=mt)
        seen={}
        for (t,d,_,_) in ev:
            b=t//HZ
            if b not in seen and t+HZ<n: seen[b]=(c[t+HZ]/c[t]-1)*d
        a=np.array(list(seen.values()))*1e4
        if len(a)<15:
            print(f"  >={mt} Ber.: {len(ev):4d} Ereignisse, zu wenige unabh. Bloecke"); continue
        _,p=stats.ttest_1samp(a,0)
        # Bounce zur Gegenprobe
        bn=levels.bounce_events(by,df,min_touch=mt,zone_atr=0.25)
        sb={}
        for (t,d,_,_) in bn:
            b=t//HZ
            if b not in sb and t+HZ<n: sb[b]=(c[t+HZ]/c[t]-1)*d
        ab=np.array(list(sb.values()))*1e4
        btxt = f"{ab.mean():+7.1f} bp" if len(ab)>=15 else "     —  "
        print(f"  >={mt} Ber.: Ausbruch {len(ev):4d} Ereignisse, {a.mean():+7.1f} bp "
              f"(p={p:.3f})  |  Bounce {btxt}")
    # Pass-Rate der Handelsregel
    ev=levels.breakout_events(by,df,min_touch=6)
    for lev in (1.0,0.5):
        pos=np.zeros(n)
        for (t,d,_,_) in ev: pos[t:min(t+24,n)]+=d
        w=pd.Series(np.clip(pos,-1,1),index=df.index).astype(float)*lev
        held=w.shift(1); s=held*ret-COST*held.diff().abs().fillna(0)
        dd=((1+s.dropna()).resample("1D").prod()-1).dropna().to_numpy()
        p_=f_=cn=0
        for st in range(0,len(dd)-1):
            eq=1.0; done=None
            for i in range(st,min(st+365,len(dd))):
                r=dd[i]
                if r<-.03: done="f";break
                eq*=(1+r)
                if eq<=.94: done="f";break
                if eq-1>=.10: done="p";break
            if done=="p": p_+=1
            elif done=="f": f_+=1
            else: cn+=1
        tot=p_+f_+cn
        print(f"  Pass-Rate bei {lev:.1f}x: {p_/(p_+f_)*100 if p_+f_ else 0:5.1f} % "
              f"(Untergrenze {p_/tot*100:5.1f} %, {cn/tot*100:.0f} % offen)")
    print()

run(V+"btc_1h.csv", "BTC (bekannt -- zum Vergleich)")
run(V+"eth_1h.csv", "ETH (nie verwendet -- unabhaengiger Beleg)")
