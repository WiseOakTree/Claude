# MACD + Stochastik + Bollinger auf 4h — gemessen

Deine Entscheidung, also die konkrete Messung. Nicht die 120er-Familie von
damals, sondern **genau diese drei Indikatoren auf genau diesem Zeitrahmen**,
in beiden Lesarten, die in der Praxis gehandelt werden.

Daten: BTC/ETH/SOL 4h aus 1h-Kerzen, 2021-03 bis 2026-06. Suchzeitraum bis
2024-12, **Holdout 2025-01 bis 2026-06** (für diese Familie nie benutzt).
Kosten 8 bp je Seite = 16 bp je Roundtrip.

---

## Der wichtigste Befund kommt zuerst

Die Lehrbuch-Konfluenz für einen Long lautet:

> Kurs am **unteren Bollinger-Band** · Stochastik **unter 20** ·
> MACD-Histogramm **dreht nach oben**

Wie oft trat das auf BTC 4h zwischen 2021 und 2024 auf?

| Bedingung | Bars | Anteil |
|---|---|---|
| Kurs ≤ unteres Band | 508 | 6,0 % |
| Stochastik < 20 | 1.109 | 13,2 % |
| MACD-Histogramm steigt | 4.185 | 49,8 % |
| zwei davon gleichzeitig | 278 | 3,3 % |
| **alle drei gleichzeitig** | **0** | **0,0 %** |

**Null. In 3,8 Jahren, über 8.400 Kerzen, kein einziges Mal.**

Der Grund ist mechanisch: Wenn der Kurs das untere Band berührt und die
Stochastik unter 20 steht, **fällt** er gerade — und dann fällt auch das
MACD-Histogramm. Die dritte Bedingung widerspricht den ersten beiden. Sie
kann per Konstruktion nicht gleichzeitig erfüllt sein.

> **Das Setup, das in jedem Video gezeigt wird, existiert nicht.** Was Leute
> tatsächlich handeln, ist eine gelockerte Version davon — und die muss man
> getrennt messen.

### Gelockert

| Schwellen | Halten | Signale | bp/Trade | t |
|---|---|---|---|---|
| Stoch < 25, %B < 0,05 | 24 h | 26 | +7,3 | 0,06 |
| Stoch < 30, %B < 0,10 | 24 h | 183 | −8,0 | −0,15 |
| Stoch < 35, %B < 0,15 | 24 h | 468 | −10,1 | −0,28 |
| Stoch < 35, %B < 0,15 | 120 h | 468 | −5,5 | −0,03 |

Je mehr man lockert, desto mehr Signale — und desto klarer null.

---

## Die drei Indikatoren einzeln, 4h

| Indikator | 4 h | 24 h | 48 h | 120 h |
|---|---|---|---|---|
| MACD-Kreuzung | −14,3 | −28,5 | −28,0 | −7,5 |
| Stochastik-Kreuzung | −18,8 | −24,5 | −22,9 | −13,4 |
| Bollinger-Berührung | −21,7 | −37,3 | −43,4 | −75,9 |

*(bp je Trade nach Kosten, BTC 2021-24)*

**Alle zwölf Zellen negativ.** Und bei 4 h Haltedauer ist die Signifikanz
sogar deutlich — t = −2,85 / −3,29 / −3,26. Das ist kein „kein Edge", das ist
ein **messbar negativer** Edge auf kurzer Haltedauer.

### Liegt es an den Gebühren?

Nein. Dieselbe Rechnung mit **Kosten = 0**:

| Indikator | 24 h ohne Kosten | mit Kosten |
|---|---|---|
| MACD | −10,6 | −26,6 |
| Stochastik | −9,0 | −25,0 |
| Bollinger | −12,9 | −28,9 |

**Auch bei null Gebühren negativ.** Die Kosten machen es schlimmer, sie sind
nicht die Ursache.

---

## Die Trendlesart — die einzige mit einer positiven Zahl

> MACD-Linie über Signal · Kurs über dem Mittelband ·
> Stochastik kreuzt nach oben

| Markt | Zeitraum | Signale | bp/Trade | t |
|---|---|---|---|---|
| BTC | Suche 21-24 | 693 | **+30,0** | 0,20 |
| BTC | **Holdout 25-26** | 259 | **−15,0** | −0,10 |
| ETH | Suche 21-24 | 745 | **+69,4** | 0,39 |
| ETH | **Holdout 25-26** | 267 | **−93,0** | −0,34 |
| SOL | Suche 21-24 | 720 | −10,3 | −0,04 |
| SOL | Holdout 25-26 | 292 | +23,4 | 0,09 |

Alle sechs t-Werte liegen zwischen −0,34 und +0,39. **Zur Erinnerung: ab
etwa 2,0 spricht man von einem Befund.** Das Vorzeichen wechselt zwischen
Suche und Holdout bei BTC und ETH, und bei SOL in die andere Richtung — das
ist das Muster von Zufall, nicht von Struktur.

---

## Und jetzt die Gittersuche — dasselbe Muster wie überall

324 gültige Varianten (4 MACD-Einstellungen × 3 Stochastik × 3 Bollinger ×
2 Schwellen × 2 Lesarten × 3 Haltedauern):

- **54 %** der Varianten positiv im Suchzeitraum
- Median über alle: **+3,3 bp**

Die besten acht, gefunden auf 2021-24, dann auf dem Holdout nachgerechnet:

| | Suchzeitraum | Holdout 2025-26 |
|---|---|---|
| Mittelwert der besten 8 | **+61,2 bp** | **−359,7 bp** |

| Variante | Suche | Holdout |
|---|---|---|
| Reversion 8/21, Stoch 9, BB 20/2, 5 Tage | +82,1 | **−402,2** |
| Reversion 8/21, Stoch 14, BB 20/2 | +73,4 | **−402,2** |
| Reversion 8/21, Stoch 9, Stoch<30 | +67,2 | **−436,9** |
| Reversion 19/39, BB 50/2 | +45,2 | −40,7 |

**Der Vorzeichenwechsel ist vollständig.** Acht von acht. Das ist die
Rauschdecke aus [`tradingview.md`](tradingview.md) im Live-Betrieb: wer 324
Varianten durchprobiert und die beste nimmt, findet zuverlässig etwas, das
danach das Gegenteil tut.

---

## Wenn du es trotzdem handelst — das hier bewegt die Zahlen

Denn eine Sache ist wichtig: **Die Stellschrauben, die wirklich wirken, haben
nichts mit den Indikatoren zu tun.**

### Handelsfrequenz ist der Killer

| Umsetzung | Trades/Jahr | Gebühren p.a. bei 1× |
|---|---|---|
| Jede MACD-Kreuzung auf 4h | 170 | **27,2 %** |
| Konfluenz, sofort wieder raus | 180 | **28,9 %** |
| Konfluenz, **5 Tage halten** | **56** | **9,0 %** |

**Wer jedes 4h-Signal handelt, zahlt über ein Viertel des Kontos pro Jahr an
Gebühren.** Das ist mehr, als jede realistische Strategie verdient.

### Die Pass-Rate unter den echten Kraken-Regeln

10 % Ziel, 6 % statischer Drawdown, 3 % Tageslimit, kein Zeitlimit:

| | 0,25× | 0,35× | 0,50× | 1,00× |
|---|---|---|---|---|
| long+short, 5 Tage halten | **63,8 %** | 50,5 % | 37,4 % | 30,2 % |
| nur long, 5 Tage halten | 62,3 % | 44,2 % | 41,4 % | 28,1 % |
| nur long, 2 Tage halten | **65,9 %** | 50,2 % | 38,8 % | 25,8 % |
| **long+short, jedes Signal (1 Bar)** | **0,0 %** | **0,0 %** | **0,0 %** | **0,5 %** |

Drei Dinge stehen in dieser Tabelle:

1. **Die Positionsgröße bewegt die Pass-Rate um 34 Punkte** (63,8 % → 30,2 %).
   Die Wahl der Indikator-Parameter bewegt sie um ~0.
2. **Jedes Signal zu handeln liefert 0,0 %.** Nicht „schlecht" — *null*. Die
   Gebühren allein reißen den 6-%-Drawdown, bevor irgendein Trade greifen kann.
3. **Halten schlägt Handeln.** 56 Trades im Jahr statt 180, gleiche Signale.

> **Wenn du diese Kombination handelst, ist die einzige Entscheidung, die
> messbar etwas bringt: klein (0,25–0,35×), selten (5 Tage halten), und nicht
> jedes Signal.**

---

## 🛑 Aber die 50,5 % halten der Trennung nicht stand

Die Pass-Rate oben ist über die **gesamte** Historie gerechnet — also
überwiegend über den Zeitraum, auf dem ich die Lesart ausgesucht habe.
Getrennt sieht es so aus:

| Zeitraum | Pass-Rate bei 0,35× | Starts |
|---|---|---|
| Suchzeitraum 2021-24 | **57,8 %** | 270 |
| **Holdout 2025-26** | **9,3 %** | 43 |
| gesamt (die Zahl oben) | 50,5 % | 325 |

**57,8 % → 9,3 %.** Zum Vergleich: reiner Zufall liegt bei diesem Regelwerk
bei 37,5 %. Der Holdout liegt also nicht nur unter der Suche, sondern **weit
unter dem Würfel**.

### Und die Kontrollen, die gut aussahen

Ich habe zwei Kontrollen gerechnet, bevor die Trennung da war:

| Kontrolle | echt | Kontrollverteilung | p |
|---|---|---|---|
| Gleiche Zeitpunkte, **Richtung gewürfelt** (500×) | 50,5 % | Median 23,0 % | **0,028** |
| Signale **zirkulär verschoben** (500×) | 50,5 % | Median 23,9 % | **0,004** |

Beide p-Werte sehen nach einem Befund aus. **Sie sind trotzdem wertlos** —
denn 270 der 325 Startpunkte liegen im Suchzeitraum. Die Kontrollen messen
gegen Zufall, aber sie messen *innerhalb* der Daten, aus denen die Lesart
gewählt wurde. Ein signifikanter Kontrolltest im Suchzeitraum sagt nichts
darüber, ob die Sache hält.

> **Das ist genau die Falle, die dieses Projekt neunmal vorher gestellt hat.
> Der p-Wert war nie das Problem — der Zeitraum war es.**

---

## Die ehrliche Zusammenfassung

| Frage | Antwort |
|---|---|
| Gibt es das Lehrbuch-Setup? | **Nein — 0 Vorkommen in 3,8 Jahren** |
| Funktionieren die drei einzeln auf 4h? | Nein, alle zwölf Zellen negativ |
| Liegt es an den Gebühren? | Nein, auch bei 0 Kosten negativ |
| Funktioniert die Trendlesart? | t = 0,20 in der Suche, **−0,10 im Holdout** |
| Hilft Parameteroptimierung? | +61 bp → **−360 bp** out-of-sample |
| Pass-Rate unter Kraken-Regeln? | 57,8 % in der Suche → **9,3 % im Holdout** |
| Was hilft dann? | **Kleiner traden und seltener** — aber nicht genug |

Ich sage nicht, dass du es lassen sollst — das ist deine Entscheidung, und die
Kraken-Challenge ist bezahlt. Ich sage, was gemessen ist: **Der Edge dieser
Kombination ist innerhalb der Messgenauigkeit null, und die einzigen Hebel,
die wirken, sind Größe und Haltedauer** — die aber wirken für jede Strategie
gleich, auch für Münzwürfe.

Wenn du sie handelst, dann in der kleinen, seltenen Version — nicht in der aus
dem Video. Und mit der Zahl im Kopf, die als einzige aus unberührten Daten
kommt: **9,3 %.**

---

## Was ich nicht ausschließen kann

- **43 Startpunkte im Holdout sind wenig.** 9,3 % ist eine schlechte Zahl,
  aber mit breitem Konfidenzintervall. Sie widerlegt „funktioniert" — sie
  beweist nicht „funktioniert garantiert nie".
- **Ich habe eine bestimmte Umsetzung getestet.** Feste Haltedauer, kein Stop,
  keine Trendfilter höherer Zeitebene, kein Positionsmanagement. Wer die
  Indikatoren anders benutzt, handelt etwas anderes als das hier Gemessene.
- **Diskretionäre Anwendung ist nicht testbar.** Wenn jemand die drei
  Indikatoren ansieht und *dann* entscheidet, misst kein Backtest das. Das ist
  kein Argument dafür, dass es funktioniert — nur eine ehrliche Grenze.

---

*Skripte: `research/msb.py` (Indikatoren, beide Lesarten, Ereigniszahlen),
`research/msb2.py` (Gittersuche gegen Holdout), `research/msb3.py`
(ETH/SOL, Kostenzerlegung, Pass-Rate), `research/msb4.py` und
`research/msb5.py` (Kontrollen gegen Zufall und Verschiebung),
`research/msb6.py` (Frequenz, Größe, Haltedauer).*
