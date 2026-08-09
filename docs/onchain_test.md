# On-Chain-Daten: MVRV, Puell, Hash Ribbons, NVT — getestet

Vorschlag: Blockchain-Daten (Transaktionsvolumen, Wallet-Aktivität,
Miner-Verhalten) nutzen, um Marktzyklen und Wendepunkte zu erkennen.

**Ergebnis: Ein Signal mit klarer, monotoner Struktur — das genau umgekehrt
wirkt als die verbreitete Lesart. Statistisch nicht von Zufall zu trennen, und
als Strategie ein Totalausfall.**

## Datengrundlage

| | |
|---|---|
| Quellen | CoinMetrics Community API + Blockchain.com Charts (beide frei) |
| Zeitraum | **2013-01 bis 2026-08 (13,6 Jahre, 5.118 Tage)** |
| Kennzahlen | MVRV, Marktkapitalisierung, aktive Adressen, Transaktionszahl, Hashrate, Emission (USD), Gebühren, Transaktionsvolumen |

Bemerkenswert: **`CapMVRVCur` ist frei verfügbar** — das Verhältnis von Markt-
zu realisierter Kapitalisierung, der bekannteste On-Chain-Zyklusindikator. Die
üblichen Bezahlschranken (Glassnode, SoSoValue) waren dafür nicht nötig.

Daraus die klassischen Indikatoren gebaut:

| Indikator | Konstruktion | misst |
|---|---|---|
| **MVRV z-Score** | MVRV, normiert über 365 Tage | Bewertung |
| **Puell Multiple** | Tagesemission USD / 365-Tage-Mittel | Miner-Verhalten |
| **Hash Ribbons** | Hashrate 30T-Mittel / 60T-Mittel | Miner-Kapitulation |
| **NVT** | Marktkap. / Transaktionsvolumen (28T) | Netzwerknutzung |
| **Adressen-Momentum** | aktive Adressen 30T / 180T | Wallet-Aktivität |
| **Transaktions-Momentum** | Transaktionszahl 30T / 180T | Netzwerknutzung |

Alle Indikatoren nutzen ausschließlich rückblickende Fenster — look-ahead-frei.

## Ergebnis: 2 von 32 Kombinationen signifikant

8 Signale × 4 Horizonte (30/90/180/365 Tage), jeweils mit
**Überlappungskorrektur** — die Lehre aus der Orderbuch-Analyse, wo naive
p-Werte von 10⁻²⁴⁰ nichts wert waren.

| Signal | Horizont | IC | p naiv | **p korrigiert** | n_eff |
|---|---|---|---|---|---|
| **MVRV z-Score** | 30 T | +0,169 | 9·10⁻³¹ | **0,037** | 152 |
| **MVRV z-Score** | 90 T | **+0,281** | 1·10⁻⁸² | **0,048** | 50 |
| MVRV z-Score | 180 T | +0,368 | 2·10⁻¹⁴¹ | 0,074 | 25 |
| MVRV z-Score | 365 T | +0,338 | 2·10⁻¹¹³ | 0,294 | 12 |
| Puell Multiple | alle | ≤ 0,25 | — | 0,45–0,90 | — |
| Hash Ribbons | alle | ≤ 0,08 | — | 0,40–0,99 | — |
| NVT | alle | ≤ 0,16 | — | 0,56–0,93 | — |
| Adressen-Momentum | alle | ≤ 0,10 | — | 0,53–0,79 | — |
| Transaktions-Momentum | alle | ≤ 0,20 | — | 0,52–0,97 | — |

**Miner-Verhalten (Puell, Hash Ribbons) und Netzwerknutzung (NVT, Adressen,
Transaktionen) liefern nichts.** Kein einziger Wert kommt in die Nähe von
Signifikanz.

### Bei 32 Tests sind 1,6 Zufallstreffer zu erwarten. Gefunden: 2.

Die Bonferroni-Schwelle liegt bei 0,05/32 = **0,0016**. MVRV erreicht 0,037
bzw. 0,048 — **beide fallen um mehr als das Zwanzigfache durch.**

## Der interessante Teil: MVRV wirkt umgekehrt

Die verbreitete Lesart ist: MVRV niedrig = unterbewertet = kaufen, MVRV hoch
(> 3,7) = überhitzt = verkaufen. Gemessen über 13,6 Jahre, 90-Tage-Folgerendite:

| MVRV-Quintil | Median | Mittel |
|---|---|---|
| Q1 (sehr günstig) | **−8,2 %** | +3,3 % |
| Q2 (günstig) | −9,8 % | +2,7 % |
| Q3 (neutral) | +10,9 % | +23,3 % |
| Q4 (teuer) | +21,9 % | +36,8 % |
| Q5 (sehr teuer) | **+23,3 %** | +35,4 % |

**Monoton steigend statt fallend.** Wer bei niedrigem MVRV kaufte, verlor in
den folgenden 90 Tagen im Median 8–10 %; wer bei hohem MVRV kaufte, gewann 22–23 %.

MVRV ist also — auf 30- bis 90-Tage-Sicht — ein **Momentum-Indikator**, kein
Kontraindikator. Ökonomisch plausibel: Ein hohes MVRV bedeutet, dass die
Mehrheit der Coins im Gewinn liegt, und das ist ein Bullenmarkt. Die
Zyklusgipfel, für die MVRV berühmt ist, sind wenige Einzelereignisse — sie
prägen die Erzählung, nicht die Statistik.

Out-of-Sample bleibt die Größe erhalten (IC +0,259 → +0,281), aber **keine
der beiden Hälften ist für sich signifikant** (p = 0,21 bzw. 0,17, n_eff = 25).

## Das strukturelle Problem: es gibt nur 3,5 Zyklen

| | |
|---|---|
| Datenlänge | 14,0 Jahre |
| Vierjahreszyklen darin | **≈ 3,5** |
| n_eff auf 365-Tage-Sicht | **12** |

Ein Zyklusindikator lässt sich mit dreieinhalb Zyklen **prinzipiell nicht
validieren**. Das ist kein Datenproblem, das sich durch eine bessere Quelle
lösen ließe — Bitcoin existiert erst seit 2009. Selbst wenn MVRV Zyklen perfekt
beschreibt, ist eine Stichprobe von 12 unabhängigen Jahresfenstern zu klein,
um das von Zufall zu unterscheiden.

Genau das erklärt auch die naiven p-Werte von 10⁻¹⁴¹: Sie entstehen aus 5.000
überlappenden Tagesbeobachtungen, die in Wahrheit ein paar Dutzend unabhängige
Episoden sind.

## Gegen die Challenge-Regeln

MVRV als Momentum-Filter (long wenn z-Score über Schwelle), 16 bp Kosten,
90-Tage-Fenster:

| Variante | Median-Rendite | Drawdown | Pass-Rate |
|---|---|---|---|
| long wenn z > −0,5 | +0,0 % | 17,3 % | 0,3 % |
| long wenn z > 0,0 | +0,0 % | 12,7 % | 0,1 % |
| long wenn z > +0,5 | +0,0 % | **5,7 %** | 0,5 % |
| BTC einfach halten | +11,4 % | 33,5 % | 0,0 % |

Die Median-Rendite von **exakt 0,0 %** ist kein Rundungsfehler: Bei einem
Signal, das sich über Monate kaum ändert, ist das typische 90-Tage-Fenster
vollständig flat. Bei der einzigen Variante, die das Drawdown-Limit einhält
(z > +0,5, 5,7 %), passiert schlicht nichts.

**Pass-Rate 0,1–0,5 %.** Schlechter als jede vorherige Idee, einschließlich
Vol-Targeting (20–25 %).

## Fazit

On-Chain-Daten beschreiben Marktzyklen — sie **prognostizieren** sie nicht auf
einer Zeitskala, die für eine 90-Tage-Challenge nutzbar wäre.

Drei Ergebnisse, in absteigender Härte:

1. **Miner-Verhalten und Netzwerknutzung liefern nichts.** Puell, Hash
   Ribbons, NVT, Adressen- und Transaktions-Momentum: kein Wert auch nur in
   der Nähe von Signifikanz, über 13,6 Jahre.
2. **MVRV hat eine klare, monotone Struktur — in der Gegenrichtung zur
   verbreiteten Lesart.** Das ist der interessanteste Einzelbefund, aber er
   fällt bei Bonferroni um das Zwanzigfache durch.
3. **Zyklusindikatoren sind mit 3,5 Zyklen prinzipiell nicht validierbar.**
   Das ist eine Grenze der Datenlage selbst, keine Frage der Methode.

Für die Challenge ist das der bislang deutlichste Fehlschlag: **Pass-Rate 0,1
bis 0,5 %.** Die Zeitskala passt nicht — On-Chain-Signale bewegen sich in
Quartalen bis Jahren, die Challenge läuft 90 Tage mit 6 % Drawdown-Limit.
