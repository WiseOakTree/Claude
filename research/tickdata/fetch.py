"""Echte Footprint-Daten von Binance: jeder einzelne Trade mit Kennzeichnung,
ob der Kaeufer oder der Verkaeufer der Aggressor war.

Je Tag ~3,7 Mio Trades. Wird sofort zu 5-Minuten-Footprint-Merkmalen
verdichtet, Rohdatei danach geloescht -- sonst platzt die Platte.
"""
import os, sys, zipfile, io, subprocess
import numpy as np, pandas as pd

BASE="https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT"
TMP="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/tick"
OUT=f"{TMP}/footprint.csv"
TICK=10.0        # Preisraster fuer die Footprint-Level (BTC)
BAR="5min"

def one_day(day):
    z=f"{TMP}/d.zip"
    url=f"{BASE}/BTCUSDT-aggTrades-{day}.zip"
    rc=subprocess.run(["curl","-sS","-f","--max-time","300","-o",z,url],
                      capture_output=True)
    if rc.returncode!=0 or not os.path.exists(z): return None
    try:
        with zipfile.ZipFile(z) as zf:
            name=zf.namelist()[0]
            df=pd.read_csv(zf.open(name),usecols=["price","quantity",
                    "transact_time","is_buyer_maker"],
                    dtype={"price":"float64","quantity":"float64",
                           "transact_time":"int64","is_buyer_maker":"bool"})
    except Exception as e:
        os.remove(z); return None
    os.remove(z)
    if len(df)<1000: return None

    df["ts"]=pd.to_datetime(df.transact_time,unit="ms",utc=True)
    df["bar"]=df.ts.dt.floor(BAR)
    # is_buyer_maker == True  -> der VERKAEUFER war aggressiv
    df["buy"]=(~df.is_buyer_maker)*df.quantity
    df["sell"]=(df.is_buyer_maker)*df.quantity
    df["lvl"]=np.round(df.price/TICK)*TICK

    g=df.groupby("bar")
    base=pd.DataFrame({
        "open":  g.price.first(), "high": g.price.max(),
        "low":   g.price.min(),   "close":g.price.last(),
        "vol":   g.quantity.sum(),"n":    g.size(),
        "buy":   g.buy.sum(),     "sell": g.sell.sum(),
    })
    base["delta"]=base.buy-base.sell
    base["avg_size"]=base.vol/base.n

    # Grosse gegen kleine Trades -- das, was 5-Minuten-Bars NICHT hergeben
    q99=df.quantity.quantile(0.99); q50=df.quantity.quantile(0.50)
    big=df[df.quantity>=q99]; small=df[df.quantity<=q50]
    base["delta_big"]=(big.groupby("bar").buy.sum()-big.groupby("bar").sell.sum()).reindex(base.index).fillna(0)
    base["vol_big"]=big.groupby("bar").quantity.sum().reindex(base.index).fillna(0)
    base["delta_small"]=(small.groupby("bar").buy.sum()-small.groupby("bar").sell.sum()).reindex(base.index).fillna(0)

    # Footprint je Preislevel -> gestapelte Ungleichgewichte (3:1 diagonal)
    lv=df.groupby(["bar","lvl"])[["buy","sell"]].sum().reset_index()
    lv=lv.sort_values(["bar","lvl"])
    lv["sell_below"]=lv.groupby("bar").sell.shift(1)
    lv["buy_above"] =lv.groupby("bar").buy.shift(-1)
    imb_buy =(lv.buy  >= 3*lv.sell_below.replace(0,np.nan)).astype(float)
    imb_sell=(lv.sell >= 3*lv.buy_above .replace(0,np.nan)).astype(float)
    lv["ib"]=imb_buy.fillna(0); lv["is_"]=imb_sell.fillna(0)
    agg=lv.groupby("bar").agg(imb_buy=("ib","sum"),imb_sell=("is_","sum"))
    base=base.join(agg).fillna({"imb_buy":0,"imb_sell":0})

    # Bar-POC: wo im Bar lag das meiste Volumen (0 = Tief, 1 = Hoch)
    lv["tot"]=lv.buy+lv.sell
    pocidx=lv.groupby("bar").tot.idxmax()
    base["poc"]=lv.loc[pocidx].set_index("bar").lvl.reindex(base.index)
    rng=(base.high-base.low).replace(0,np.nan)
    base["poc_pos"]=((base.poc-base.low)/rng).clip(0,1)

    # Absorption: viel Volumen, wenig Bewegung
    base["absorb"]=base.vol/ (np.abs(base.close/base.open-1)*1e4 + 1.0)
    return base.reset_index()

if __name__=="__main__":
    days=pd.date_range(sys.argv[1],sys.argv[2],freq=f"{sys.argv[3]}D").strftime("%Y-%m-%d")
    first = not os.path.exists(OUT)
    done=set()
    if not first:
        try: done=set(pd.read_csv(OUT,usecols=["bar"]).bar.str[:10].unique())
        except Exception: pass
    for i,d in enumerate(days):
        if d in done: continue
        r=one_day(d)
        if r is None:
            print(f"  {d}: nicht verfuegbar",flush=True); continue
        r.to_csv(OUT,mode="a",header=first,index=False); first=False
        print(f"  {d}: {len(r):>4} Bars, {r.n.sum():>9,} Trades",flush=True)
