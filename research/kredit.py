"""Kredit auf die Haus-Seite: die vollstaendige Rechnung.

Grundlage: die GEMESSENE HLP-Verteilung (90 Perioden a 14 Tage) und der
gemessene Ertragsverfall (2024 +79 %, 2025 +19 %, 2026 hochgerechnet ~11 %).
"""
import warnings; warnings.filterwarnings("ignore")
import json,subprocess
import numpy as np, pandas as pd
body=json.dumps({"type":"vaultDetails",
                 "vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"})
r=subprocess.run(["curl","-sS","--max-time","90","-X","POST",
    "-H","Content-Type: application/json","-d",body,
    "https://api.hyperliquid.xyz/info"],capture_output=True)
port=dict(json.loads(r.stdout)["portfolio"])
def reihe(f):
    x=pd.DataFrame(port["allTime"][f],columns=["ms","w"]); x["w"]=x.w.astype(float)
    x["ts"]=pd.to_datetime(x.ms,unit="ms",utc=True); return x.set_index("ts").w.sort_index()
W=reihe("accountValueHistory"); P=reihe("pnlHistory")
D=pd.DataFrame({"w":W,"p":P}).dropna(); D["r"]=D.p.diff()/D.w.shift(1)
D=D[(D.w.shift(1)>1e6)&np.isfinite(D.r)]
R=D.r.to_numpy(); per=365/14

print("="*90)
print("1. DER ZINSSPREAD -- und was vom Ertrag uebrig bleibt")
print("="*90)
print(f"  {'Erwartete Vault-Rendite':<26}"+"".join(f"{x:>13}" for x in
      ["37 % (2023-26)","19 % (2025)","11 % (2026)"]))
for zins,lab in ((4,"Lombard/Wertpapier 4 %"),(7,"Rahmenkredit 7 %"),
                 (10,"Ratenkredit 10 %"),(13,"Dispo 13 %")):
    print(f"  {lab:<26}"+"".join(f"{v-zins:>+12.1f} %" for v in (37.3,19.0,11.0)))
print("\n  -> Beim aktuellen Ertragsniveau (~11 %) ist der Spread bei jedem")
print("     Konsumentenkredit NEGATIV oder nahe null. Nur ein Lombardkredit")
print("     zu 4 % laesst ueberhaupt etwas uebrig -- und der verlangt")
print("     Wertpapiere als Sicherheit, die man dann schon haette.")

print("\n"+"="*90)
print("2. GEHEBELT: Rendite und Rueckgang auf der GEMESSENEN Verteilung")
print("="*90)
print(f"  {'Hebel':<8}{'Rendite p.a.':>15}{'nach 7 % Zins':>16}"
      f"{'groesster Rueckgang':>22}{'schlechteste Periode':>22}")
for h in (1,2,3,5,10):
    rr=R*h
    kum=(1+rr).prod(); jahre=len(R)/per
    ann=(kum**(1/jahre)-1)*100 if kum>0 else -100
    eq=np.cumprod(1+rr); dd=(eq/np.maximum.accumulate(eq)-1).min()*100
    zins=7*(h-1)
    print(f"  {h}x{'':<6}{ann:>+14.1f} %{ann-zins:>+15.1f} %{dd:>21.1f} %"
          f"{rr.min()*100:>21.1f} %")

print("\n"+"="*90)
print("3. DER FALL, DER NOCH NICHT EINGETRETEN IST")
print("="*90)
print("  Der Vault ist ein Versicherungsgeschaeft. In drei Jahren gab es")
print("  keinen Tag, an dem alle Trader gleichzeitig recht hatten.")
print("  Was passiert, wenn doch?\n")
print(f"  {'Verlust des Vaults':<22}{'bei 1x':>11}{'bei 2x':>11}{'bei 3x':>11}"
      f"{'bei 5x':>11}{'bei 10x':>11}")
for v in (10,20,30,50,80,100):
    zeile=[]
    for h in (1,2,3,5,10):
        eigen=100 - v*h            # Eigenkapital nach dem Ereignis, in % des Einsatzes
        zeile.append(f"{eigen:>10.0f}%")
    print(f"  -{v:>3} % des Vaults{'':<5}"+"".join(zeile))
print("\n  Ab -20 % ist ein 5x-Konto weg. Ab -10 % ein 10x-Konto.")
print("  Und der Kredit bleibt in voller Hoehe bestehen.")

print("\n"+"="*90)
print("4. DIE ZWEITE FALLE: der Ertrag faellt, der Zins nicht")
print("="*90)
print(f"  {'Jahr':<8}{'Vault-Ertrag':>15}{'Zins 7 %':>12}{'Netto 3x':>12}")
for j,e in ((2023,19.6),(2024,79.1),(2025,19.0),(2026,11.0)):
    netto=e*3-7*2
    print(f"  {j:<8}{e:>+14.1f} %{-7.0:>11.1f} %{netto:>+11.1f} %")
print("\n  2024 haette 3x Hebel +223 % gebracht. 2026 sind es +19 %.")
print("  Der Zins war in beiden Jahren derselbe.")
print("  Ein Kredit laeuft 5-7 Jahre -- der Ertrag, auf den man ihn")
print("  aufnimmt, existiert dann vermutlich nicht mehr.")

print("\n"+"="*90)
print("5. WAS DER KREDIT WIRKLICH KOSTET, wenn alles gut geht")
print("="*90)
K=20000
for zins,jahre in ((7,5),(10,5),(7,7)):
    rate=K*(zins/100)/(1-(1+zins/100)**-jahre)
    gesamt=rate*jahre
    for ertrag in (11,19):
        wert=K*(1+ertrag/100)**jahre
        print(f"  {K:,} $ zu {zins} % ueber {jahre} J  ->  zurueckzuzahlen "
              f"{gesamt:>8,.0f} $   Anlage bei {ertrag} %: {wert:>8,.0f} $   "
              f"Ergebnis {wert-gesamt:>+9,.0f} $")
