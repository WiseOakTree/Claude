"""Die offenen Fragen an einer ECHTEN SPX-Kette (CBOE, kostenlos, mit Bid/Ask).

1) Wie viel Prozent der Straddle-Praemie behaelt ein enger Iron Condor wirklich?
2) Wie gross ist die Geld-Brief-Spanne -- also die Slippage auf 4 Legs?
"""
import json, re, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from datetime import datetime

d=json.load(open("spx_chain.json"))["data"]
S=d["current_price"]; asof=pd.Timestamp(d["last_trade_time"])
rows=[]
for o in d["options"]:
    m=re.match(r"^SPX[W]?(\d{6})([CP])(\d{8})$", o["option"])
    if not m: continue
    exp=pd.Timestamp("20"+m.group(1)[:2]+"-"+m.group(1)[2:4]+"-"+m.group(1)[4:6])
    rows.append(dict(exp=exp, typ=m.group(2), K=int(m.group(3))/1000,
                     bid=o["bid"], ask=o["ask"], iv=o["iv"], delta=o["delta"],
                     oi=o["open_interest"]))
c=pd.DataFrame(rows)
c["dte"]=(c.exp-asof.normalize()).dt.days
c["mid"]=(c.bid+c.ask)/2
c["spread"]=c.ask-c.bid
c=c[(c.bid>0)&(c.mid>0)]
print("="*88)
print(f"ECHTE SPX-KETTE   Spot {S:,.2f}   Stand {asof:%Y-%m-%d %H:%M}   {len(c):,} Optionen")
print("="*88)

# Verfall bei ~30 Tagen
target=30
dtes=sorted(c.dte.unique())
dte=min([x for x in dtes if x>=20], key=lambda x: abs(x-target))
ch=c[c.dte==dte].copy()
print(f"  Gewaehlter Verfall: {dte} Tage, {len(ch)} Kontrakte\n")

def leg(typ,K):
    sub=ch[(ch.typ==typ)]
    r=sub.iloc[(sub.K-K).abs().argsort().iloc[0]]
    return r

atm_c=leg("C",S); atm_p=leg("P",S)
straddle=atm_c.mid+atm_p.mid
print(f"  ATM-Straddle: Call {atm_c.mid:.2f} + Put {atm_p.mid:.2f} = {straddle:.2f} "
      f"= {straddle/S*100:.2f} % des Spot")
print(f"    (Modellwert war 4,23 % -- gemessen {straddle/S*100:.2f} %)\n")

print("="*88)
print("FRAGE 1: Wie viel behaelt ein Iron Condor?")
print("="*88)
print(f"  {'Strangle':>9s} {'Fluegel':>8s} {'Kredit MID':>11s} {'in % Spot':>10s} "
      f"{'Anteil Straddle':>16s} {'max.Verlust':>12s}")
print("  "+"-"*72)
res=[]
for x in [0.02,0.03,0.04,0.05,0.06]:
    for w in [0.008,0.015,0.025]:
        sp=leg("P",S*(1-x)); lp=leg("P",S*(1-x-w))
        sc=leg("C",S*(1+x)); lc=leg("C",S*(1+x+w))
        cred=(sp.mid+sc.mid)-(lp.mid+lc.mid)
        width=max(sp.K-lp.K, lc.K-sc.K)
        res.append((x,w,cred,width))
        print(f"  {x*100:>8.1f}% {w*100:>7.1f}% {cred:>10.2f} {cred/S*100:>9.3f}% "
              f"{cred/straddle*100:>15.1f}% {(width-cred)/S*100:>11.2f}%")

print()
print("="*88)
print("FRAGE 2: Die Geld-Brief-Spanne -- was kostet der Ein- und Ausstieg?")
print("="*88)
print(f"  {'Position':>26s} {'Bid':>9s} {'Ask':>9s} {'Spanne':>8s} {'% vom Mid':>10s}")
print("  "+"-"*66)
for nm,r in [("ATM Call",atm_c),("ATM Put",atm_p),
             ("Short Put -5 %",leg("P",S*0.95)),("Long Put -6,5 %",leg("P",S*0.935)),
             ("Short Call +5 %",leg("C",S*1.05)),("Long Call +6,5 %",leg("C",S*1.065))]:
    print(f"  {nm:>26s} {r.bid:>8.2f} {r.ask:>8.2f} {r.spread:>7.2f} "
          f"{r.spread/r.mid*100:>9.1f}%")

x,w=0.05,0.015
sp=leg("P",S*(1-x)); lp=leg("P",S*(1-x-w)); sc=leg("C",S*(1+x)); lc=leg("C",S*(1+x+w))
cred_mid=(sp.mid+sc.mid)-(lp.mid+lc.mid)
cred_bad=(sp.bid+sc.bid)-(lp.ask+lc.ask)          # schlechtester Fill
half=sum(r.spread for r in [sp,lp,sc,lc])/2
print(f"""
  Condor +-5 % / 1,5 %:
    Kredit zum Mid          {cred_mid:>8.2f}  ({cred_mid/S*100:.3f} % des Spot)
    Kredit im schlechtesten Fall {cred_bad:>3.2f}  ({cred_bad/S*100:.3f} %)
    Summe halber Spannen    {half:>8.2f}  ({half/S*100:.3f} % des Spot)

    -> Ein Roundtrip (rein UND raus) kostet bei Mid-Fills etwa
       {2*half/S*100:.3f} % des Nominals -- gegen einen Kredit von
       {cred_mid/S*100:.3f} %. Das sind {2*half/cred_mid*100:.0f} % des Kredits.""")
