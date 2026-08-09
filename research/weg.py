"""Die unbequeme Arithmetik: Einkommen = Kapital x Rendite.
Und: welcher Weg kommt wann an?
"""
import numpy as np, pandas as pd
print("="*84)
print("1) WIE VIEL KAPITAL BRAUCHT WELCHES GEHALT?")
print("="*84)
print(f"  {'Monat netto':>12s} " + " ".join(f"{r*100:>10.0f}% p.a." for r in [0.10,0.15,0.20,0.27]))
print("  "+"-"*62)
for m in [500,1000,2000,3000,5000]:
    row=f"  {m:>11,d}€ "
    for r in [0.10,0.15,0.20,0.27]:
        row+=f"{m*12/r:>13,.0f}€"
    print(row)
print("""
  Das ist keine Meinung, das ist Division. Bei 20 % im Jahr --
  einer sehr guten Rendite -- kosten 3.000 € im Monat 180.000 € Kapital.
  Jeder Weg, der Gehalt aus kleinem Kapital verspricht, ist
  entweder Hebel (= 2024) oder eine Luege.""")

print()
print("="*84)
print("2) DER SPARWEG: wann kommt man an?")
print("="*84)
def jahre(start, sparen, r, ziel):
    k=start; y=0
    while k<ziel and y<40:
        k=k*(1+r)+sparen; y+=1
    return y if k>=ziel else None
ZIEL=180000
print(f"  Ziel: {ZIEL:,} € (= 3.000 €/Monat bei 20 % Rendite)\n")
print(f"  {'Start':>9s} " + " ".join(f"{s:>9,d}€/J" for s in [3000,6000,12000,24000]))
print("  "+"-"*54)
for start in [0,5000,20000,50000]:
    row=f"  {start:>8,d}€ "
    for s in [3000,6000,12000,24000]:
        j=jahre(start,s,0.20,ZIEL)
        row+=f"{(str(j)+' J') if j else '>40 J':>11s}"
    print(row)
print("""
  Lies eine Zeile: Wer bei null anfaengt und 12.000 € im Jahr spart,
  ist bei 20 % Rendite nach 9 Jahren da. Ohne Sparen: nie.
  -> Das SPAREN traegt den Weg, nicht die Rendite.""")

print()
print("="*84)
print("3) Was traegt mehr -- Rendite oder Sparrate?")
print("="*84)
base=jahre(20000,12000,0.20,ZIEL)
print(f"  Ausgangspunkt: 20.000 € Start, 12.000 €/Jahr sparen, 20 % -> {base} Jahre\n")
print(f"  {'Aenderung':>34s} {'Jahre':>7s} {'gespart':>9s}")
print("  "+"-"*54)
for lab,st,sp,r in [("Rendite 20 % -> 27 % (+35 %)",20000,12000,0.27),
                    ("Rendite 20 % -> 30 %",20000,12000,0.30),
                    ("Sparrate 12k -> 16k (+35 %)",20000,16000,0.20),
                    ("Sparrate 12k -> 24k",20000,24000,0.20),
                    ("Start 20k -> 40k",40000,12000,0.20)]:
    j=jahre(st,sp,r,ZIEL)
    print(f"  {lab:>34s} {j:>6d}J {base-j:>+8d}J")
print("""
  -> Eine um 35 % HOEHERE RENDITE spart weniger Zeit als eine um
     35 % hoehere SPARRATE. Und die Sparrate ist sicher.""")

print()
print("="*84)
print("4) Was die Prop-Konten dazu beitragen")
print("="*84)
print("""  Kraken: 85 $ je Challenge, ~70 % Quote bei versetzten Starts,
  10.000 $ Konto, 80 % Split.

  Realistisch je gefundetem Konto und Jahr (S/R, 0,35x):""")
for r,lab in [(0.10,"schwaches Jahr"),(0.18,"Ø Jahr"),(0.30,"gutes Jahr")]:
    print(f"    {lab:16s} {10000*r*0.8:>7,.0f} $ fuer dich")
print(f"""
  Bei drei gefundeten Konten also grob 2.400 - 7.200 $ im Jahr --
  UND das Konto ueberlebt im Schnitt nur 102 Tage
  (siehe trading_as_job.md).

  -> Prop-Konten sind KEIN Gehalt. Sie sind ein Sparbeschleuniger
     mit Ausfallrisiko. In der Tabelle oben verschieben sie die
     Sparrate um vielleicht 3.000-5.000 € im Jahr.""")
