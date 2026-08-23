"""GAMMA EXPOSURE: die vier Behauptungen des GEX-Indikators geprueft.

Aufbau nach docs/gex_spec.md -- vor der Rechnung festgelegt.

Datenlage: Binance Options EOHSummary, stuendlich, 2023-05-18 bis 2023-10-23,
147 Tage. Gamma kommt von der Boerse, nicht aus eigener Rechnung.
"""
import sys, warnings
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats

S = "/tmp/claude-0/-home-user/6ea4b953-8381-58a1-a843-0b428058fee5/scratchpad/"
E, V = S + "eoh/", S + "vol/"
MAERKTE = ["btc", "eth"]
ALPHA = 0.05 / 4          # Bonferroni fuer vier Behauptungen
STUNDE = 8                # eine Beobachtung je Tag (Deribit-Verfallszeit)


def lade(sym):
    g = pd.read_csv(E + f"gex_{sym}.csv", index_col=0, parse_dates=True)
    px = pd.read_csv(V + f"{sym}_1h.csv", index_col=0, parse_dates=True)
    px = px.reindex(g.index)
    d = g.join(px[["open", "high", "low", "close"]])
    r = np.log(d["close"]).diff()
    # Realisierte Vol der naechsten 24 h (annualisiert), und die Vergangenheit
    d["rv_next"] = r.shift(-1).rolling(24).std().shift(-23) * np.sqrt(24 * 365) * 100
    d["rv_past"] = r.rolling(24).std() * np.sqrt(24 * 365) * 100
    d["ret_next"] = d["close"].shift(-24) / d["close"] - 1
    d["ret_past"] = d["close"] / d["close"].shift(24) - 1
    # GEX auf das Open Interest normiert -- sonst dominiert der Bestandsaufbau
    d["gex_norm"] = d["net_gex"] / d["abs_gex"]
    d["ueber_flip"] = np.nan     # wird in B4 gefuellt
    return d.dropna(subset=["net_gex", "close"])


def tages(d):
    """Nicht ueberlappende Tagesbeobachtungen -- nur darauf wird getestet."""
    return d[d.index.hour == STUNDE].dropna(subset=["rv_next", "gex_norm"])


def spearman(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 10:
        return np.nan, np.nan, int(m.sum())
    rho, p = stats.spearmanr(x[m], y[m])
    return rho, p, int(m.sum())


def haelften(d):
    mitte = d.index[len(d) // 2]
    return d[d.index < mitte], d[d.index >= mitte]


def urteil(werte, erwartet_negativ, ps):
    """Vorzeichen wie erwartet, signifikant, in beiden Haelften und Maerkten."""
    vz = all((v < 0) == erwartet_negativ for v in werte if np.isfinite(v))
    sig = any(p < ALPHA for p in ps if np.isfinite(p))
    return "BESTAETIGT" if (vz and sig) else "nicht bestaetigt"


print("=" * 96)
print("DATENLAGE")
print("=" * 96)
daten = {}
for sym in MAERKTE:
    d = lade(sym)
    daten[sym] = d
    t = tages(d)
    print(f"  {sym.upper()}: {len(d)} Stunden, {len(t)} Tagesbeobachtungen, "
          f"{d.index.min():%Y-%m-%d} .. {d.index.max():%Y-%m-%d}")
    print(f"        Net GEX negativ in {(d['net_gex']<0).mean()*100:5.1f} % der Stunden, "
          f"Median |GEX| {d['abs_gex'].median()/1e6:.1f} M$, "
          f"Ø {d['n_strikes'].mean():.0f} Strikes")

# ── B1: Negatives Gamma -> mehr Volatilitaet ─────────────────────────────
print("\n" + "=" * 96)
print("B1  Negatives Gamma verstaerkt die Volatilitaet")
print("=" * 96)
print(f"{'Markt':6s} {'Stichprobe':16s} {'Spearman':>9s} {'p':>9s} {'n':>6s}   Erwartung: rho < 0")
print("-" * 96)
b1_r, b1_p = [], []
for sym in MAERKTE:
    d, t = daten[sym], tages(daten[sym])
    r_h, p_h, n_h = spearman(d["gex_norm"].to_numpy(), d["rv_next"].to_numpy())
    print(f"{sym.upper():6s} {'stuendlich':16s} {r_h:9.3f} {p_h:9.4f} {n_h:6d}   (ueberlappend, nur beschreibend)")
    r_t, p_t, n_t = spearman(t["gex_norm"].to_numpy(), t["rv_next"].to_numpy())
    print(f"{sym.upper():6s} {'TAGESDATEN':16s} {r_t:9.3f} {p_t:9.4f} {n_t:6d}   <- hierauf wird geurteilt")
    b1_r.append(r_t); b1_p.append(p_t)
    for name, h in zip(("1. Haelfte", "2. Haelfte"), haelften(t)):
        r_x, p_x, n_x = spearman(h["gex_norm"].to_numpy(), h["rv_next"].to_numpy())
        print(f"{'':6s} {name:16s} {r_x:9.3f} {p_x:9.4f} {n_x:6d}")
        b1_r.append(r_x)
print(f"\n  Urteil B1: {urteil(b1_r, True, b1_p)}")

print("\n  Realisierte Vol der naechsten 24 h nach GEX-Quintil (Tagesdaten, %):")
print(f"  {'Quintil':10s} " + "  ".join(f"{s.upper():>12s}" for s in MAERKTE))
for q in range(5):
    zeile = f"  {q+1}. ({'niedrigstes GEX' if q==0 else 'hoechstes GEX' if q==4 else ''})"[:12].ljust(12)
    werte = []
    for sym in MAERKTE:
        t = tages(daten[sym])
        qs = pd.qcut(t["gex_norm"], 5, labels=False, duplicates="drop")
        werte.append(t["rv_next"][qs == q].mean())
    print(zeile + "  ".join(f"{w:12.1f}" for w in werte))
for sym in MAERKTE:
    t = tages(daten[sym])
    neg, pos = t[t["net_gex"] < 0]["rv_next"], t[t["net_gex"] >= 0]["rv_next"]
    if len(neg) > 5 and len(pos) > 5:
        u, p = stats.mannwhitneyu(neg, pos, alternative="greater")
        print(f"  {sym.upper()}: Vol bei negativem GEX {neg.mean():.1f} % gegen "
              f"{pos.mean():.1f} % bei positivem (n={len(neg)}/{len(pos)}), "
              f"Mann-Whitney p = {p:.4f}")

# ── B2: Positives Gamma -> Mean-Reversion ────────────────────────────────
print("\n" + "=" * 96)
print("B2  Positives Gamma bringt Mean-Reversion, negatives Trend")
print("=" * 96)
print(f"{'Markt':6s} {'Regime':22s} {'corr(ret-24h, ret+24h)':>24s} {'p':>9s} {'n':>6s}")
print("-" * 96)
b2 = []
for sym in MAERKTE:
    t = tages(daten[sym]).dropna(subset=["ret_past", "ret_next"])
    for name, teil in (("positives Gamma", t[t["net_gex"] >= 0]),
                       ("negatives Gamma", t[t["net_gex"] < 0])):
        r, p, n = spearman(teil["ret_past"].to_numpy(), teil["ret_next"].to_numpy())
        print(f"{sym.upper():6s} {name:22s} {r:24.3f} {p:9.4f} {n:6d}")
        b2.append((sym, name, r, p))
erw = ("Erwartung: bei positivem Gamma rho < 0 (Umkehr), "
       "bei negativem rho > 0 (Fortsetzung)")
print(f"\n  {erw}")
ok_pos = all(r < 0 for s, n_, r, p in b2 if n_.startswith("positives") and np.isfinite(r))
ok_neg = all(r > 0 for s, n_, r, p in b2 if n_.startswith("negatives") and np.isfinite(r))
sig = any(p < ALPHA for _, _, _, p in b2 if np.isfinite(p))
print(f"  Urteil B2: {'BESTAETIGT' if (ok_pos and ok_neg and sig) else 'nicht bestaetigt'}"
      f"  (Vorzeichen positiv-Regime {'ok' if ok_pos else 'falsch'}, "
      f"negativ-Regime {'ok' if ok_neg else 'falsch'}, "
      f"{'ein p unter der Schwelle' if sig else 'kein p unter der Schwelle'})")

# ── B3: Walls als Widerstand/Unterstuetzung, gegen Zufallsstrike ─────────
print("\n" + "=" * 96)
print("B3  Call-Wall / Put-Wall wirken -- gegen Kontrolle: Zufallsstrike gleicher Distanz")
print("=" * 96)
print(f"{'Markt':6s} {'Level':12s} {'Beruehrungen':>13s} {'Umkehr %':>9s} "
      f"{'Kontrolle %':>12s} {'Differenz':>10s} {'p':>8s}")
print("-" * 96)
rng = np.random.default_rng(42)
b3 = []
for sym in MAERKTE:
    d = daten[sym]
    strikes = pd.read_csv(E + f"gex_strikes_{sym}.csv", parse_dates=["t"])
    alle_k = {t_: grp["k"].to_numpy() for t_, grp in strikes.groupby("t")}
    hoch, tief, close = d["high"].to_numpy(), d["low"].to_numpy(), d["close"].to_numpy()
    idx = d.index
    for level_name, spalte in (("Call-Wall", "call_wall"), ("Put-Wall", "put_wall")):
        lv = d[spalte].to_numpy()
        echt, kontr = [], []
        for i in range(len(d) - 24):
            L = lv[i]
            if not np.isfinite(L):
                continue
            # Beruehrung in den naechsten 24 h?
            j0, j1 = i + 1, i + 25
            beruehrt = (hoch[j0:j1] >= L).any() and (tief[j0:j1] <= L).any() \
                if False else ((hoch[j0:j1] >= L) & (tief[j0:j1] <= L)).any()
            if not beruehrt:
                continue
            # Umkehr = Kurs 24 h nach der Beruehrung auf der Ausgangsseite
            oben_vorher = close[i] > L
            zurueck = (close[min(i + 48, len(d) - 1)] > L) == oben_vorher
            echt.append(zurueck)
            # Kontrolle: zufaelliger anderer Strike, aehnliche Distanz
            ks = alle_k.get(idx[i])
            if ks is not None and len(ks) > 3:
                dist = abs(L - close[i])
                kand = ks[(np.abs(np.abs(ks - close[i]) - dist) < dist * 0.5) & (ks != L)]
                if len(kand):
                    K = float(rng.choice(kand))
                    ber_k = ((hoch[j0:j1] >= K) & (tief[j0:j1] <= K)).any()
                    if ber_k:
                        ob = close[i] > K
                        kontr.append((close[min(i + 48, len(d) - 1)] > K) == ob)
        if len(echt) > 20 and len(kontr) > 20:
            pe, pk = np.mean(echt), np.mean(kontr)
            tab = [[sum(echt), len(echt) - sum(echt)], [sum(kontr), len(kontr) - sum(kontr)]]
            _, p = stats.fisher_exact(tab)
            print(f"{sym.upper():6s} {level_name:12s} {len(echt):13d} {pe*100:8.1f}% "
                  f"{pk*100:11.1f}% {(pe-pk)*100:+9.1f} pp {p:8.4f}")
            b3.append((pe - pk, p))
sig3 = any(p < ALPHA for _, p in b3)
pos3 = all(dd > 0 for dd, _ in b3)
print(f"\n  Urteil B3: {'BESTAETIGT' if (sig3 and pos3) else 'nicht bestaetigt'}")

# ── B4: Der Gamma-Flip trennt die Regime ─────────────────────────────────
print("\n" + "=" * 96)
print("B4  Ober-/unterhalb des Gamma-Flip unterscheiden sich die Regime")
print("=" * 96)
print("  Naeherung: das Vorzeichen des Net GEX IST die Regime-Trennung, die der")
print("  Flip geometrisch markiert. Geprueft wird deshalb, ob der Wechsel des")
print("  Vorzeichens eine Vol-Aenderung ankuendigt.")
print(f"\n{'Markt':6s} {'Ereignis':28s} {'n':>5s} {'Vol davor':>10s} {'Vol danach':>11s} {'p':>9s}")
print("-" * 96)
b4 = []
for sym in MAERKTE:
    t = tages(daten[sym])
    vz = np.sign(t["net_gex"].to_numpy())
    wechsel_ab = (vz[1:] < 0) & (vz[:-1] >= 0)
    wechsel_auf = (vz[1:] >= 0) & (vz[:-1] < 0)
    for name, maske in (("Flip nach NEGATIV", wechsel_ab), ("Flip nach POSITIV", wechsel_auf)):
        i = np.where(maske)[0] + 1
        if len(i) < 8:
            print(f"{sym.upper():6s} {name:28s} {len(i):5d}   zu wenige Ereignisse")
            continue
        davor = t["rv_past"].to_numpy()[i]
        danach = t["rv_next"].to_numpy()[i]
        m = np.isfinite(davor) & np.isfinite(danach)
        _, p = stats.wilcoxon(danach[m], davor[m]) if m.sum() > 5 else (np.nan, np.nan)
        print(f"{sym.upper():6s} {name:28s} {int(m.sum()):5d} {np.mean(davor[m]):9.1f}% "
              f"{np.mean(danach[m]):10.1f}% {p:9.4f}")
        b4.append((name, np.mean(danach[m]) - np.mean(davor[m]), p))
neg_hoch = all(dd > 0 for n_, dd, p in b4 if "NEGATIV" in n_)
sig4 = any(p < ALPHA for _, _, p in b4 if np.isfinite(p))
print(f"\n  Urteil B4: {'BESTAETIGT' if (neg_hoch and sig4) else 'nicht bestaetigt'}")
print("\nFERTIG")
