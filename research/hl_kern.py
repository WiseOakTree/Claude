"""Korrektur: 'in beiden Perioden im Plus' ist fast reiner Zufall.
Das echte Signal sitzt in den RAENDERN. Also: wer ist in BEIDEN Perioden
im obersten Dezil -- und wie handeln DIE?
"""
import warnings; warnings.filterwarnings("ignore")
import json,subprocess,time
import numpy as np, pandas as pd
S="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/hl"
L=pd.read_csv(f"{S}/leaderboard.csv")
L["pnl_A"]=L.pnl_month-L.pnl_week; L["vlm_A"]=L.vlm_month-L.vlm_week
L["pnl_B"]=L.pnl_week-L.pnl_day;   L["vlm_B"]=L.vlm_week-L.vlm_day
A=L[(L.vlm_A>1e6)&(L.vlm_B>1e6)&(L.wert>5000)].copy()
A["rA"]=A.pnl_A/A.vlm_A; A["rB"]=A.pnl_B/A.vlm_B
print("="*88)
print("WIE VIEL VON 'DAUERHAFT PROFITABEL' IST UEBERHAUPT MEHR ALS ZUFALL?")
print("="*88)
pa=(A.rA>0).mean(); pb=(A.rB>0).mean()
beide=((A.rA>0)&(A.rB>0)).mean()
print(f"  Konten: {len(A):,}")
print(f"  in Periode A im Plus: {pa*100:.1f} %   in B im Plus: {pb*100:.1f} %")
print(f"  in BEIDEN im Plus:    {beide*100:.1f} %   bei Unabhaengigkeit: {pa*pb*100:.1f} %")
print(f"  UEBERSCHUSS:          {(beide-pa*pb)*100:+.1f} Prozentpunkte")
print(f"\n  -> 'In beiden Perioden im Plus' ist praktisch REINER ZUFALL.")
print(f"     Meine erste Gruppeneinteilung war damit weitgehend eine Zufallsstichprobe.")
print()
for q,lab in ((0.10,"oberstes Dezil"),(0.05,"oberste 5 %"),(0.01,"oberstes Prozent")):
    ta=A.rA>=A.rA.quantile(1-q); tb=A.rB>=A.rB.quantile(1-q)
    beid=(ta&tb).mean()
    print(f"  {lab:<20} in beiden: {beid*100:>5.2f} %   Zufall: {q*q*100:>5.2f} %   "
          f"Faktor {beid/(q*q):>4.1f}x   n={int((ta&tb).sum())}")
kern=A[(A.rA>=A.rA.quantile(0.90))&(A.rB>=A.rB.quantile(0.90))]
gegen=A[(A.rA<=A.rA.quantile(0.10))&(A.rB<=A.rB.quantile(0.10))]
print(f"\n  KERNGRUPPE (beide Perioden oberstes Dezil): {len(kern)} Konten")
print(f"  GEGENGRUPPE (beide Perioden unterstes Dezil): {len(gegen)} Konten")

def profil(adr):
    body=json.dumps({"type":"userFills","user":adr,"aggregateByTime":False})
    r=subprocess.run(["curl","-sS","--max-time","30","-X","POST",
        "-H","Content-Type: application/json","-d",body,
        "https://api.hyperliquid.xyz/info"],capture_output=True)
    try:
        f=json.loads(r.stdout)
        if not isinstance(f,list) or len(f)<30: return None
    except Exception: return None
    d=pd.DataFrame(f); d["ts"]=pd.to_datetime(d.time,unit="ms",utc=True); d=d.sort_values("ts")
    h=(d.ts.max()-d.ts.min()).total_seconds()/3600
    if h<1: return None
    for c in ("px","sz","fee"): d[c]=pd.to_numeric(d[c],errors="coerce")
    return dict(pro_tag=len(f)/(h/24), taker=d.get("crossed",pd.Series([np.nan])).mean(),
                groesse=(d.px*d.sz).mean(), maerkte=d.coin.nunique(),
                gebuehr_bp=d.fee.sum()/(d.px*d.sz).sum()*1e4)

print("\n"+"="*88)
print("WIE HANDELT DIE KERNGRUPPE? (echte Fills)")
print("="*88)
out={}
for lab,grp in (("KERN (oberstes Dezil x2)",kern),("GEGEN (unterstes Dezil x2)",gegen)):
    res=[]
    for adr in grp.adr.head(60):
        p=profil(adr)
        if p: res.append(p)
        time.sleep(0.1)
    R=pd.DataFrame(res); out[lab]=R
    if not len(R): print(f"  {lab}: keine Daten"); continue
    print(f"\n  {lab}   (n={len(R)})")
    print(f"    Fills pro Tag       Median {R.pro_tag.median():>8,.0f}   "
          f"25-75 %: {R.pro_tag.quantile(.25):,.0f} - {R.pro_tag.quantile(.75):,.0f}")
    print(f"    Taker-Anteil        Median {R.taker.median()*100:>7.1f} %")
    print(f"    Ordergroesse ($)    Median {R.groesse.median():>8,.0f}")
    print(f"    Maerkte             Median {R.maerkte.median():>8,.0f}")
    print(f"    Gebuehren (bp/Vol)  Median {R.gebuehr_bp.median():>8.2f}")
    print(f"    unter 20 Fills/Tag: {(R.pro_tag<20).mean()*100:>5.1f} %")
if len(out)==2 and all(len(v) for v in out.values()):
    k,g=out["KERN (oberstes Dezil x2)"],out["GEGEN (unterstes Dezil x2)"]
    from scipy.stats import mannwhitneyu
    print("\n  Unterschiede (Mann-Whitney-U):")
    for c,lab in (("pro_tag","Fills/Tag"),("taker","Taker-Anteil"),
                  ("gebuehr_bp","Gebuehren")):
        p=mannwhitneyu(k[c].dropna(),g[c].dropna()).pvalue
        print(f"    {lab:<18} p = {p:.3f}{'   signifikant' if p<0.05 else ''}")
