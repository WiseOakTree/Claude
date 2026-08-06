"""Die Konsistenzregel neu gemessen -- JE TRADE statt je Tag.

Vorher habe ich den besten TAG gemessen (10,1 % des Jahresgewinns).
Google sagt: Vanquish misst "Best Trade / Total Profits". Das ist eine
voellig andere Groesse -- bei ~12 Zyklen im Jahr traegt jeder gewonnene
Zyklus im Schnitt 8,3 %, aber Verlustzyklen heben den Anteil der Gewinner.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
exec(open("condor.py").read().split('print("="*94)')[0])
X,W,STOP=0.05,0.025,0.50
r,cr,st,ml=condor(X,W,skew=0.7,stop=STOP)
x=r.to_numpy()
print("="*88)
print("KONSISTENZREGEL: bester TRADE gegen Gesamtgewinn")
print("="*88)
print(f"  Konfiguration: Strangle +-{X*100:.0f} %, Fluegel {W*100:.1f} %, Stop {STOP*100:.0f} %")
print(f"  {len(x)} Zyklen ueber {len(x)/12:.1f} Jahre\n")
print(f"  Trefferquote {(x>0).mean()*100:.1f} %   "
      f"Ø Gewinnzyklus {x[x>0].mean()*100:+.3f} %   Ø Verlustzyklus {x[x<0].mean()*100:+.3f} %\n")

# Rollierende 12-Monats-Fenster: Anteil des besten Trades am Gesamtgewinn
res=[]
for st_ in range(0,len(x)-12):
    w=x[st_:st_+12]
    tot=w.sum()
    if tot<=0: res.append(np.nan); continue
    res.append(w.max()/tot*100)
res=np.array(res); ok=res[~np.isnan(res)]
print(f"  {'Anteil des besten Trades am Jahresgewinn':45s}")
print("  "+"-"*52)
print(f"    Median                    {np.median(ok):>6.1f} %")
print(f"    Mittelwert                {ok.mean():>6.1f} %")
print(f"    75. Perzentil             {np.percentile(ok,75):>6.1f} %")
print(f"    90. Perzentil             {np.percentile(ok,90):>6.1f} %")
print(f"    Maximum                   {ok.max():>6.1f} %")
print()
for schwelle in [20,30,40,50]:
    print(f"    Jahre ueber {schwelle} %:          {(ok>schwelle).mean()*100:>6.1f} %")
print(f"    (Jahre mit Gesamtverlust: {np.isnan(res).mean()*100:.1f} %)")

print()
print("="*88)
print("Hilft es, die AUSZAHLUNG spaeter zu nehmen?")
print("="*88)
print("  Je laenger man sammelt, desto kleiner der Anteil des besten Trades.\n")
print(f"  {'Sammelzeitraum':>18s} {'Median':>9s} {'90. Perz.':>11s} {'ueber 30 %':>12s}")
print("  "+"-"*54)
for M,lab in [(3,"3 Monate"),(6,"6 Monate"),(12,"12 Monate"),(24,"24 Monate")]:
    rr=[]
    for st_ in range(0,len(x)-M):
        w=x[st_:st_+M]; t=w.sum()
        if t>0: rr.append(w.max()/t*100)
    rr=np.array(rr)
    print(f"  {lab:>18s} {np.median(rr):>8.1f}% {np.percentile(rr,90):>10.1f}% "
          f"{(rr>30).mean()*100:>11.1f}%")

print()
print("="*88)
print("Und die Behauptung, das Problem 'multipliziere' sich ueber Konten")
print("="*88)
print(f"""  Das stimmt NICHT, solange je Konto gemessen wird.
  Drei Konten mit identischen Positionen haben jeweils DENSELBEN
  Anteil des besten Trades am Gesamtgewinn -- das Verhaeltnis ist
  skaleninvariant. Drei mal {np.median(ok):.0f} % ist immer noch {np.median(ok):.0f} %.

  Es wuerde nur dann schlimmer, wenn die Firma die Konten fuer die
  Konsistenzpruefung ZUSAMMENFASST -- und dann waere auch der
  Puffer-Vorteil weg. Beides haengt an derselben Frage.""")
