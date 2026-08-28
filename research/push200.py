"""200-$-PUSH auf dem 15-min-Chart, 1 Trade pro Tag.

Aufbau nach docs/push200_spec.md -- vor der Rechnung festgelegt.
Kostenmodell aus einem echten Trade des Nutzers: 4 bp je Seite.
"""
import sys, os, warnings, pickle
sys.path.insert(0, "/home/user/Claude/src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats

S = "/tmp/claude-0/-home-user/6ea4b953-8381-58a1-a843-0b428058fee5/scratchpad/"
V = S + "vol/"
GRENZE = pd.Timestamp("2025-01-01", tz="UTC")

# Kosten in Anteilen (aus dem echten Trade abgeleitet)
KOSTEN = {
    "gemessen": dict(ein=0.0004, ziel=0.0004, stop=0.0006, ende=0.0004),
    "taker16":  dict(ein=0.0008, ziel=0.0008, stop=0.0010, ende=0.0008),
    "brutto":   dict(ein=0.0,    ziel=0.0,    stop=0.0,    ende=0.0),
}


def lade(sym, tf="15m"):
    df = pd.read_csv(V + f"{sym}_{tf}.csv", index_col=0, parse_dates=True)
    df["tag"] = df.index.floor("1D")
    return df


def trades(df, push, ziel, stop, richtung=1, prozent=False, kosten="gemessen"):
    """Ein Trade je Tag: erster Push vom Tagesstart, dann Klammer bis Tagesschluss.

    ``push``/``ziel``/``stop`` in $ (oder als Anteil, wenn ``prozent``).
    ``richtung`` +1 = mit dem Push (Momentum), -1 = dagegen (Fade).
    """
    k = KOSTEN[kosten]
    o = df["open"].to_numpy(float); h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float);  c = df["close"].to_numpy(float)
    tage = df["tag"].to_numpy()
    grenzen = np.flatnonzero(np.r_[True, tage[1:] != tage[:-1]])
    grenzen = np.r_[grenzen, len(df)]
    out = []
    for g in range(len(grenzen) - 1):
        a, b = grenzen[g], grenzen[g + 1]
        if b - a < 8:
            continue
        start = o[a]
        p_abs = start * push if prozent else push
        z_abs = start * ziel if prozent else ziel
        s_abs = start * stop if prozent else stop
        # 1) Ausloeser: erste Kerze, die p_abs vom Tagesstart entfernt schliesst
        weg = c[a:b] - start
        tr = np.flatnonzero(np.abs(weg) >= p_abs)
        if len(tr) == 0 or a + tr[0] >= b - 1:
            continue
        i = a + tr[0]
        seite = int(np.sign(weg[tr[0]])) * richtung
        if seite == 0:
            continue
        entry = c[i]
        tp = entry + seite * z_abs
        sl = entry - seite * s_abs
        # 2) Klammer bis Tagesschluss -- Stop zaehlt vor Ziel (pessimistisch)
        grund, exitp, bars = "ende", c[b - 1], b - 1 - i
        for j in range(i + 1, b):
            stop_hit = (l[j] <= sl) if seite == 1 else (h[j] >= sl)
            ziel_hit = (h[j] >= tp) if seite == 1 else (l[j] <= tp)
            if stop_hit:
                grund, exitp, bars = "stop", sl, j - i
                break
            if ziel_hit:
                grund, exitp, bars = "ziel", tp, j - i
                break
        brutto = seite * (exitp - entry) / entry
        gebuehr = k["ein"] + k[grund if grund in k else "ende"]
        out.append({
            "t": df.index[i], "tag": pd.Timestamp(tage[g if False else a]),
            "seite": seite, "entry": entry, "exit": exitp, "grund": grund,
            "bars": bars, "brutto_bp": brutto * 1e4,
            "netto_bp": (brutto - gebuehr) * 1e4,
            "ziel_bp": z_abs / entry * 1e4, "stop_bp": s_abs / entry * 1e4,
            "start_bar": i, "tag_start": a, "tag_ende": b,
        })
    return pd.DataFrame(out)


def basissatz(df, push, ziel, stop, prozent=False, ziehungen=20, seed=7):
    """Kontrolle: gleicher Trade, aber Einstiegszeitpunkt zufaellig im Tag."""
    rng = np.random.default_rng(seed)
    o = df["open"].to_numpy(float); h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float);  c = df["close"].to_numpy(float)
    tage = df["tag"].to_numpy()
    grenzen = np.flatnonzero(np.r_[True, tage[1:] != tage[:-1]]); grenzen = np.r_[grenzen, len(df)]
    treffer = gesamt = 0
    for g in range(len(grenzen) - 1):
        a, b = grenzen[g], grenzen[g + 1]
        if b - a < 12:
            continue
        start = o[a]
        z_abs = start * ziel if prozent else ziel
        s_abs = start * stop if prozent else stop
        for _ in range(ziehungen):
            i = int(rng.integers(a, b - 4))
            seite = 1 if rng.random() < 0.5 else -1
            entry = c[i]
            tp = entry + seite * z_abs; sl = entry - seite * s_abs
            grund = "ende"
            for j in range(i + 1, b):
                if (l[j] <= sl) if seite == 1 else (h[j] >= sl):
                    grund = "stop"; break
                if (h[j] >= tp) if seite == 1 else (l[j] <= tp):
                    grund = "ziel"; break
            if grund in ("ziel", "stop"):
                gesamt += 1
                treffer += grund == "ziel"
    return treffer / max(gesamt, 1), gesamt


def bericht(t, name, breakeven=None, basis=None):
    if not len(t):
        print(f"{name:44s}  keine Trades"); return None
    entschieden = t[t["grund"].isin(["ziel", "stop"])]
    quote = (entschieden["grund"] == "ziel").mean() if len(entschieden) else np.nan
    x = t["netto_bp"].to_numpy()
    tw = x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 2 else np.nan
    print(f"{name:44s} {len(t):5d} {quote*100:7.1f}% {t['brutto_bp'].mean():8.2f} "
          f"{x.mean():9.2f} {tw:7.2f} "
          f"{(t['grund']=='ende').mean()*100:6.1f}% {t['bars'].mean()*15/60:7.1f}h")
    return dict(n=len(t), quote=quote, brutto=t["brutto_bp"].mean(), netto=x.mean(), t=tw)


if __name__ == "__main__":
    print("=" * 118)
    print("DIE REGEL: 15-min-Chart, erster Push vom Tagesstart, 1 Trade/Tag, Klammer bis Tagesschluss")
    print("=" * 118)
    btc = lade("btc")
    suche = btc[btc.index < GRENZE]; hold = btc[btc.index >= GRENZE]
    print(f"BTC 15m: {len(btc)} Bars, {btc['tag'].nunique()} Tage "
          f"({suche['tag'].nunique()} Suche / {hold['tag'].nunique()} Holdout)")

    print("\nWas 200 $ ueber die Jahre bedeutet:")
    for jahr, grp in btc.groupby(btc.index.year):
        m = grp["close"].median()
        print(f"  {jahr}: BTC Median {m:9,.0f} $  ->  200 $ = {200/m*100:5.3f} %"
              f"   (Kosten 8 bp = {8/(200/m*1e4)*100:5.1f} % des Ziels)")

    kopf = (f"\n{'Aufbau':44s} {'n':>5s} {'Treffer':>8s} {'brutto bp':>9s} "
            f"{'netto bp':>9s} {'t':>7s} {'Tagesende':>7s} {'Ø Dauer':>8s}")

    # ── Hauptkombination ─────────────────────────────────────────────────
    print("\n" + "=" * 118)
    print("HAUPTKOMBINATION (vorab benannt): Push 200 $, Ziel 200 $, Stop 200 $, Momentum")
    print("=" * 118)
    print(kopf); print("-" * 118)
    haupt = {}
    for periode, d in (("SUCHE", suche), ("HOLDOUT", hold)):
        for kost in ("brutto", "gemessen", "taker16"):
            t = trades(d, 200, 200, 200, 1, kosten=kost)
            haupt[(periode, kost)] = bericht(t, f"{periode:8s} Momentum, Kosten {kost}")
        t = trades(d, 200, 200, 200, -1, kosten="gemessen")
        bericht(t, f"{periode:8s} FADE (Kontrolle), Kosten gemessen")

    # ── Basissatz ────────────────────────────────────────────────────────
    print("\n" + "=" * 118)
    print("BASISSATZ: gleiche Klammer, aber zufaelliger Einstiegszeitpunkt im Tag")
    print("=" * 118)
    for periode, d in (("SUCHE", suche), ("HOLDOUT", hold)):
        p0, n0 = basissatz(d, 200, 200, 200)
        h = haupt[(periode, "gemessen")]
        entschieden = int(h["n"] * (1 - 0.0)) if h else 0
        print(f"  {periode:8s} Basissatz {p0*100:5.1f} % (n={n0})   "
              f"Strategie {h['quote']*100:5.1f} %   Differenz {(h['quote']-p0)*100:+5.1f} pp")
        t = trades(d, 200, 200, 200, 1, kosten="gemessen")
        ent = t[t["grund"].isin(["ziel", "stop"])]
        pv = stats.binomtest(int((ent["grund"] == "ziel").sum()), len(ent), p0,
                             alternative="greater").pvalue
        print(f"           Binomialtest gegen den Basissatz: p = {pv:.4f}")

    # ── Break-even ───────────────────────────────────────────────────────
    print("\n" + "=" * 118)
    print("BREAK-EVEN: welche Trefferquote braucht es, welche kommt heraus?")
    print("=" * 118)
    for periode, d in (("SUCHE", suche), ("HOLDOUT", hold)):
        t = trades(d, 200, 200, 200, 1, kosten="gemessen")
        ent = t[t["grund"].isin(["ziel", "stop"])]
        z = t["ziel_bp"].mean()
        be = (z + 9.0) / (2 * z)     # 9 bp mittlere Reibung
        print(f"  {periode:8s} Ziel Ø {z:.1f} bp -> Break-even {be*100:.1f} %   "
              f"gemessen {(ent['grund']=='ziel').mean()*100:.1f} %   "
              f"Luecke {((ent['grund']=='ziel').mean()-be)*100:+.1f} pp")

    # ── Gitter ───────────────────────────────────────────────────────────
    print("\n" + "=" * 118)
    print("EMPFINDLICHKEIT (keine Auswahl daraus) -- netto bp je Trade, Kosten gemessen")
    print("=" * 118)
    for periode, d in (("SUCHE", suche), ("HOLDOUT", hold)):
        print(f"\n  {periode} -- Zeilen: Push $, Spalten: Stop $ (Ziel = 200 $)")
        print(f"  {'':8s}" + "".join(f"{s:>12d}" for s in (100, 200, 400, 800)))
        for pu in (200, 500, 1000, 2000):
            zeile = f"  {pu:8d}"
            for st in (100, 200, 400, 800):
                t = trades(d, pu, 200, st, 1, kosten="gemessen")
                zeile += f"{(t['netto_bp'].mean() if len(t) else np.nan):12.1f}"
            print(zeile)
        print(f"\n  {periode} -- symmetrisch: Ziel = Stop = Push")
        print(f"  {'Push $':8s}{'n':>6s}{'Treffer':>10s}{'brutto bp':>11s}{'netto bp':>10s}{'netto $ je Trade':>18s}")
        for pu in (200, 500, 1000, 2000):
            t = trades(d, pu, pu, pu, 1, kosten="gemessen")
            if not len(t): continue
            ent = t[t["grund"].isin(["ziel", "stop"])]
            q = (ent["grund"] == "ziel").mean() if len(ent) else np.nan
            usd = (t["netto_bp"] / 1e4 * t["entry"] * 0.387).mean()
            print(f"  {pu:8d}{len(t):6d}{q*100:9.1f}%{t['brutto_bp'].mean():11.1f}"
                  f"{t['netto_bp'].mean():10.1f}{usd:17.2f}")

    # ── Quermarkt ────────────────────────────────────────────────────────
    print("\n" + "=" * 118)
    print("QUERMARKT: dieselbe Regel in Prozent (0,25 %) auf BTC und ETH")
    print("=" * 118)
    print(kopf); print("-" * 118)
    for sym in ("btc", "eth"):
        d = lade(sym)
        for periode, teil in (("SUCHE", d[d.index < GRENZE]), ("HOLDOUT", d[d.index >= GRENZE])):
            t = trades(teil, 0.0025, 0.0025, 0.0025, 1, prozent=True, kosten="gemessen")
            bericht(t, f"{sym.upper():4s} {periode:8s} 0,25 % Push/Ziel/Stop")

    # ── Was bringt es in Geld ────────────────────────────────────────────
    print("\n" + "=" * 118)
    print("IN GELD: bei 0,387 BTC je Trade (wie im Beispiel-Trade)")
    print("=" * 118)
    for periode, d in (("SUCHE", suche), ("HOLDOUT", hold)):
        t = trades(d, 200, 200, 200, 1, kosten="gemessen")
        usd = t["netto_bp"] / 1e4 * t["entry"] * 0.387
        jahre = (d.index[-1] - d.index[0]).days / 365.25
        print(f"  {periode:8s} {len(t)} Trades in {jahre:.1f} Jahren  |  "
              f"Ø {usd.mean():+7.2f} $ je Trade  |  Summe {usd.sum():+10.2f} $  |  "
              f"{usd.sum()/jahre:+9.2f} $ je Jahr")
        gebuehr = (t["brutto_bp"] - t["netto_bp"]) / 1e4 * t["entry"] * 0.387
        print(f"           davon an Gebuehren: {gebuehr.sum():,.2f} $ "
              f"(Brutto waere {(usd.sum()+gebuehr.sum()):+,.2f} $)")
    print("\nFERTIG")
