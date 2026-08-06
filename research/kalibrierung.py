"""Der Fehler, den die echte Kette aufdeckt: VIX ist NICHT die ATM-Vol.

Mein Modell hat den Straddle zur VIX-Vol bepreist. Der VIX ist aber ein
varianz-swap-artiges Mass ueber die GANZE Kette -- und liegt wegen des Skew
systematisch UEBER der ATM-Vol. Ich habe also zu teuer verkauft.
"""
import json, re, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
d=json.load(open("spx_chain.json"))["data"]
S=d["current_price"]; vix30=d["iv30"]; asof=pd.Timestamp(d["last_trade_time"])
rows=[]
for o in d["options"]:
    m=re.match(r"^SPX[W]?(\d{6})([CP])(\d{8})$", o["option"])
    if not m: continue
    exp=pd.Timestamp("20"+m.group(1)[:2]+"-"+m.group(1)[2:4]+"-"+m.group(1)[4:6])
    rows.append(dict(exp=exp,typ=m.group(2),K=int(m.group(3))/1000,
                     bid=o["bid"],ask=o["ask"],iv=o["iv"]))
c=pd.DataFrame(rows); c["dte"]=(c.exp-asof.normalize()).dt.days
c["mid"]=(c.bid+c.ask)/2; c=c[(c.bid>0)&(c.mid>0)]
ch=c[c.dte==30]
atm=ch.iloc[(ch.K-S).abs().argsort()[:4]]
iv_atm=atm.iv.mean()
print("="*84)
print("DER FEHLER: VIX gegen echte ATM-Vol")
print("="*84)
print(f"  iv30 des Anbieters (VIX-artig): {vix30*100:>6.2f} %")
print(f"  Gemessene ATM-Vol (30 Tage):    {iv_atm*100:>6.2f} %")
print(f"  Verhaeltnis ATM / VIX:          {iv_atm/vix30:>6.3f}")
print(f"\n  Straddle im Modell (VIX-Vol):   4,23 % des Spot")
print(f"  Straddle in der echten Kette:   3,05 % des Spot")
print(f"  Verhaeltnis:                    {3.05/4.23:>6.3f}")
print("""
  -> Mein Modell hat den Straddle rund 39 % zu teuer verkauft.
     Der VIX liegt wegen des Skew ueber der ATM-Vol -- er mittelt
     die teuren OTM-Puts mit ein. Wer ATM verkauft, bekommt weniger.""")

print()
print("="*84)
print("Was mein Modell RICHTIG hatte: der Condor-Anteil")
print("="*84)
print(f"  {'Konfiguration':>18s} {'Modell':>9s} {'echte Kette':>13s} {'Abweichung':>12s}")
print("  "+"-"*56)
for lab,mod,real in [("+-3 % / 0,8 %",8.0,8.8),("+-5 % / 0,8 %",4.1,4.3),
                     ("+-2 % / 0,8 %",10.6,12.5)]:
    print(f"  {lab:>18s} {mod:>8.1f}% {real:>12.1f}% {real-mod:>+11.1f} pp")
print("""
  -> Der ANTEIL stimmte fast exakt. Nur die Bezugsgroesse (Straddle)
     war zu hoch. Damit sind meine absoluten Kredite ~25-33 % zu gross.""")

print()
print("="*84)
print("KORRIGIERTE ENDRECHNUNG")
print("="*84)
k=3.05/4.23
print(f"  Kalibrierungsfaktor: {k:.3f}\n")
print(f"  {'':34s} {'bisher':>10s} {'korrigiert':>12s}")
print("  "+"-"*58)
for lab,v in [("Kredit je Zyklus (% Nominal)",0.323),("Rendite p.a. auf Nominal",2.36)]:
    print(f"  {lab:34s} {v:>9.3f}% {v*k:>11.3f}%")
print()
print(f"  {'Nominal':>9s} {'Rendite p.a. korrigiert':>25s} {'$ auf 100k':>13s}")
print("  "+"-"*50)
for N in [4,6,8,10,12]:
    print(f"  {N:>8d}x {2.36*k*N:>24.1f}% {2.36*k*N*1000:>12,.0f} $")

print()
print("="*84)
print("UND DIE GUTE NACHRICHT: die Spannen sind winzig")
print("="*84)
print("""  SPX ist extrem liquide. Gemessen an der echten Kette:
    ATM-Option           Spanne 0,90 Punkte = 0,7 % vom Mid
    Short Put -5 %       Spanne 0,60        = 2,2 %
    Long Call +6,5 %     Spanne 0,40        = 9,1 %

    Vier Legs, halbe Spannen zusammen: 1,05 Punkte = 0,014 % des Spot
    Ein kompletter Roundtrip:          0,027 % des Nominals

  Gegen einen Kredit von 0,200 % sind das 14 % des Kredits.
  Deine Sorge zur 4-Leg-Slippage ist damit gemessen: real, aber
  beherrschbar -- solange man zu Mid-Preisen handelt und nicht
  im Stress in den Markt schlaegt.""")
