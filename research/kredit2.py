"""Was sagen drei Jahre ohne Schadensfall ueber die Schadenshaeufigkeit?
Und wie oft geht ein gehebeltes Konto kaputt, wenn es doch einen gibt?
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
R=D.r.to_numpy(); jahre=len(R)/(365/14)

print("="*88)
print("1. WAS SAGEN 3,2 JAHRE OHNE SCHADENSFALL?")
print("="*88)
print(f"  Beobachtungen: {len(R)} Perioden ueber {jahre:.2f} Jahre")
print(f"  schlechteste Periode: {R.min()*100:.2f} %")
print(f"  Ereignisse mit -20 % oder schlimmer: 0\n")
print("  Dreierregel: bei 0 Ereignissen in n Versuchen liegt die obere")
print("  95-%-Schranke der Rate bei 3/n.")
print(f"    je 14-Tage-Periode:  bis zu {3/len(R)*100:.1f} %")
print(f"    je Jahr:             bis zu {min(3/jahre,1)*100:.0f} %")
print("\n  -> Aus drei Jahren ohne Schaden folgt PRAKTISCH NICHTS ueber die")
print("     Schadenshaeufigkeit. Man kann eine Rate von 'alle 30 Jahre'")
print("     genauso wenig ausschliessen wie 'alle 4 Jahre'.")

print("\n"+"="*88)
print("2. RUINWAHRSCHEINLICHKEIT ueber 5 Jahre, je nach angenommener Haeufigkeit")
print("="*88)
rng=np.random.default_rng(11)
print(f"  {'Schaden alle ... Jahre':<24}{'Schadenshoehe':>15}"
      +"".join(f"{f'{h}x':>9}" for h in (1,2,3,5,10)))
for takt in (4,10,25,50):
    for hoehe in (0.30,0.60):
        zeile=[]
        for h in (1,2,3,5,10):
            ruin=0
            for _ in range(1200):
                kap=1.0; kaputt=False
                for p in range(int(5*365/14)):
                    r_=rng.choice(R)
                    if rng.random() < 14/(takt*365): r_=-hoehe
                    kap*= (1+r_*h)
                    if kap<=0: kaputt=True; break
                ruin+=kaputt
            zeile.append(f"{ruin/1200*100:>8.1f}%")
        print(f"  alle {takt:>2} Jahre{'':<12}{f'-{hoehe*100:.0f} %':>15}"+"".join(zeile))

print("\n"+"="*88)
print("3. DASSELBE OHNE KREDIT: was passiert im schlimmsten Fall?")
print("="*88)
print(f"  {'Hebel':<8}{'schlimmster Fall':>22}{'bleibt Schuld?':>18}")
for h in (1,2,3,5,10):
    verlust=min(1.0*h,1.0)
    schuld=max(0,(h-1)-max(0,h*1.0-1.0)*0) if h>1 else 0
    rest = 1-h*1.0
    print(f"  {h}x{'':<6}{'Einsatz weg' if h==1 else f'Einsatz weg + {(h-1)*100:.0f} % Schulden':>22}"
          f"{'nein' if h==1 else f'{(h-1)*100:.0f} % des Einsatzes':>18}")
print("\n  Der Unterschied zwischen 1x und Kredit ist nicht die Rendite.")
print("  Es ist die Frage, ob nach dem schlimmsten Fall NULL dasteht")
print("  oder eine Zahl mit Minuszeichen, die weiterlaeuft.")
