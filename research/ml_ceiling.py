"""Was koennte ML hoechstens bringen? Orakel-Modelle als Obergrenze.

Zeitkonvention (der Fehler im ersten Anlauf):
  sig[t]  = Prognose fuer die Rendite von t nach t+1, bekannt am Ende von t
  pos[t]  = daraus abgeleitete Position, gehalten waehrend t+1
  pnl[t+1]= pos[t] * ret[t+1] - Kosten * |pos[t] - pos[t-1]|
=> in pandas: pos.shift(1) * ret
"""
import numpy as np, pandas as pd

V = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/vol/"
px = pd.read_csv(V+"btc_1h.csv", index_col=0, parse_dates=True)["close"].resample("1D").last().dropna()
dvol = pd.read_csv(V+"dvol_BTC.csv", index_col=0, parse_dates=True)["close"].resample("1D").last()
ret = px.pct_change().fillna(0)
logr = np.log(px).diff()
COST = 16e-4

def challenge(r, win=90):
    r = r.dropna().to_numpy(); passed=tot=0; R=[];DD=[]
    for s in range(0,len(r)-win):
        w=r[s:s+win]; eq=np.cumprod(1+w); dd=(eq/np.maximum.accumulate(eq)-1).min()
        passed += (eq[-1]-1>=.10 and dd>=-.06 and w.min()>-.03); tot+=1
        R.append(eq[-1]-1); DD.append(-dd)
    if not tot: return 0,0,0
    return passed/tot*100, np.median(R)*100, np.median(DD)*100

def pnl_from_pos(pos):
    """pos[t] wird waehrend t+1 gehalten."""
    held = pos.shift(1)
    return held*ret - COST*held.diff().abs().fillna(0)

trail    = logr.rolling(30).std()*np.sqrt(365)*100
implied  = dvol.reindex(px.index).ffill()
oracle_v = logr.shift(-1).rolling(30).std().shift(-29)*np.sqrt(365)*100   # perfekt

print("="*82)
print("A) Obergrenze fuer ML in der VOLATILITAETSPROGNOSE (long-only, Sizing)")
print("="*82)
print(f"{'Schaetzer':34s} {'Ziel':>6s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*70)
for nm, est in (("trailing 30T (heute genutzt)", trail),
                ("DVOL implizit (Markt)", implied),
                ("ORAKEL: perfekte Vol-Prognose", oracle_v)):
    best = None
    for tgt in (10, 12, 15, 18, 20, 25):
        pos = (tgt/est).clip(upper=2.0)
        p,m,d = challenge(pnl_from_pos(pos).loc[est.dropna().index])
        if best is None or p > best[0]: best = (p,m,d,tgt)
    p,m,d,tgt = best
    print(f"{nm:34s} {tgt:5d}% {m:+8.1f}% {d:6.1f}% {p:6.1f}%")

print("\n"+"="*82)
print("B) Obergrenze fuer ML in der RICHTUNGSPROGNOSE")
print("="*82)
print(f"{'Trefferquote (Rest zufaellig falsch)':34s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*70)
rng = np.random.default_rng(11)
truth = np.sign(ret.shift(-1)).fillna(0)          # Vorzeichen von t -> t+1
size  = (15.0/trail).clip(upper=2.0).fillna(0)
for acc in (0.50, 0.52, 0.55, 0.60, 0.70, 0.80, 1.00):
    ps = []
    for seed in range(5):                          # mehrere Ziehungen mitteln
        rg = np.random.default_rng(100+seed)
        flip = rg.random(len(truth)) > acc
        sig = pd.Series(np.where(flip, -truth, truth), index=truth.index)
        p,m,d = challenge(pnl_from_pos(sig*size))
        ps.append((p,m,d))
    p,m,d = np.mean(ps, axis=0)
    tag = "  <- reiner Zufall" if acc==.50 else ("  <- perfekt" if acc==1.0 else "")
    print(f"{f'{acc*100:.0f} % richtig':34s} {m:+8.1f}% {d:6.1f}% {p:6.1f}%{tag}")

print("\n"+"="*82)
print("C) Long-only-Orakel (nur aussteigen, wenn es faellt -- weniger Umsatz)")
print("="*82)
print(f"{'Trefferquote':34s} {'Rendite':>9s} {'DD':>7s} {'Pass':>7s}")
print("-"*70)
for acc in (0.50, 0.55, 0.60, 0.70, 1.00):
    ps=[]
    for seed in range(5):
        rg = np.random.default_rng(200+seed)
        flip = rg.random(len(truth)) > acc
        sig = pd.Series(np.where(flip, -truth, truth), index=truth.index)
        pos = (sig > 0).astype(float)*size          # long oder flat, nie short
        ps.append(challenge(pnl_from_pos(pos)))
    p,m,d = np.mean(ps, axis=0)
    print(f"{f'{acc*100:.0f} % richtig':34s} {m:+8.1f}% {d:6.1f}% {p:6.1f}%")
