"""Die einfachste ausfuehrbare Regel: EINE Position, nie gestapelt.
Groesse so waehlen, dass die effektive Jahresvol bei ~15 % landet.
Getrennt nach Such/Holdout, alle vier Assets, gegen die Basis.
"""
import sys, warnings; sys.path.insert(0,"/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/oc/simpel.py").read().split('VARIANTS=[')[0])

print("="*94)
print("EINE Position gleichzeitig -- Groessensweep (Vol soll ~15 % treffen)")
print("="*94)
print(f"  {'Asset':6s} {'Groesse':>8s} {'Jahresvol':>10s} {'Such':>8s} {'Holdout':>9s} "
      f"{'gesamt':>8s} {'Trades':>7s}")
print("  "+"-"*62)
best={}
for a in ["btc","eth","sol","xrp"]:
    for lev in [0.35,0.50,0.65,0.80,1.00]:
        s,n=build(a,one_at_a_time=True,lev=lev); s=s.dropna()
        d=((1+s).resample("1D").prod()-1).dropna().to_numpy()
        vol=d.std()*np.sqrt(365)*100
        r=evaluate(s)
        mark=""
        if a not in best or r["ges"]>best[a][0]: best[a]=(r["ges"],lev); mark=""
        print(f"  {a.upper():6s} {lev:>7.2f}x {vol:>9.1f}% {r['Such']:>7.1f}% "
              f"{r['Hold']:>8.1f}% {r['ges']:>7.1f}% {n:>7d}")
    print()

print("="*94)
print("DIREKTVERGLEICH: heutige Regel gegen die einfachste Variante")
print("="*94)
print(f"  {'Asset':6s} {'Basis (stapelnd) 0,5x':>24s} {'1 Position 0,65x':>20s} {'Differenz':>11s}")
print(f"  {'':6s} {'Such / Holdout / ges':>24s} {'Such / Holdout / ges':>20s}")
print("  "+"-"*66)
agg=[[],[]]
for a in ["btc","eth","sol","xrp"]:
    sb,nb=build(a); rb=evaluate(sb.dropna())
    ss,ns=build(a,one_at_a_time=True,lev=0.65); rs=evaluate(ss.dropna())
    agg[0].append(rb["ges"]); agg[1].append(rs["ges"])
    print(f"  {a.upper():6s} {rb['Such']:>7.1f}/{rb['Hold']:>6.1f}/{rb['ges']:>6.1f}"
          f" {rs['Such']:>11.1f}/{rs['Hold']:>6.1f}/{rs['ges']:>6.1f}"
          f" {rs['ges']-rb['ges']:>+10.1f}")
print(f"\n  Mittel gesamt:  Basis {np.mean(agg[0]):.1f}%   einfach {np.mean(agg[1]):.1f}%")
print(f"  Trades:         Basis 3946              einfach {sum(build(a,one_at_a_time=True)[1] for a in ['btc','eth','sol','xrp'])}")
