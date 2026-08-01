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

## Fazit

Zum ersten Mal ein messbares Signal (Coinbase-Premium, IC ~0,10 auf 5 Tage) —
aber schwach, out-of-sample instabil und um den Faktor 13 zu weit von dem
entfernt, was ein 6-%-Drawdown-Limit verlangt.

**Damit ist der zugängliche Ideenraum ausgeschöpft.** Klassische TA: nichts.
Orderbuch: rechnerisch unerreichbar. Alternative Daten: ein Flüstern, das nicht
trägt. Die ehrliche Schlussfolgerung: Mit dem, was hier gebaut werden kann, ist
diese Challenge nicht planbar zu gewinnen.
