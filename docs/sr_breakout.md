# Support/Resistance-Ausbruch — der erste handelbare Effekt

Vorschlag nach zehn erfolglosen Ideen: ein Ausbruch aus Unterstützungs- und
Widerstandszonen.

**Ergebnis: der erste Befund dieser Untersuchung, der jede Härteprüfung
besteht — und trotzdem die Challenge nicht löst.** Beides muss klar
auseinandergehalten werden.

## Warum das nicht der schon getestete Donchian-Ausbruch ist

Donchian bricht ein **rollierendes Hoch** — jeder N-Bar-Höchststand zählt.
Eine echte S/R-Zone entsteht dagegen durch **mehrfaches Antesten** desselben
Niveaus. Daraus folgt eine falsifizierbare These, die im 120er-Suchlauf nicht
enthalten war:

> Je öfter ein Level gehalten hat, desto bedeutsamer ist sein Bruch.

## Aufbau (look-ahead-frei)

| | |
|---|---|
| Pivots | Hoch/Tief über ±8 Bars — **erst bei i+8 bestätigt** |
| Level | Pivots im Umkreis von 0,5 × ATR zusammengefasst, Berührungen gezählt |
| Ausbruch | Schlusskurs kreuzt ein Level, das bei *t−1* bereits bekannt war |
| Ausführung | Position ab *t+1* |
| Daten | BTC 1h, 4,5 Jahre, 3.887 Pivots, ⌀ 44 aktive Level je Bar |

## 1. Die Dosis-Wirkung: monoton

| Berührungen | Ereignisse | 24 h | 72 h | vs. 16 bp |
|---|---|---|---|---|
| 1 | 14.418 | +3,94 bp | +12,54 bp | 0,25× |
| 2 | 8.075 | +8,09 bp | +15,58 bp | 0,51× |
| 3 | 4.651 | +9,54 bp | +10,60 bp | 0,60× |
| 4 | 2.641 | +22,11 bp | +23,03 bp | 1,38× |
| **5** | 1.536 | **+29,94 bp** | +48,84 bp | **1,87×** |
| **6** | 775 | **+42,88 bp** | — | **2,68×** |
| 8 | 162 | +107,84 bp | — | 6,74× |

Eine saubere monotone Dosis-Wirkung ist die Signatur eines echten Effekts —
Rauschen erzeugt so etwas nicht. Und ab 4 Berührungen liegt der Effekt **über
der Kostenschwelle**, was in dieser Untersuchung zuvor nie vorkam.

## 2. Vier Kontrollen — alle bestanden

Nach den Fehlschlägen zuvor (DVOL-z-Score, Orderbuch-Langhorizont) habe ich
jede Falle geprüft, die diese Befunde gekippt hat.

### Ist es nur BTC-Aufwärtsdrift?

| Berührungen | Long | Short |
|---|---|---|
| 5 | +14,07 bp | **+45,35 bp** |
| 6 | +29,99 bp | **+53,34 bp** |

**Nein — Shorts sind stärker als Longs.** Der allgemeine 24h-Drift von BTC
beträgt +5,29 bp. Wäre es Drift, müssten Longs dominieren.

### Überlappungskorrektur (Ereignisse in 24h-Blöcke gruppiert)

| Berührungen | unabh. Blöcke | Effekt | p |
|---|---|---|---|
| 4 | 899 | +12,80 bp | 0,179 |
| **5** | 622 | +30,20 bp | **0,0072** |
| **6** | 366 | +45,70 bp | **0,0015** |

### Jahresweise Stabilität (≥5 Berührungen)

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| +49,6 | +31,3 | +42,4 | +20,2 | +20,0 | +27,9 bp |

**Alle sechs Jahre positiv.** Abnehmender Trend, aber kein Jahr negativ.

### Kontrolle mit zufälligem Zeitpunkt

| | echt | Kontrolle | p |
|---|---|---|---|
| ≥5 Berührungen | +29,94 bp | +0,29 bp | 0,0053 |
| ≥6 Berührungen | +42,88 bp | −3,26 bp | 0,0013 |

## 3. Als Strategie: gut, aber nicht gut genug

| Variante | Rendite | Drawdown | **R/DD** | Pass-Rate |
|---|---|---|---|---|
| ≥6 Ber., 24 h halten | +7,0 % | 5,1 % | **1,39** | 13,8 % |
| **≥6 Ber., 48 h halten** | **+6,5 %** | **6,8 %** | **0,95** | **17,0 %** |
| ≥5 Ber., 24 h halten | +1,1 % | 12,2 % | 0,09 | 10,4 % |
| ≥6 Ber., 48 h + Vol-Targeting | +2,1 % | 2,2 % | 0,96 | 0,9 % |

Out-of-Sample der besten Variante:

| | Pass | Rendite | Drawdown |
|---|---|---|---|
| 1. Hälfte | 15,2 % | **+5,4 %** | 8,6 % |
| 2. Hälfte | 20,6 % | **+8,5 %** | 5,9 % |
| *(reines Vol-Targeting zum Vergleich)* | *3,6 % / 23,0 %* | *−2,2 % / +1,4 %* | |

**Der qualitative Unterschied zu allem Bisherigen:** Diese Strategie erzeugt
in **beiden** Hälften eine positive Rendite (+5,4 % und +8,5 %). Vol-Targeting
kommt auf ähnliche Pass-Raten, erzeugt dabei aber keine Rendite (−2,2 % und
+1,4 %) — es besteht nur, wenn BTC von selbst läuft.

Hier kommt die Rendite zum ersten Mal **aus der Strategie**.

### Warum es die Challenge trotzdem nicht löst

Das Verhältnis Rendite/Drawdown liegt bei **0,95 bis 1,39**. Nötig sind
**1,67**. Der Abstand ist erstmals klein — Faktor 1,2 bis 1,8 statt Faktor 13
wie beim Coinbase-Premium — aber er ist da.

Und Vol-Targeting hilft hier **nicht**: Es senkt den Drawdown auf 2,2 %,
drückt die Rendite aber auf +2,1 % — das Verhältnis bleibt bei 0,96, und die
Pass-Rate bricht auf 0,9 % ein, weil das 10-%-Ziel unerreichbar wird.

## Einordnung

**Was gesichert ist:** Der *Effekt* ist real. Monotone Dosis-Wirkung,
überlappungskorrigiert signifikant, in allen sechs Jahren positiv, gegen
Zufallskontrollen abgesichert, und nicht durch Aufwärtsdrift erklärbar
(Shorts sind stärker). Das ist deutlich mehr Evidenz als für jeden anderen
Befund dieser Untersuchung außer der Volatilitätsprämie.

**Was nicht gesichert ist:** Die konkrete *Strategie*. Für die Umsetzung wurden
24 Varianten geprüft; „≥6 Berührungen, 48 h" ist eine ausgewählte Kombination,
und die Pass-Rate von 17,0 % ist entsprechend optimistisch. Die Evidenz für den
Effekt ist unabhängig davon — die für diese Parameterwahl nicht.

**Was es praktisch bedeutet:** Ein Level, das fünf- oder sechsmal gehalten hat
und dann bricht, ist ein statistisch belegtes Ereignis mit +30 bis +46 bp
Erwartungswert auf 24 Stunden. Das ist real und über der Kostenschwelle. Es
reicht nicht für +10 % in 90 Tagen ohne 6 % Drawdown — aber es ist das erste
Mal in dieser Untersuchung, dass ein Chartmuster einer ernsthaften Prüfung
standhält.
