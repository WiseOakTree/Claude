# Orderflow, Orderbuch-Liquidität, Volumen-Ausbrüche und MACD — getestet

Vier Vorschläge, drei davon mit echten neuen Daten geprüft, einer als
Nachholung: Orderflow hatte ich in [`altdata_test.md`](altdata_test.md)
**wegargumentiert statt gemessen**. Das ist hier nachgeholt.

**Ergebnis: Alle Signale sind real und statistisch hochsignifikant. Keines ist
groß genug für die Kostenschwelle von 16 bp.**

## 1. Orderflow — jetzt gemessen

**Daten:** 472.896 Fünf-Minuten-Bars (2022-01 bis 2026-06, 4,5 Jahre),
Binance-Futures-Klines inkl. Taker-Buy-Volumen. Daraus das
Orderflow-Ungleichgewicht:

```
OFI = (aggressives Kaufvolumen − aggressives Verkaufvolumen) / Gesamtvolumen
```

| Signal | Horizont | IC | p | Q5−Q1 | vs. 16 bp |
|---|---|---|---|---|---|
| OFI geglättet (1 h) | 1 h | **−0,041** | **3·10⁻¹⁷³** | −1,26 bp | **0,08×** |
| OFI z-Score (1 Tag) | 5 min | −0,036 | 9·10⁻¹³⁴ | −0,59 bp | 0,04× |
| OFI (5 min) | 5 min | −0,034 | 3·10⁻¹²³ | −0,52 bp | 0,03× |

Der p-Wert von 10⁻¹⁷³ ist der **statistisch stärkste Fund der gesamten
Untersuchung**. Und gleichzeitig der eindeutigste Beleg dafür, dass
Signifikanz und Handelbarkeit nichts miteinander zu tun haben:

| | |
|---|---|
| Stärkstes Dezil-Signal (5 min) | **0,29 bp** |
| Kostenschwelle je Roundtrip | **16,00 bp** |
| Verhältnis | **0,02×** |
| Trades für +10 % nötig | **3.475** |

### Das Vorzeichen ist die eigentliche Erklärung

Der IC ist **negativ**: Aggressives Kaufen sagt *fallende* Folgekurse voraus.
Das ist keine Anomalie, sondern die Bezahlung des Market Makers — wer
Liquidität nimmt, zahlt sie. Genau deshalb ist das Signal für einen
**Taker strukturell nicht erntbar**: Man steht auf der falschen Seite
desselben Geschäfts.

Die frühere Schätzung („1–5 bp über Sekunden bis Minuten") war damit korrekt,
aber sie war eine Behauptung. Jetzt ist sie gemessen: 0,3–1,3 bp.

## 2. Orderbuch-Tiefe — der einzige Fund, der out-of-sample hält

**Daten:** 9.202.020 Orderbuch-Snapshots (Binance `bookDepth`, 60-Sekunden-
Takt, 303 Tage 2025-09 bis 2026-06), Tiefe auf 12 Ebenen (±0,2 % bis ±5 %
vom Mittelkurs).

```
Imbalance = (Bid-Notional − Ask-Notional) / (Bid + Ask)
```

| Signal | Horizont | IC | p | Q5−Q1 | vs. 16 bp |
|---|---|---|---|---|---|
| **Imbalance ±5 %** | **4 h** | **+0,054** | 4·10⁻⁵⁸ | +5,04 bp | 0,31× |
| Imbalance ±3 % | 4 h | +0,052 | 2·10⁻⁵³ | **+6,21 bp** | **0,39×** |
| Imbalance ±3 % | 1 h | +0,041 | 2·10⁻³⁴ | +2,62 bp | 0,16× |
| Liquidität (Niveau) | alle | ~0,006 | > 0,05 | — | nichts |

**Out-of-Sample-Kontrolle** des stärksten Signals (Imbalance ±5 %, 4 h):

| | IC |
|---|---|
| 1. Hälfte | +0,046 (p = 1,7·10⁻²¹) |
| 2. Hälfte | **+0,057** (p = 2,6·10⁻³²) |

Das ist das **einzige Signal der gesamten Untersuchung, das out-of-sample
stärker wird statt zusammenzubrechen** — im Gegensatz zum Coinbase-Premium,
zum DVOL-z-Score und zu jeder getunten TA-Variante.

Trotzdem nicht handelbar: 5–6 bp Effekt gegen 16 bp Kosten. Es fehlt der
**Faktor 3**. Bemerkenswert ist die Richtung der Zeitskala — anders als beim
Orderflow wächst der Effekt mit dem Horizont (0,17 → 0,52 → 2,62 → 6,21 bp
von 5 min auf 4 h). Bei ausreichend langem Horizont könnte er die Schwelle
überschreiten; das ließ sich mit 303 Tagen nicht mehr sauber prüfen.

**Das Liquiditätsniveau selbst** (wie viel Tiefe insgesamt im Buch liegt) hat
keine Vorhersagekraft (p > 0,05 auf allen Horizonten).

### Nachtrag: der lange Horizont, auf 1.265 Tagen nachgeprüft

Der offene Faden war die monoton mit dem Horizont wachsende Effektgröße. Auf
den ersten 303 Tagen sah das so aus:

| Horizont | Q5−Q1 | vs. 16 bp | p korrigiert |
|---|---|---|---|
| 4 h | +6,2 bp | 0,39× | **0,026** |
| 1 T | +16,7 bp | 1,04× | 0,446 |
| **3 T** | **+110,6 bp** | **6,92×** | 0,266 |

Die +110 bp bei 3 Tagen wären das Vierfache dessen gewesen, was die Challenge
braucht. Kontrollen sprachen dafür: 3,7× stärker als reine
Preis-Mean-Reversion, nach Herausrechnen der Vergangenheitsrendite blieben
108 von 109 bp übrig, und der Effekt war in allen drei Preisregimen da
(+88 / +136 / +68 bp). Es fehlte nur die Signifikanz — 303 Tage geben bei
3-Tage-Horizont nur 100 unabhängige Fenster.

**Deshalb 973 weitere Tage geladen (2023-01 bis 2025-08), n_eff von 100 auf
421 vervierfacht. Der Befund verschwindet:**

| Zeitraum | imb3 | imb5 |
|---|---|---|
| 2025-09 .. 2026-06 (Erstbefund) | +110,6 bp | +104,0 bp |
| **2023-01 .. 2025-08 (neu)** | **−33,4 bp** | **−9,7 bp** |
| gesamt (1.265 Tage) | +17,8 bp (p = 0,57) | +42,9 bp (p = 0,33) |

Auf den 973 zuvor ungetesteten Tagen ist der Effekt **nicht vorhanden und
teilweise umgekehrt**. Die +110 bp waren ein Artefakt des Zehnmonatsfensters,
in dem der Datensatz zufällig begann. Kein Horizont über 4 Stunden übersteht
Signifikanz und Kostenschwelle gemeinsam.

### Was bleibt: ein sehr stabiles, sehr kleines 4-Stunden-Signal

| Jahr | IC | Q5−Q1 |
|---|---|---|
| 2023 | +0,063 | −5,9 bp |
| 2024 | +0,057 | +8,7 bp |
| 2025 | +0,037 | +9,3 bp |
| 2026 | +0,056 | +5,1 bp |
| **gesamt** | **+0,054** | **+5,0 bp** (p = 3·10⁻⁶) |

Der IC ist über vier Jahre bemerkenswert konstant — und die Schätzung aus den
ersten 303 Tagen (+5,04 bp) trifft die aus 1.265 Tagen (+5,0 bp) auf ein
Zehntel Basispunkt genau. Das Signal ist echt und gut vermessen.

Es ist nur **0,31× so groß wie die Kosten**. Und die Vorzeichen der
Quintil-Spreads wechseln über die Jahre (2023 negativ), was selbst die
Richtung des handelbaren Teils fragwürdig macht.

**Der Faden ist damit geschlossen.** Die Lehre ist methodisch: Ein Effekt, der
mit dem Horizont wächst, kann genau deshalb wachsen, weil die Zahl
unabhängiger Beobachtungen schrumpft. Die Kontrollen (Preisbereinigung,
Doppelsortierung, Regime-Konsistenz) waren alle bestanden — sie prüfen
Konfundierung, nicht Zufall. Gegen Zufall hilft nur mehr Zeit, und die hat den
Befund kassiert.

## 3. Ausbruch mit Volumenbestätigung und MACD

Beide Familien fehlten im ursprünglichen 120er-Suchlauf
([`strategy_search.md`](strategy_search.md)) — echtes Neuland. Als
`strategies.macd` und `strategies.breakout_volume` implementiert; beide
bestehen `test_no_lookahead`.

138 Kombinationen (2 Familien × Parameter × 3 Timeframes × 3 Risikostufen),
gleiche Methodik: Walk-Forward, 90-Tage-Fenster, echte Kraken-Prop-Kosten,
`execution.mode="close"`.

| Familie | beste Pass-Rate | Median | worst DD | TF |
|---|---|---|---|---|
| Ausbruch + Volumen | **12,9 %** | +5,14 % | 12,5 % | 4h |
| MACD | 7,2 % | −2,85 % | 21,7 % | 4h |

- **0,0 %** aller Kombinationen erreichen 50 % Pass-Rate
- Median-Rendite über alle 138: **+0,02 %**

Dasselbe Nullergebnis wie beim ersten Suchlauf (+0,00 % über 120
Kombinationen).

### Die Volumenbestätigung hat einen echten, aber anderen Effekt

Direktvergleich — identischer Donchian-Ausbruch, identische Parameter und
Kosten, einziger Unterschied ist der Volumenfilter (Volumen > 1,5× Mittel):

| TF / Lookback | ohne Filter | mit Volumen | Trades |
|---|---|---|---|
| 1h / 20 | Median **−3,41 %** | **+1,37 %** | 1024 → 724 |
| 1h / 55 | −0,81 % | +0,05 % | 416 → 370 |
| 4h / 20 | +0,62 % | **+2,64 %** | 228 → 148 |
| 4h / 55 | +1,01 % | +1,03 % | 94 → 88 |

**Die These stimmt:** Ausbrüche auf dünnem Volumen sind schlechter, der Filter
hebt die Rendite je Trade deutlich. Aber die **Pass-Rate** verbessert er nur in
**1 von 9** Fällen — weniger Trades bei etwa gleichem Drawdown heben das
Verhältnis Rendite/Drawdown nicht.

**Out-of-Sample** der besten Variante (4h, Lookback 20, 1,5×, 1 % Risiko):

| | Pass-Rate |
|---|---|
| 1. Hälfte (2021-03..2023-10) | 20,8 % |
| 2. Hälfte (2023-10..2026-06) | **6,3 %** |

Klassischer Überanpassungs-Zusammenbruch.

## Fazit

Vier Ideen, drei neue Datensätze (472k Bars Orderflow, 9,2 Mio.
Orderbuch-Snapshots, 138 neue TA-Kombinationen). Das Muster ist jetzt sehr
scharf:

**Die Signale existieren.** Orderflow ist mit p = 10⁻¹⁷³ so gut belegt wie
kaum etwas in der Finanzmarktforschung. Orderbuch-Imbalance hält sogar
out-of-sample. Volumenbestätigung verbessert die Trade-Qualität messbar.

**Und keines ist groß genug.** 0,3 bp, 6,2 bp, +2 pp Median — gegen 16 bp
Reibung je Roundtrip.

Nicht die Signalsuche ist die Wand, sondern die **Kostenschwelle**. Ein
manueller Trader auf einem Prop-Konto zahlt 16 bp; die Effekte, die in diesen
Daten stecken, sind 3- bis 50-mal kleiner. Wer sie ernten will, braucht
Maker-Rebates statt Taker-Gebühren und Latenz im Millisekundenbereich — eine
andere Infrastrukturklasse, keine bessere Strategie.
