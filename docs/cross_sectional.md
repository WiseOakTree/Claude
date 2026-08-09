# Cross-Sectional Relative Strength — getestet

Vorschlag: Statt BTC absolut zu handeln, das relative Momentum-Gefälle nutzen.
Long den stärksten Coin, short (oder Cash) den schwächsten, Rebalancing alle
4–12 Stunden.

Der Reiz: Als einziger geprüfter Ansatz ändert er die **Struktur** der Wette —
von „Kurs steigt" zu „A läuft besser als B". Die Marktrichtung fällt heraus,
und genau daran ist bisher alles gescheitert.

**Ergebnis: echtes Brutto-Alpha, von Reibung aufgefressen, und im Holdout
negativ.**

## Aufbau

| | |
|---|---|
| Universum | **14 Coins** (ADA, ATOM, AVAX, BCH, BNB, BTC, DOGE, DOT, ETH, LINK, LTC, SOL, TRX, XRP) |
| Daten | 1h, 2021-03 bis 2026-07, 47.483 Stunden |
| Suchzeitraum | 2021-03 bis 2024-12 |
| Holdout | ab 2025-01 |
| Suchraum | 96 Kombinationen (Rückblick × Rebalancing × k × long-only/long-short) |

## 1. Das Signal ist echt — brutto

| Rebalancing | Umsatz/Jahr | **brutto** | Kosten bei 16 bp | netto |
|---|---|---|---|---|
| alle 8 h | 327× | **+82,0 %** | 52 % | +7,8 % |
| alle 24 h | 191× | **+53,9 %** | 31 % | +13,3 % |
| alle 72 h | 94× | +28,8 % | 15 % | +10,9 % |
| alle 168 h | 39× | **+39,0 %** | 6 % | **+30,5 %** |
| alle 336 h | 21× | +29,4 % | 3 % | +25,1 % |

Cross-Sectional-Momentum in Krypto hat **substanzielles Brutto-Alpha** — bis
+82 % im Jahr. Das ist qualitativ neu: In dieser Untersuchung war bisher kein
Ansatz brutto stark und nur an Kosten gescheitert; die meisten hatten schlicht
kein Signal.

**Break-even-Kosten** (bei denen netto null bleibt): 25 bp bei 8h-Rebalancing,
28 bp bei 24h, bis 141 bp bei zweiwöchigem. Die reale Schwelle von 16 bp wird
also bei niedriger Frequenz überlebt.

## 2. Die Umkehr ist nicht die Lösung

Falls Momentum an Kosten scheitert, liegt Reversal nahe (Verlierer kaufen).
Getestet — **brutto negativ**:

| Rückblick / Rebalancing | Momentum brutto | Reversal brutto |
|---|---|---|
| 12 h / 24 h | +12,3 % | −18,9 % |
| 24 h / 24 h | +30,7 % | −30,5 % |
| 72 h / 24 h | +36,4 % | −33,7 % |

Momentum ist die richtige Richtung. Reversal ist es eindeutig nicht.

## 3. Long/Short zerstört sich selbst

| Modus | Median p.a. | Drawdown | Sharpe |
|---|---|---|---|
| Long/Short (marktneutral) | **−55,9 %** | 97,7 % | −1,23 |
| Long-only (Rest Cash) | −3,4 % | 81,8 % | −0,07 |

Meine Erwartung war das Gegenteil — marktneutral sollte den Drawdown senken.
Tatsächlich verdoppelt die Short-Seite den Umsatz und damit die Kosten,
während sie den Krypto-Aufwärtsdrift wegnimmt, der die Long-Seite trägt.

## 4. Der Holdout kippt es

Beste Variante aus dem Suchzeitraum (long-only, Rückblick 168 h, alle 72 h
neu, k = 3), unverändert angewandt:

| | p.a. | Drawdown | Sharpe | Rendite/DD |
|---|---|---|---|---|
| **Suchzeitraum** | **+36,0 %** | 53,7 % | **+0,82** | 0,67 |
| *Benchmark (gleichgewichtet halten)* | *+34,5 %* | *78,1 %* | *+0,46* | *0,44* |
| **Holdout ab 2025-01** | **−20,3 %** | 38,7 % | **−0,72** | −0,52 |
| *Benchmark* | *−42,6 %* | *66,1 %* | *−0,70* | *−0,64* |

Im Suchzeitraum Sharpe +0,82 und besser als der Vergleichsmaßstab. Im Holdout
**−20,3 % pro Jahr**.

### Die eine faire Beobachtung

Die Strategie schlägt das gleichgewichtete Halten in **beiden** Zeiträumen
(+36,0 gegen +34,5 %, und −20,3 gegen −42,6 %). Es gibt also relative
Fähigkeit — sie verliert nur weniger, wenn alles fällt.

Für eine Challenge, die **absolute** +10 % verlangt, ist das wertlos.

## 5. Und selbst in-sample reicht es nicht

| | |
|---|---|
| erreichtes Verhältnis Rendite/Drawdown | **0,67** |
| für die Challenge nötig | **1,67** |
| Lücke | Faktor **2,5** |

Auf 6 % Drawdown skaliert bleiben **+4,0 % pro Jahr** — die +10 % dauerten
dann **30 Monate**.

## Fazit

Der strukturell interessanteste Ansatz der ganzen Untersuchung, und er
scheitert an drei Stellen gleichzeitig:

1. **Reibung.** Bei handelbarer Frequenz frisst der Umsatz 31–52 % pro Jahr.
2. **Holdout.** Was im Suchzeitraum Sharpe 0,82 hatte, verliert danach 20 %
   im Jahr.
3. **Das Verhältnis.** Selbst der beste In-sample-Wert liegt um Faktor 2,5
   unter dem, was die Challenge verlangt.

Bemerkenswert bleibt das Brutto-Alpha. Wer Maker-Orders auf einer Börse mit
niedrigen Gebühren stellen kann, hätte hier mehr Spielraum als ein Taker mit
16 bp — das ist aber ein anderes Handelsmodell, kein Prop-Konto.
