# Alternative Daten: ETF-Flüsse, Orderbuch, Funding — getestet

Nachdem klassische technische Analyse nichts hergab
([`strategy_search.md`](strategy_search.md)), war die naheliegende Frage: Steckt
in **anderen Datenquellen** ein Edge? Konkret vorgeschlagen: ETF-Flüsse und
Orderbuch.

## Vorab: Die Kostenschwelle entscheidet mit

| Kostenart (Kraken Prop) | je Roundtrip |
|---|---|
| Kommission (2 Seiten) | 0,080 % |
| Halber Spread (2×) | 0,040 % |
| Slippage (2×) | 0,040 % |
| **Summe** | **0,160 % = 16 Basispunkte** |

Ein Signal muss also im Mittel **mehr als 16 bp** Bewegung vorhersagen, nur um
kostendeckend zu sein.

## Orderbuch — ohne Test verworfen

Orderflow-Signale (Bid/Ask-Ungleichgewicht, Mikrostruktur) sagen typischerweise
**1–5 bp über Sekunden bis Minuten** voraus. Das liegt um den Faktor 3–15
**unter** der Kostenschwelle. Wer das handelt, braucht Colocation,
Maker-Rebates und Millisekunden-Latenz — auf einem manuellen Prop-Konto ist
das strukturell unmöglich, unabhängig davon, ob der Edge real ist.

Kein Backtest nötig: Die Rechnung entscheidet.

## ETF-Flüsse — über einen Stellvertreter getestet

Direkte Flussdaten (Farside, SoSoValue) sind nicht frei zugänglich. Getestet
wurde deshalb der **Coinbase-Premium** — der Preisaufschlag von Coinbase
gegenüber Binance. Er misst dieselbe Sache: US-institutionelle Nachfrage, die
zu großen Teilen über Coinbase abgewickelt wird (auch die ETF-Verwahrung).

Zusätzlich getestet: **Funding-Raten** (Positionierung im Perp-Markt).

**Datensatz:** 1.132 Tage (2023-05 bis 2026-06), Coinbase + Binance + Funding.

### Vorhersagekraft (Spearman-IC, look-ahead-frei)

| Signal | Horizont | IC | p-Wert | Bewertung |
|---|---|---|---|---|
| Coinbase-Premium | 5 Tage | **+0,098** | **0,001** | signifikant |
| Premium (z-Score) | 5 Tage | +0,083 | 0,006 | signifikant |
| Coinbase-Premium | 3 Tage | +0,071 | 0,018 | schwach |
| Premium-Änderung | alle | ~0 | > 0,3 | nichts |
| Funding-Rate | alle | ~0 | > 0,1 | **nichts** |

Richtung ökonomisch plausibel: höherer US-Aufschlag → höhere Folgerenditen.

**Aber drei Einschränkungen:**

1. **Multiples Testen:** 15 Tests gerechnet. Nach Bonferroni läge die Schwelle
   bei p < 0,0033 — nur ein Wert überlebt knapp.
2. **Quintile nicht monoton:** Q1 −0,22 %, Q2 +0,17 %, Q3 −0,06 %, Q4 +0,45 %,
   Q5 +0,10 %. Kein sauberer Zusammenhang, eher Rauschen.
3. **Out-of-Sample instabil:** erste Hälfte p = 0,103 (nicht signifikant),
   zweite Hälfte p = 0,040 (grenzwertig). Das Signal hält nicht durchgängig.

### Als Strategie gehandelt

Long bei positivem Premium-z-Score, short bei negativem, look-ahead-frei,
16 bp Kosten je Roundtrip:

| Schwelle | Trades | Ø netto/Trade | Gesamt | Sharpe |
|---|---|---|---|---|
| 0,0 | 242 | +0,327 % | +79,1 % | 0,83 |
| 0,3 | 384 | +0,177 % | +68,1 % | **1,00** |
| 0,5 | 407 | +0,092 % | +37,6 % | 0,87 |
| 1,0 | 358 | −0,032 % | −11,6 % | 0,49 |

Positiv nach Kosten — deutlich besser als alles aus dem TA-Suchlauf. Aber:

- **Unterperformt einfaches Halten:** +79 % gegenüber +119 % bei BTC über
  denselben Zeitraum. (Immerhin: Korrelation zu BTC nur −0,07, also kein
  verkapptes Beta.)
- **Sharpe 0,8–1,0.** Für die Challenge nötig wäre ~2+.

### Gegen die Challenge-Regeln

35 Walk-Forward-Fenster à 90 Tage:

| | |
|---|---|
| Pass-Rate | **23 %** (8/35) |
| Median-Rendite | +7,4 % |
| **Worst-Drawdown** | **57,2 %** (Limit: 6 %) |

## Warum das trotz Signal nicht reicht

Die entscheidende Kennzahl ist **Rendite ÷ Drawdown**:

| | Verhältnis |
|---|---|
| Diese Strategie | 7,4 / 57,2 = **0,13** |
| Challenge braucht | 10 / 6 = **1,67** |
| **Lücke** | **Faktor 13** |

Herunterskalieren hilft nicht: Um den Drawdown auf 6 % zu drücken, müsste die
Position auf **10 %** skaliert werden — aus +7,4 % Median würden **+0,78 %**.
Das 10 %-Ziel bräuchte dann rund **39 Monate**.

**Rendite und Drawdown skalieren gemeinsam.** Deshalb ist ihr Verhältnis die
einzige Kennzahl, die für eine Prop-Challenge zählt — nicht die Rendite allein.


## Liquidations-Level — getestet

Die mechanisch überzeugendste Idee: Eine Liquidation ist eine **erzwungene**
Marktorder. Der Verkäufer *muss* verkaufen, was den Kurs unter den fairen Wert
drückt — dagegenzuhalten wäre ein echter ökonomischer Edge, kein Chartmuster.
Und die Größenordnung stimmt: Kaskaden bewegen den Kurs um 100–500 bp, weit über
der Kostenschwelle von 16 bp.

**Datenlage:** Binance hat die Liquidations-Rohdaten eingestellt (404),
Coinglass braucht einen Key. Rekonstruiert wurde die Kaskade deshalb aus den
**Metrics-Daten**: ein 5-Minuten-Fenster mit großem Kursausschlag **und**
einbrechendem Open Interest ist die Signatur erzwungener Schließungen.

**Datensatz:** 156.887 Fünf-Minuten-Fenster, 2025-01 bis 2026-06 (18 Monate),
5-Minuten-Volatilität 0,145 %.

### Ergebnis: keine Rückkehr messbar

| Kaskaden-Stärke | Fälle (down/up) | bestes Ergebnis | p |
|---|---|---|---|
| moderat (2σ, OI −0,3 %) | 369 / 306 | +0,090 % nach 1 h | 0,092 |
| stark (3σ, OI −0,5 %) | 111 / 78 | +0,135 % nach 1 h | 0,212 |
| extrem (4σ, OI −1,0 %) | 19 / 16 | zu wenige Fälle | — |

Kein Wert erreicht Signifikanz (alle p > 0,08). Entscheidend: Selbst der beste
Effekt (+0,135 %) liegt **unter der Kostenschwelle von 0,160 %** — er wäre
selbst dann nicht handelbar, wenn er echt wäre.

**Die These ist nicht einmal richtungskonsistent:** Nach Up-Kaskaden
(Short-Liquidationen) sind die Folgerenditen ebenfalls positiv (+0,247 % nach
1 h). Bei echter Mean-Reversion müssten sie negativ sein. Das Muster sieht nach
allgemeinem Aufwärtsdrift im Zeitraum aus, nicht nach einem Kaskaden-Effekt.

**Nicht testbar war die Heatmap** (wo künftige Liquidationen *liegen*) — das ist
Coinglass' Schätzmodell aus Open Interest und Hebelannahmen, keine beobachtbare
Größe, und nicht frei zugänglich. Getestet wurde die härtere, sauber messbare
Variante: die Reaktion auf tatsächlich eingetretene Kaskaden.


## Tech-Kopplung (Nasdaq / NVIDIA) — getestet

Beobachtung: BTC handelt wie ein High-Beta-Risikoasset; fällt Tech, fällt BTC.

**Die Kopplung ist real:**

| | Korrelation (gleicher Tag) |
|---|---|
| BTC ~ QQQ | **+0,384** (rollierend 60T: −0,08 .. +0,65, Median +0,42) |
| BTC ~ NVDA | +0,282 |

**Aber sie ist gleichzeitig, nicht vorlaufend.** Der entscheidende Test — sagt
der Move der US-Aktiensitzung die BTC-Bewegung *danach* voraus? Sauber
abgegrenzt: QQQ open→close am Tag D (bekannt 21:00 UTC) gegen BTC von 21:00 UTC
bis 14:00 UTC am Folgetag, also während die Börsen geschlossen sind:

| Ziel | r | p |
|---|---|---|
| BTC 21:00 → 14:00 (Aktien zu) | **−0,0006** | 0,985 |
| BTC bis nächster Aktienschluss | −0,0232 | 0,464 |

Quintil-Analyse (BTC übernacht je QQQ-Sitzungsquintil): +0,144 %, −0,115 %,
+0,088 %, −0,043 %, +0,114 % — reines Rauschen. Spread Q5−Q1 = **−0,029 %**,
weit unter der Kostenschwelle von 0,160 %.

(Ein schwacher Wert bei Tagesdaten — QQQ(t−1) → BTC(t), r = −0,091, p = 0,004 —
hält dem schärferen, überlappungsfreien Test nicht stand.)

**Interpretation:** BTC und Tech bewegen sich in Echtzeit gemeinsam, nicht
nacheinander. Die Information ist eingepreist, bevor man reagieren kann —
Markteffizienz bei einer breit beobachteten Beziehung.

### Trotzdem nützlich — als Risikohinweis, nicht als Signal

Eine Korrelation von +0,38 heißt: **Eine BTC-Position ist faktisch eine
verkappte Tech-Wette.** Für eine Challenge mit 6 %-Drawdown-Limit ist das
relevant: An Tagen mit großen Makro-/Tech-Ereignissen (Fed, CPI,
NVIDIA-Quartalszahlen) steigt das Risiko eines gleichzeitigen Einbruchs.
Argument für kleinere Positionen oder Pause an solchen Tagen — kein
Handelssignal.

## Fazit

Zum ersten Mal ein messbares Signal (Coinbase-Premium, IC ~0,10 auf 5 Tage) —
aber schwach, out-of-sample instabil und um den Faktor 13 zu weit von dem
entfernt, was ein 6-%-Drawdown-Limit verlangt.

**Damit ist der zugängliche Ideenraum ausgeschöpft.** Klassische TA: nichts.
Orderbuch: rechnerisch unerreichbar. Alternative Daten: ein Flüstern, das nicht
trägt. Liquidationskaskaden: kein messbarer Effekt, und selbst der beste
Schätzwert liegt unter den Handelskosten. Tech-Kopplung: real, aber
gleichzeitig statt vorlaufend — kein Signal, nur ein Risikohinweis. Die ehrliche Schlussfolgerung: Mit dem, was hier gebaut werden kann, ist
diese Challenge nicht planbar zu gewinnen.
