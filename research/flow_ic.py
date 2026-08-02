"""Orderflow-Ungleichgewicht: Vorhersagekraft gegen die Kostenschwelle."""
import numpy as np, pandas as pd
from scipy import stats

OUT = "/tmp/claude-0/-home-user-Claude/15d15817-1e32-5d20-88a2-91c5ca4d5da2/scratchpad/of/"
df = pd.read_csv(OUT + "flow_5m.csv.gz", index_col=0, parse_dates=True)
df = df[df["volume"] > 0].copy()

# Orderflow-Ungleichgewicht: (Kaeufer-aggressiv - Verkaeufer-aggressiv) / Gesamt
df["ofi"] = (2 * df["taker_base"] - df["volume"]) / df["volume"]
df["ofi_z"] = (df["ofi"] - df["ofi"].rolling(288).mean()) / df["ofi"].rolling(288).std()
# volumengewichtet ueber 12 Bars (1h) -- glaettet das Rauschen
df["ofi_1h"] = ((2 * df["taker_base"] - df["volume"]).rolling(12).sum()
                / df["volume"].rolling(12).sum())
df["ret"] = df["close"].pct_change()
df["dollar"] = df["quote_volume"]
COST_BP = 16.0

print("=" * 82)
print(f"Orderflow-Vorhersagekraft   n = {len(df):,} 5-Minuten-Bars "
      f"({df.index.min().date()} .. {df.index.max().date()})")
print("=" * 82)
print(f"{'Signal':22s} {'Horizont':>10s} {'IC':>8s} {'p':>10s} "
      f"{'Q5-Q1 Spread':>14s} {'vs 16bp':>9s}")
print("-" * 82)
for nm, sig in (("OFI (5 min)", df["ofi"]),
                ("OFI z-Score (1 Tag)", df["ofi_z"]),
                ("OFI geglaettet (1 h)", df["ofi_1h"])):
    for bars, lbl in ((1, "5 min"), (3, "15 min"), (12, "1 h"), (48, "4 h")):
        fwd = df["close"].pct_change(bars).shift(-bars)
        m = pd.concat([sig.rename("s"), fwd.rename("f")], axis=1).dropna()
        if len(m) < 1000: continue
        ic, p = stats.spearmanr(m["s"], m["f"])
        q = pd.qcut(m["s"], 5, labels=False, duplicates="drop")
        spread = (m["f"][q == 4].mean() - m["f"][q == 0].mean()) * 1e4
        verdict = "handelbar" if abs(spread) > COST_BP else f"{abs(spread)/COST_BP:.2f}x"
        print(f"{nm:22s} {lbl:>10s} {ic:+8.3f} {p:10.2e} {spread:+11.2f} bp {verdict:>9s}")

print("\n" + "=" * 82)
print("Der entscheidende Vergleich")
print("=" * 82)
fwd = df["close"].pct_change(1).shift(-1)
m = pd.concat([df["ofi"].rename("s"), fwd.rename("f")], axis=1).dropna()
q = pd.qcut(m["s"], 10, labels=False, duplicates="drop")
best = max(abs(m["f"][q == 9].mean()), abs(m["f"][q == 0].mean())) * 1e4
print(f"  Staerkstes Dezil-Signal (5 min):        {best:6.2f} bp")
print(f"  Kostenschwelle je Roundtrip:            {COST_BP:6.2f} bp")
print(f"  Verhaeltnis:                            {best/COST_BP:6.2f}x  "
      f"-> {'reicht' if best > COST_BP else 'reicht NICHT'}")
print(f"\n  Typische 5-Minuten-Bewegung (Std):      {df['ret'].std()*1e4:6.2f} bp")
print(f"  Trades noetig fuer +10 % bei {best:.1f} bp:  {int(0.10/max(best/1e4,1e-9)):,}")
