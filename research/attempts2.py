"""Kontrolle: Wie stark sind aufeinanderfolgende Versuche korreliert?

Direkt gemessen: P(Versuch 2 besteht | Versuch 1 gescheitert, Start direkt
danach) gegen die unbedingte Quote. Ohne Ketten-Artefakt durch Datenende.
Zusaetzlich die Zeitasymmetrie -- wie lange dauern Erfolge vs. Fehlschlaege.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/attempts.py").read().split("print(\"=\"*90)")[0])

print("="*88)
print("Korrelationskosten und Zeitasymmetrie")
print("="*88)
print(f"  {'Asset':6s} {'P(bestehen)':>12s} {'P(2|1 fiel)':>12s} {'Differenz':>10s} "
      f"{'Ø Tage Erfolg':>14s} {'Ø Tage Fehlschlag':>18s}")
print("  "+"-"*76)
for asset in ["btc","eth","sol","xrp"]:
    dd=daily(asset); n=len(dd)
    out=[]; dur=[]
    for st in range(0,n-60):
        o,d=one_attempt(dd,st); out.append(o); dur.append(d)
    out=np.array(out); dur=np.array(dur)
    solved=out!="c"
    uncond=(out[solved]=="p").mean()*100
    # bedingt: Versuch 1 gescheitert -> Versuch 2 startet st+dur
    hit=[]
    for st in range(0,n-60):
        if out[st]!="f": continue
        s2=st+dur[st]
        if s2>=n-60: continue
        if out[s2]=="c": continue
        hit.append(out[s2]=="p")
    cond=np.mean(hit)*100 if hit else float("nan")
    dp=dur[(out=="p")].mean(); df=dur[(out=="f")].mean()
    print(f"  {asset.upper():6s} {uncond:>11.1f}% {cond:>11.1f}% {cond-uncond:>+9.1f} "
          f"{dp:>13.0f}T {df:>17.0f}T")

print()
print("="*88)
print("Was 3 Versuche kosten -- erwarteter Gesamteinsatz je Ergebnis")
print("="*88)
print(f"  {'Asset':6s} {'P(1)':>7s} {'P(<=3)':>8s} {'Ø Einsatz':>10s} "
      f"{'$ je Erfolg':>12s}")
print("  "+"-"*50)
for asset,p1,p3,sp in [("BTC",50.9,78.7,132),("ETH",27.5,88.9,169),
                       ("SOL",20.6,41.7,208),("XRP",23.2,51.8,201)]:
    print(f"  {asset:6s} {p1:>6.1f}% {p3:>7.1f}% {sp:>9d}$ {sp/(p3/100):>11.0f}$")
