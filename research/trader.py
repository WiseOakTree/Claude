"""'Es gibt profitable Trader, das sieht man in oeffentlichen Statistiken.'

Die Frage ist nicht ob es sie gibt -- die Frage ist, wie viele man sehen
WUERDE, wenn niemand Koennen haette. Erst die Differenz ist der Beweis.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
rng=np.random.default_rng(808)

VOL=0.60      # Jahresvol eines typischen gehebelten Retail-Kontos
print("="*90)
print("A. WIE VIELE 'PROFITABLE TRADER' ZEIGT REINER ZUFALL?")
print("="*90)
print("100.000 Trader, ALLE mit wahrem Erwartungswert null, Jahresvol 60 %\n")
N=100_000
print(f"{'nach':>8}{'im Plus':>11}{'ueber +20 %':>14}{'ueber +50 %':>14}"
      f"{'ueber +100 %':>15}{'jedes Jahr +':>15}")
for jahre in (1,2,3,5,10):
    R=rng.normal(-0.5*VOL**2, VOL, size=(N,jahre))
    kum=np.exp(R.cumsum(1)[:,-1])-1
    jedes=(np.exp(R)-1>0).all(1)
    print(f"{jahre:>6} J{(kum>0).mean()*100:>10.1f}%{(kum>0.20).mean()*100:>13.1f}%"
          f"{(kum>0.50).mean()*100:>13.1f}%{(kum>1.00).mean()*100:>14.1f}%"
          f"{jedes.mean()*100:>14.1f}%")

print(f"\n  Bei 100.000 Tradern sind das nach 5 Jahren:")
R=rng.normal(-0.5*VOL**2,VOL,size=(N,5)); kum=np.exp(R.cumsum(1)[:,-1])-1
jedes=(np.exp(R)-1>0).all(1)
print(f"    {int((kum>1.0).sum()):>6} mit ueber +100 %   -- ohne jedes Koennen")
print(f"    {int(jedes.sum()):>6} mit FUENF Gewinnjahren in Folge -- ohne jedes Koennen")

print("\n"+"="*90)
print("B. UND JETZT MIT ECHTEM KOENNEN: kann man die zwei Gruppen trennen?")
print("="*90)
ANTEIL=0.01          # 1 % haben echtes Koennen
SHARPE=1.0           # und zwar ein sehr gutes
for jahre in (1,3,5,10):
    koennen=rng.random(N)<ANTEIL
    mu=np.where(koennen, SHARPE*VOL, 0.0)
    R=rng.normal(mu[:,None]-0.5*VOL**2, VOL, size=(N,jahre))
    kum=np.exp(R.cumsum(1)[:,-1])-1
    top=kum>np.percentile(kum,99)      # die sichtbare Bestenliste
    print(f"  nach {jahre:>2} Jahren: in den besten 1 % haben "
          f"{koennen[top].mean()*100:>4.1f} % wirklich Koennen "
          f"(Grundrate {ANTEIL*100:.0f} %)")

print("\n"+"="*90)
print("C. DER EINZIGE TEST, DER TRENNT: bleiben sie oben?")
print("="*90)
print("Anteil der Bestenliste aus Jahr 1, der auch im Folgejahr oben ist:\n")
print(f"{'Anteil Koenner':>16}{'Sharpe':>9}{'Persistenz':>14}{'bei reinem Zufall':>20}")
for anteil,sh in ((0.00,0.0),(0.01,1.0),(0.05,1.0),(0.01,2.0),(0.10,0.5)):
    koennen=rng.random(N)<anteil
    mu=np.where(koennen,sh*VOL,0.0)
    j1=rng.normal(mu-0.5*VOL**2,VOL); j2=rng.normal(mu-0.5*VOL**2,VOL)
    top1=j1>np.percentile(j1,99); top2=j2>np.percentile(j2,99)
    print(f"{anteil*100:>14.0f} %{sh:>9.1f}{top2[top1].mean()*100:>13.1f}%{1.0:>19.1f}%")

print("\n"+"="*90)
print("D. WAS DAS FUER EINE BESTENLISTE MIT 1 % KOENNERN BEDEUTET")
print("="*90)
koennen=rng.random(N)<0.01
mu=np.where(koennen,1.0*VOL,0.0)
R=rng.normal(mu[:,None]-0.5*VOL**2,VOL,size=(N,3))
kum=np.exp(R.cumsum(1)[:,-1])-1
for schwelle,lab in ((0.0,"im Plus"),(0.5,"ueber +50 %"),(2.0,"ueber +200 %")):
    sel=kum>schwelle
    print(f"  {lab:<14} {sel.sum():>6} Trader   davon mit echtem Koennen: "
          f"{koennen[sel].mean()*100:>4.1f} %   -> {int(koennen[sel].sum())} echte, "
          f"{int((~koennen[sel]).sum())} Glueckliche")
