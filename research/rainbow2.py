"""Zwei Fragen zum Rainbow Chart:
1. Wie viele UNABHAENGIGE Beobachtungen stecken hinter dem Ein-Jahres-Effekt?
2. Wie stabil ist die Trendlinie selbst?
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
T="/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/rb"
K=pd.read_csv(f"{T}/btc_d.csv",parse_dates=["ts"]).set_index("ts")
K["close"]=pd.to_numeric(K.close)
lx=np.log(np.arange(1,len(K)+1)); ly=np.log(K.close.to_numpy())

print("="*92)
print("1. WIE STABIL IST DIE TRENDLINIE? (Exponent b, nur mit Daten bis zum Stichtag)")
print("="*92)
print(f"{'Stand':<12}{'Tage':>7}{'Exponent b':>13}{'implizierter Preis in 1 Jahr':>32}")
for jahr in range(2019,2027):
    t=(K.index<pd.Timestamp(f"{jahr}-01-01",tz="UTC")).sum()
    if t<500: continue
    b,a=np.polyfit(lx[:t],ly[:t],1)
    zukunft=np.exp(a+b*np.log(t+365))
    print(f"{jahr}-01-01{'':<3}{t:>7}{b:>13.3f}{zukunft:>28,.0f} $")
b_end,a_end=np.polyfit(lx,ly,1)
print(f"{'heute':<12}{len(K):>7}{b_end:>13.3f}{np.exp(a_end+b_end*np.log(len(K)+365)):>28,.0f} $")
print(f"\n  Der Exponent ist von {np.polyfit(lx[:(K.index<pd.Timestamp('2019-01-01',tz='UTC')).sum()],ly[:(K.index<pd.Timestamp('2019-01-01',tz='UTC')).sum()],1)[0]:.3f} "
      f"auf {b_end:.3f} gefallen.")
print("  Die 'Regenbogen'-Mitte wird also laufend nach unten korrigiert --")
print("  jede alte Prognose sah damals hoeher aus als das, was eintrat.")

print("\n"+"="*92)
print("2. WIE VIELE UNABHAENGIGE BEOBACHTUNGEN? (Ein-Jahres-Fenster)")
print("="*92)
jahre=len(K)/365.25
print(f"  Zeitraum:                 {jahre:.1f} Jahre")
print(f"  taegliche Beobachtungen:  {len(K)-365:,}")
print(f"  davon UNABHAENGIG:        {jahre-1:.0f}   (Ein-Jahres-Fenster ueberlappen 365-fach)")
print(f"  BTC-Zyklen im Zeitraum:   2   (2018-2021 und 2022-2025)")
print()
# Effekt mit korrekter effektiver Stichprobe
MIN=365*2
bandB=np.full(len(K),np.nan)
for t in range(MIN,len(K)):
    bb,aa=np.polyfit(lx[:t],ly[:t],1)
    r=ly[:t]-(aa+bb*lx[:t])
    bandB[t]=((ly[t]-(aa+bb*lx[t]))-r.mean())/r.std()
c=K.close.to_numpy(); H=365
f=np.full(len(c),np.nan); f[:-H]=c[H:]/c[:-H]-1
m=np.isfinite(bandB)&np.isfinite(f)
x=bandB[m]; y=f[m]
q=pd.qcut(pd.Series(x),5,labels=False,duplicates="drop")
lo=pd.Series(y)[q==0]; hi=pd.Series(y)[q==4]
diff=np.concatenate([lo.to_numpy(),-hi.to_numpy()])
n_eff=len(diff)/H
t_naiv=diff.mean()/(diff.std(ddof=1)/np.sqrt(len(diff)))
t_korr=diff.mean()/(diff.std(ddof=1)/np.sqrt(max(n_eff,2)))
print(f"  Effekt (unten long, oben short): {diff.mean()*100:+.1f} %")
print(f"  t OHNE Ueberlappungskorrektur:   {t_naiv:>6.2f}   (n = {len(diff)})")
print(f"  t MIT  Ueberlappungskorrektur:   {t_korr:>6.2f}   (n_eff = {n_eff:.1f})")
print(f"\n  -> Mit {n_eff:.0f} effektiven Beobachtungen ist nichts beweisbar.")

print("\n"+"="*92)
print("3. WAS BLEIBT NACH ABZUG DES REINEN AUFWAERTSTRENDS?")
print("="*92)
# Kontrolle: dieselbe Auswertung, aber Bandposition durch Zufall ersetzt
rng=np.random.default_rng(5)
echte=diff.mean()*100
zs=[]
for _ in range(500):
    xs=np.roll(x,rng.integers(200,len(x)-200))
    qq=pd.qcut(pd.Series(xs),5,labels=False,duplicates="drop")
    l2=pd.Series(y)[qq==0]; h2=pd.Series(y)[qq==4]
    zs.append(np.concatenate([l2.to_numpy(),-h2.to_numpy()]).mean()*100)
zs=np.array(zs)
print(f"  echt: {echte:+.1f} %   verschobenes Band: Median {np.median(zs):+.1f} %   "
      f"5-95 %: {np.percentile(zs,5):+.0f} .. {np.percentile(zs,95):+.0f} %")
print(f"  p (einseitig) = {(zs>=echte).mean():.3f}")
