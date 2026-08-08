"""Was tun die, die es nachweislich koennen? Echte Fills von Hyperliquid.

Gruppe A: in BEIDEN disjunkten Perioden im Plus, Volumen > 2 Mio $ je Periode
Gruppe B: in beiden im Minus, gleiche Groessenordnung
"""
import warnings; warnings.filterwarnings("ignore")
import json,subprocess,time
import numpy as np, pandas as pd
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/hl"
A=pd.read_csv(f"{S}/top.csv")
A["rA"]=A.pnl_A/A.vlm_A; A["rB"]=A.pnl_B/A.vlm_B

gut=A[(A.rA>0)&(A.rB>0)].nlargest(45,"vlm_month")
schlecht=A[(A.rA<0)&(A.rB<0)].nlargest(45,"vlm_month")
print(f"Gruppe GUT      (beide Perioden im Plus):  {len(A[(A.rA>0)&(A.rB>0)])} Konten, "
      f"davon die 45 groessten untersucht")
print(f"Gruppe SCHLECHT (beide Perioden im Minus): {len(A[(A.rA<0)&(A.rB<0)])} Konten\n")

def fills(adr, n=2000):
    body=json.dumps({"type":"userFills","user":adr,"aggregateByTime":False})
    r=subprocess.run(["curl","-sS","--max-time","40","-X","POST",
        "-H","Content-Type: application/json","-d",body,
        "https://api.hyperliquid.xyz/info"],capture_output=True)
    try: return json.loads(r.stdout)
    except Exception: return None

def analyse(adr):
    f=fills(adr)
    if not f or not isinstance(f,list) or len(f)<50: return None
    d=pd.DataFrame(f)
    for c in ("px","sz","closedPnl","fee","startPosition"):
        if c in d: d[c]=pd.to_numeric(d[c],errors="coerce")
    d["ts"]=pd.to_datetime(d.time,unit="ms",utc=True)
    d=d.sort_values("ts")
    spanne=(d.ts.max()-d.ts.min()).total_seconds()/3600
    notional=(d.px*d.sz).sum()
    maker=(d.fee<0).mean() if "fee" in d else np.nan       # negative Gebuehr = Rebate
    crossed=d.get("crossed")
    taker=crossed.mean() if crossed is not None else np.nan
    return dict(adr=adr, fills=len(d), stunden=spanne,
                fills_pro_tag=len(d)/max(spanne/24,1e-9),
                maerkte=d.coin.nunique(),
                top_markt=d.coin.value_counts().index[0],
                anteil_top=d.coin.value_counts().iloc[0]/len(d),
                taker_anteil=taker, maker_rebate_anteil=maker,
                mittl_groesse=notional/len(d),
                gebuehren=d.fee.sum() if "fee" in d else np.nan,
                pnl=d.closedPnl.sum() if "closedPnl" in d else np.nan)

for lab,grp in (("GUT",gut),("SCHLECHT",schlecht)):
    res=[]
    for adr in grp.adr:
        r=analyse(adr)
        if r: res.append(r)
        time.sleep(0.15)
    R=pd.DataFrame(res)
    if not len(R): print(f"{lab}: keine Daten"); continue
    R.to_csv(f"{S}/fills_{lab.lower()}.csv",index=False)
    print("="*84); print(f"GRUPPE {lab}  ({len(R)} Konten mit Fill-Historie)"); print("="*84)
    print(f"  {'Fills pro Tag (Median)':<34}{R.fills_pro_tag.median():>12,.0f}")
    print(f"  {'gehandelte Maerkte (Median)':<34}{R.maerkte.median():>12,.0f}")
    print(f"  {'Anteil auf dem Hauptmarkt':<34}{R.anteil_top.median()*100:>11.0f} %")
    print(f"  {'TAKER-Anteil (Median)':<34}{R.taker_anteil.median()*100:>11.1f} %")
    print(f"  {'Fills mit Maker-Rebate':<34}{R.maker_rebate_anteil.median()*100:>11.1f} %")
    print(f"  {'mittlere Ordergroesse ($)':<34}{R.mittl_groesse.median():>12,.0f}")
    print(f"  {'Beobachtungsfenster (Stunden)':<34}{R.stunden.median():>12,.0f}")
    print(f"  {'gezahlte Gebuehren ($, Median)':<34}{R.gebuehren.median():>12,.0f}")
    print()
