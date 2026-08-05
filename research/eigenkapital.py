"""Eigenes Kapital, eigener Hebel, kein Tageslimit.
Damit aendert sich die Zielgroesse: nicht Pass-Rate, sondern SHARPE --
denn Sharpe ist das, was man hebeln kann.

Geprueft: beide ueberlebenden Ansaetze als eigenstaendige Anlage,
mit voller Gebuehrensensitivitaet.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy.stats import norm
from prop_backtester import levels

V="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
SPLIT=pd.Timestamp("2025-01-01",tz="UTC")

def sr_daily(asset="btc", cost_bp=16.0, hold=48, one=True):
    d=pd.read_csv(V+f"{asset}_1h.csv",index_col=0,parse_dates=True)
    h=pd.Series(d["close"].to_numpy(),index=d.index).pct_change().fillna(0)
    by=levels.build_levels(d,width=8,tol_atr=0.5,max_age=1000)
    ev=levels.breakout_events(by,d,min_touch=6)
    n=len(d); pos=np.zeros(n); busy=-1; ntr=0
    for (t,dr,_,_) in ev:
        if one and t<busy: continue
        if one: pos[t:t+hold]=dr; busy=t+hold
        else:   pos[t:t+hold]+=dr
        ntr+=1
    w=pd.Series(np.clip(pos,-1,1),index=d.index).astype(float)
    held=w.shift(1); s=held*h-cost_bp/1e4*held.diff().abs().fillna(0)
    return ((1+s.dropna()).resample("1D").prod()-1).dropna(), ntr

def stats(r, periods=365):
    ann=(1+r).prod()**(periods/len(r))-1
    vol=r.std()*np.sqrt(periods)
    sh=r.mean()/r.std()*np.sqrt(periods)
    eq=(1+r).cumprod(); dd=(eq/eq.cummax()-1).min()
    kelly=r.mean()*periods/(vol**2) if vol>0 else 0
    return ann*100, vol*100, sh, dd*100, kelly

print("="*94)
print("A) S/R-AUSBRUCH als eigenstaendige Anlage (BTC, 1,0x, ohne Challenge-Regeln)")
print("="*94)
print(f"  {'Gebuehr/RT':>11s} {'Rendite p.a.':>13s} {'Vol':>8s} {'Sharpe':>8s} "
      f"{'max. DD':>9s} {'Kelly-Hebel':>12s}")
print("  "+"-"*68)
for c in [16,12,8,6,4,2,0]:
    r,ntr=sr_daily(cost_bp=c)
    a,v,s,dd,k=stats(r)
    print(f"  {c:>10.0f}bp {a:>+12.1f}% {v:>7.1f}% {s:>8.2f} {dd:>8.1f}% {k:>11.2f}x")
r16,ntr=sr_daily(cost_bp=16)
print(f"\n  {ntr} Trades in 5,4 Jahren = {ntr/5.4:.0f} im Jahr.")
print("  Gebuehr wirkt linear: jeder Basispunkt weniger ist bares Geld,")
print("  aber bei 40 Trades im Jahr ist der Hebel darauf KLEIN.")

print()
print("="*94)
print("B) VOLATILITAETS-RISIKOPRAEMIE -- der Edge, den die Challenge verboten hat")
print("="*94)
px=pd.read_csv(V+"btc_1h.csv",index_col=0,parse_dates=True)["close"].resample("1D").last().dropna()
iv=pd.read_csv(V+"dvol_BTC.csv",index_col=0,parse_dates=True)["close"].resample("1D").last().dropna()
df=pd.DataFrame({"px":px,"iv":iv}).dropna()
def bs(S,K,T,s):
    if T<=1e-9: return abs(S-K),(1.0 if S>K else -1.0)
    d1=(np.log(S/K)+.5*s*s*T)/(s*np.sqrt(T)); d2=d1-s*np.sqrt(T)
    return (S*norm.cdf(d1)-K*norm.cdf(d2))+(K*norm.cdf(-d2)-S*norm.cdf(-d1)), norm.cdf(d1)-norm.cdf(-d1)
def straddle(tenor=30, ba_vol=0.0, hedge_bp=0.0, fee_bp=0.0):
    dts=df.index; out=[]; i=0
    while i+tenor<len(dts):
        S0=df["px"].iloc[i]; sig=df["iv"].iloc[i]/100*(1-ba_vol); K=S0; T=tenor/365
        prem,d0=bs(S0,K,T,sig); pnl=prem; hedge=d0; Sp=S0
        for j in range(1,tenor+1):
            Sj=df["px"].iloc[i+j]; Tj=(tenor-j)/365
            pnl+=hedge*(Sj-Sp)
            _,dn=bs(Sj,K,max(Tj,1e-9),df["iv"].iloc[i+j]/100)
            pnl-=abs(dn-hedge)*Sj*hedge_bp/1e4
            hedge=dn; Sp=Sj
        ST=df["px"].iloc[i+tenor]; pnl-=abs(ST-K)
        pnl-=S0*fee_bp/1e4
        out.append(pnl/S0); i+=tenor
    return pd.Series(out)
print(f"  {'Szenario':40s} {'Ø/Monat':>9s} {'p.a.':>9s} {'Sharpe':>8s} "
      f"{'schlecht.Monat':>15s}")
print("  "+"-"*76)
SC=[("ideal (keine Reibung)",0.0,0.0,0.0),
    ("realistisch (2 Vol-Pkt, 5 bp Hedge)",0.02,5.0,0.0),
    ("+ Deribit-Gebuehren (~3 bp Notional)",0.02,5.0,3.0),
    ("konservativ (4 Vol-Pkt, 10 bp, 6 bp)",0.04,10.0,6.0),
    ("sehr konservativ (6 Vol-Pkt, 20 bp)",0.06,20.0,10.0)]
for name,bav,hb,fb in SC:
    r=straddle(ba_vol=bav,hedge_bp=hb,fee_bp=fb)
    a,v,s,dd,k=stats(r,periods=12)
    print(f"  {name:40s} {r.mean()*100:>+8.2f}% {a:>+8.1f}% {s:>8.2f} {r.min()*100:>+14.1f}%")

print()
print("="*94)
print("C) DIREKTVERGLEICH -- was ist die bessere Anlage?")
print("="*94)
rs,_=sr_daily(cost_bp=16); a1,v1,s1,dd1,k1=stats(rs)
rv=straddle(ba_vol=0.02,hedge_bp=5.0,fee_bp=3.0); a2,v2,s2,dd2,k2=stats(rv,12)
bh=px.pct_change().dropna(); a3,v3,s3,dd3,k3=stats(bh)
print(f"  {'':26s} {'p.a.':>8s} {'Vol':>8s} {'Sharpe':>8s} {'max. DD':>9s} "
      f"{'Kelly':>8s} {'bei 2x Hebel':>13s}")
print("  "+"-"*82)
for name,(a,v,s,dd,k) in [("S/R-Ausbruch BTC",(a1,v1,s1,dd1,k1)),
                          ("Short-Straddle (VRP)",(a2,v2,s2,dd2,k2)),
                          ("BTC einfach halten",(a3,v3,s3,dd3,k3))]:
    print(f"  {name:26s} {a:>+7.1f}% {v:>7.1f}% {s:>8.2f} {dd:>8.1f}% {k:>7.2f}x "
          f"{a*2:>+11.1f}% / DD {dd*2:>.0f}%")
