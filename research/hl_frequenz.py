"""Die entscheidende Frage: Gibt es dauerhaft profitable Trader, die mit
MENSCHLICHER Frequenz handeln -- also ein paar Trades am Tag statt tausend?
"""
import warnings; warnings.filterwarnings("ignore")
import json,subprocess,time
import numpy as np, pandas as pd
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/hl"
L=pd.read_csv(f"{S}/leaderboard.csv")
L["pnl_A"]=L.pnl_month-L.pnl_week; L["vlm_A"]=L.vlm_month-L.vlm_week
L["pnl_B"]=L.pnl_week-L.pnl_day;   L["vlm_B"]=L.vlm_week-L.vlm_day
# aktiv in beiden Perioden, aber Schwelle niedriger -> auch kleinere Trader
A=L[(L.vlm_A>2e5)&(L.vlm_B>2e5)&(L.wert>5000)].copy()
A["rA"]=A.pnl_A/A.vlm_A; A["rB"]=A.pnl_B/A.vlm_B
A["dauerhaft"]=(A.rA>0)&(A.rB>0)
print(f"Konten in der Auswahl: {len(A):,}   davon in beiden Perioden im Plus: "
      f"{A.dauerhaft.sum():,} ({A.dauerhaft.mean()*100:.1f} %)")

def fills(adr):
    body=json.dumps({"type":"userFills","user":adr,"aggregateByTime":False})
    r=subprocess.run(["curl","-sS","--max-time","30","-X","POST",
        "-H","Content-Type: application/json","-d",body,
        "https://api.hyperliquid.xyz/info"],capture_output=True)
    try:
        f=json.loads(r.stdout)
        return f if isinstance(f,list) else None
    except Exception: return None

def profil(adr):
    f=fills(adr)
    if not f or len(f)<30: return None
    d=pd.DataFrame(f); d["ts"]=pd.to_datetime(d.time,unit="ms",utc=True)
    d=d.sort_values("ts")
    h=(d.ts.max()-d.ts.min()).total_seconds()/3600
    if h<1: return None
    for c in ("px","sz","fee","closedPnl"):
        if c in d: d[c]=pd.to_numeric(d[c],errors="coerce")
    return dict(adr=adr, pro_tag=len(f)/(h/24), taker=d.get("crossed",pd.Series([np.nan])).mean(),
                groesse=(d.px*d.sz).mean(), maerkte=d.coin.nunique(), fenster_h=h)

# Stichprobe quer durch die Groessen, dauerhaft gute UND schlechte
np.random.seed(3)
stich=pd.concat([A[A.dauerhaft].sample(min(70,A.dauerhaft.sum())),
                 A[~A.dauerhaft].sample(70)])
res=[]
for _,r in stich.iterrows():
    p=profil(r.adr)
    if p: p["dauerhaft"]=r.dauerhaft; p["rA"]=r.rA; p["rB"]=r.rB; res.append(p)
    time.sleep(0.12)
R=pd.DataFrame(res); R.to_csv(f"{S}/frequenz.csv",index=False)
print(f"Fill-Historie erhalten fuer {len(R)} Konten "
      f"({R.dauerhaft.sum()} dauerhaft im Plus)\n")

print("="*90)
print("DAUERHAFTE PROFITABILITAET NACH HANDELSFREQUENZ")
print("="*90)
kanten=[0,20,100,500,2000,1e9]
lab=["unter 20 Fills/Tag (menschlich)","20-100 (aktiv, noch manuell)",
     "100-500 (halbautomatisch)","500-2000 (Bot)","ueber 2000 (HFT)"]
R["kl"]=pd.cut(R.pro_tag,kanten,labels=lab)
print(f"  {'Frequenzklasse':<34}{'n':>5}{'dauerhaft im Plus':>20}{'Ø Taker-Anteil':>17}")
for k in lab:
    g=R[R.kl==k]
    if not len(g): continue
    print(f"  {k:<34}{len(g):>5}{g.dauerhaft.mean()*100:>18.1f} %"
          f"{g.taker.mean()*100:>15.1f} %")

print("\n"+"="*90)
print("UND UMGEKEHRT: wie handeln die, die es dauerhaft schaffen?")
print("="*90)
for lab2,sel in (("dauerhaft im Plus",R.dauerhaft),("dauerhaft im Minus",~R.dauerhaft)):
    g=R[sel]
    print(f"  {lab2}  (n={len(g)})")
    print(f"    Fills pro Tag:  Median {g.pro_tag.median():>8,.0f}   "
          f"25.-75. Perzentil {g.pro_tag.quantile(.25):,.0f} - {g.pro_tag.quantile(.75):,.0f}")
    print(f"    Taker-Anteil:   Median {g.taker.median()*100:>7.1f} %")
    print(f"    unter 20 Fills/Tag: {(g.pro_tag<20).mean()*100:>5.1f} %   "
          f"ueber 500: {(g.pro_tag>500).mean()*100:.1f} %")
n_mensch=(R.pro_tag<20).sum()
n_mensch_gut=((R.pro_tag<20)&R.dauerhaft).sum()
print(f"\n  Konten mit menschlicher Frequenz in der Stichprobe: {n_mensch}")
print(f"  davon dauerhaft im Plus: {n_mensch_gut}")
