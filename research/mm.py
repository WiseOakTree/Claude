"""Liquiditaet STELLEN statt nehmen -- an echten Trades simuliert.

Modell: Ich stelle passiv Bid und Ask je delta Basispunkte um den letzten
Preis. Ein aggressiver Kaeufer, der auf oder ueber meinem Ask handelt,
fuellt mein Ask (ich werde short). Ein aggressiver Verkaeufer auf oder
unter meinem Bid fuellt mein Bid (ich werde long).

Danach messe ich, was der Preis TUT -- das ist die adverse Selektion,
die jeden naiven Market Maker toetet.
"""
import warnings; warnings.filterwarnings("ignore")
import os,subprocess,zipfile,sys
import numpy as np, pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
B="https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT"

def hole(tag):
    z=f"{T}/mm.zip"
    r=subprocess.run(["curl","-sS","-f","--max-time","300","-o",z,
                      f"{B}/BTCUSDT-aggTrades-{tag}.zip"],capture_output=True)
    if r.returncode!=0: return None
    try:
        with zipfile.ZipFile(z) as zf:
            d=pd.read_csv(zf.open(zf.namelist()[0]),
                usecols=["price","quantity","transact_time","is_buyer_maker"],
                dtype={"price":"float64","quantity":"float64",
                       "transact_time":"int64","is_buyer_maker":"bool"})
    except Exception: os.remove(z); return None
    os.remove(z); return d

def simuliere(d, delta_bp, horizont_ms, maker_fee_bp):
    """delta_bp: wie weit vom letzten Preis ich quote.
       horizont_ms: wie lange ich die Position halte, bevor ich bewerte."""
    p=d.price.to_numpy(); t=d.transact_time.to_numpy()
    aggressiv_kauf=~d.is_buyer_maker.to_numpy()      # Kaeufer war Taker
    n=len(p)
    ref=pd.Series(p).shift(1).to_numpy()             # letzter Preis vor dem Trade
    ask=ref*(1+delta_bp/1e4); bid=ref*(1-delta_bp/1e4)
    fill_ask=aggressiv_kauf&(p>=ask)                 # mein Ask wird getroffen -> short
    fill_bid=(~aggressiv_kauf)&(p<=bid)              # mein Bid wird getroffen -> long
    idx_a=np.where(fill_ask)[0]; idx_b=np.where(fill_bid)[0]
    # Preis nach horizont_ms
    ziel=np.searchsorted(t,t+horizont_ms)
    ziel=np.minimum(ziel,n-1)
    p_spaeter=p[ziel]
    # Ergebnis je Fill, in Basispunkten
    # Short auf dem Ask: ich verkaufe zu ask, spaeter zurueck zu p_spaeter
    r_a=(ask[idx_a]/p_spaeter[idx_a]-1)*1e4 - maker_fee_bp
    # Long auf dem Bid
    r_b=(p_spaeter[idx_b]/bid[idx_b]-1)*1e4 - maker_fee_bp
    alle=np.concatenate([r_a,r_b])
    return dict(fills=len(alle), bp=alle.mean() if len(alle) else np.nan,
                bp_ask=r_a.mean() if len(r_a) else np.nan,
                bp_bid=r_b.mean() if len(r_b) else np.nan,
                anteil=len(alle)/n*100)

TAGE=["2026-03-10","2026-05-19","2026-06-24","2026-07-15","2026-08-02"]
daten=[]
for tag in TAGE:
    d=hole(tag)
    if d is None: print(f"  {tag}: n/a",flush=True); continue
    daten.append((tag,d)); print(f"  {tag}: {len(d):,} Trades",flush=True)

print("\n"+"="*96)
print("PASSIV QUOTEN: was verdient man, was frisst die adverse Selektion?")
print("Maker-Gebuehr 1,5 bp (Hyperliquid/Binance-Standard)")
print("="*96)
print(f"{'Quote-Abstand':>15}{'Halten':>9}{'Fills/Tag':>12}{'bp je Fill':>13}"
      f"{'davon Ask':>12}{'davon Bid':>12}")
for delta in (0.5,1,2,5,10,25):
    for hor,hl in ((1000,"1 s"),(60000,"1 min"),(600000,"10 min")):
        res=[simuliere(d,delta,hor,1.5) for _,d in daten]
        R=pd.DataFrame(res)
        if R.fills.sum()<100: continue
        print(f"{delta:>13.1f} bp{hl:>9}{R.fills.mean():>12,.0f}{R.bp.mean():>+12.2f}"
              f"{R.bp_ask.mean():>+12.2f}{R.bp_bid.mean():>+12.2f}")
    print()
