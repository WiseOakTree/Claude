# Renko-Trail: Risikomanagement ist etwas anderes als ein Edge

Zweite Renko-Strategie dieses Projekts, diesmal mit dem Handelsmanagement als
Kern statt als Beiwerk. Spezifikation vor der Rechnung:
[`renko_trail_spec.md`](renko_trail_spec.md). 12 Märkte, 1 h,
2021-03 bis 2026-07, 8.578 bis 13.465 Trades je Variante, alle Zahlen nach
Kosten (16 bp je Roundtrip, 5 bp extra auf jede Stop-Ausführung, Funding).

---

> ## Der Befund in zwei Sätzen
>
> **Kein Managementbaustein erzeugt Erwartungswert.** Keine der sieben Stufen
> ist im Suchzeitraum *und* im Holdout positiv; die beste Stufe liefert **−6,75 bp
> je Trade** in der Suche und **−20,70 bp** im Holdout.
>
> **Aber das Management entscheidet, wie man verliert.** Ohne ausgeführten Stop
> überschreitet **jeder vierte Trade (25,8 %)** das geplante Risiko, der
> schlimmste um das **26-fache**. Mit hartem Stop sind es **1,6 %** und maximal
> das 1,9-fache — und die Tage über dem 3-%-Verlustlimit fallen von **7,1 auf 0,4**.
> Der harte Stop kostet dabei **0,16 bp je Trade**.

---

## Der eingebaute Fehler, mit dem alles anfing

Die bisherige Engine bemaß die Positionsgröße über eine **geplante**
Stop-Distanz von 2 Bricks und 0,5 % Kontorisiko — führte diesen Stop aber nie
aus. Der einzige Ausstieg war das Gegensignal.

Was das bedeutet, war vorher nicht gemessen. Jetzt ist es gemessen:

| | Anteil Trades mit Verlust > 1,2 R | größter Einzelverlust |
|---|---|---|
| **V0 — Stop geplant, nie ausgeführt** | **25,8 %** | **−25,82 R** |
| V1 — derselbe Stop, ausgeführt | 1,6 % | −1,87 R |

Ein Konto, das „0,5 % Risiko pro Trade" behauptet und in Wahrheit einen Trade
mit dem 26-fachen davon zulässt, hat kein Risikomanagement. Es hat eine
Absichtserklärung.

---

## Die Leiter

Jede Stufe fügt genau einen Baustein hinzu, damit jeder Effekt einzeln
zurechenbar ist. `bp/Trade` ist der Erwartungswert nach Kosten, `Ø R` das
Ergebnis in Vielfachen des geplanten Risikos.

### Frage A — Erwartungswert, Suchzeitraum (12 Märkte, bis 2024-12-31)

| | Aufbau | n | bp/Trade | t (Märkte) | Märkte + | Ø R | Treffer | Ø Gew. R | Ø Verl. R |
|---|---|---|---|---|---|---|---|---|---|
| V0 | Stop-and-Reverse, kein echter Stop | 13.465 | −15,18 | −4,98 | 1/12 | −0,029 | 34,8 % | 1,90 | −1,06 |
| V1 | + harter Stop | 13.465 | −15,33 | −4,75 | 1/12 | −0,027 | 31,1 % | 1,89 | −0,89 |
| **V2** | **diskrete Trades + harter Stop** | 8.578 | **−6,75** | −1,13 | 3/12 | +0,031 | 26,8 % | 2,77 | −0,97 |
| V3 | + Break-even nach 2 Bricks | 8.894 | −10,94 | −1,89 | 1/12 | +0,019 | 21,6 % | 3,03 | −0,81 |
| V4 | + Brick-Trailing | 10.479 | −22,19 | −6,78 | 0/12 | −0,052 | 32,1 % | 1,61 | −0,84 |
| V5 | + Teilmitnahme 50 % bei 2R | 10.479 | −18,00 | −5,59 | 0/12 | −0,047 | 33,0 % | 1,57 | −0,84 |
| V6 | + Zeitstop (voller Renko-Trail) | 10.479 | −18,00 | −5,59 | 0/12 | −0,047 | 33,0 % | 1,57 | −0,84 |

### Frage A — Holdout ab 2025-01-01 (11 Märkte, BTC ausgeschlossen)

| | Aufbau | n | bp/Trade | t (Märkte) | Märkte + |
|---|---|---|---|---|---|
| V0 | Stop-and-Reverse | 5.345 | −7,95 | −1,63 | 3/11 |
| V1 | + harter Stop | 5.345 | −11,37 | −2,32 | 3/11 |
| V2 | diskrete Trades + harter Stop | 3.521 | **−20,70** | −3,63 | 0/11 |
| V3 | + Break-even | 3.610 | −18,58 | −3,20 | 2/11 |
| V4 | + Trailing | 4.186 | −14,29 | −4,82 | 0/11 |
| V5 | + Teilmitnahme | 4.186 | −18,07 | −6,76 | 0/11 |
| V6 | + Zeitstop | 4.186 | −18,07 | −6,76 | 0/11 |

**Keine Stufe ist in beiden Zeiträumen positiv.** Die im Suchzeitraum beste
(V2, −6,75 bp) ist im Holdout die schlechteste (−20,70 bp) — genau das
Vorzeichenmuster, das in diesem Projekt schon mehrfach eine Regel erledigt hat.
Der einzige auffällig positive Einzelwert im Suchzeitraum, DOGE mit +45 bp
unter V2/V3, liegt im Holdout bei −1,1 bzw. +3,7 bp.

---

## Frage B — Risiko-Treue

Dieselben Trades, andere Frage: Landet der Verlust dort, wo er geplant war?

| | Aufbau | Verlust > 1,2 R | 5-%-Quantil R | größter Verlust |
|---|---|---|---|---|
| V0 | Stop geplant, nie ausgeführt | **25,8 %** | −1,84 | **−25,82 R** |
| V1 | + harter Stop | 1,6 % | −1,14 | −1,87 R |
| V2 | diskrete Trades + harter Stop | 1,5 % | −1,15 | −1,62 R |
| V3 | + Break-even | 1,3 % | −1,15 | −1,62 R |
| V4 | + Trailing | 1,0 % | −1,13 | −1,62 R |
| V5/V6 | + Teilmitnahme / Zeitstop | 1,0 % | −1,13 | −1,62 R |

Im Holdout dasselbe Bild: 26,1 % gegen 1,0–1,6 %, größter Verlust −12,85 R
gegen −1,35 R.

Das ist der Unterschied, um den es geht. Er hat nichts mit Treffergenauigkeit
zu tun und alles damit, dass ein Verlust eine **Obergrenze** hat.

---

## Der Preis der Sicherheit

Jede Stufe kostet oder bringt Erwartungswert. Suchzeitraum, bp je Trade:

| Schritt | Wirkung auf bp/Trade | was er einbringt |
|---|---|---|
| V0 → V1 harter Stop | **−0,16** | 25,8 % → 1,6 % Risikobrüche; 7,1 → 2,2 Tage über dem 3-%-Limit |
| V1 → V2 diskrete Trades | **+8,58** | ein Drittel weniger Trades (292 → 186 je Jahr und Markt) |
| V2 → V3 Break-even | −4,19 | 1,5 % → 1,3 % Brüche |
| V3 → V4 Trailing | **−11,25** | 3,6 → 0,5 Tage über dem Limit |
| V4 → V5 Teilmitnahme | +4,19 | nimmt einen Teil des Trailing-Schadens zurück |

**Der harte Stop ist praktisch gratis: 0,16 bp je Trade.** Das ist der
wichtigste Einzelbefund dieser Untersuchung. Der Baustein, der die Verlustseite
von „unbegrenzt" auf „begrenzt" umstellt, kostet ein Sechstel eines
Basispunkts.

**Das Trailing dagegen ist teuer: 11,25 bp je Trade.** Es schneidet die
Gewinner ab — der durchschnittliche Gewinn fällt von 3,03 R auf 1,61 R — und
erzeugt zusätzliche Trades (193 → 227 je Jahr und Markt), die alle Kosten
kosten. Wer ein Trailing einbaut, tauscht Erwartungswert gegen Ruhe. Das kann
richtig sein; es ist nur keine Verbesserung.

---

## Das Tageslimit — hier liegt der eigentliche Nutzen

Dieses Projekt hat an anderer Stelle gezeigt, dass **über 95 % aller
gescheiterten Prop-Challenges am Tagesverlustlimit scheitern**, nicht am
Drawdown ([`no_time_limit.md`](no_time_limit.md)). Genau diese Größe reagiert
auf Management:

| | Ø Tage mit Verlust > 3 % | Ø max. Drawdown | Ø Zeit im Markt |
|---|---|---|---|
| V0 | **7,1** | 36,5 % | 99,9 % |
| V1 | 2,2 | 34,0 % | 85,6 % |
| V2 | 4,2 | 30,7 % | 81,4 % |
| V3 | 3,6 | 30,1 % | 76,6 % |
| V4 | 0,5 | 31,6 % | 53,9 % |
| V5/V6 | **0,4** | 29,1 % | 53,9 % |

Vom Ausgangspunkt zur vollen Management-Stufe: **7,1 → 0,4 Tage**, ein Faktor
18. Im Holdout 2,4 → 0,0.

Das ändert nichts am Erwartungswert — aber es entfernt den Mechanismus, an dem
Challenges platzen. Beides gleichzeitig zu wissen ist der Punkt: Management
verhindert das Scheitern an der Regel, nicht das Verlieren am Markt.

---

## Drei Dinge, die man nicht erwartet

### 1. Der Stop hält bei 1,09 R, nicht bei 1,00 R

Über 6.190 Stop-Ausführungen in V1 liegt der durchschnittliche Verlust bei
**−1,087 R**, der Median bei −1,074 R. **79,2 %** aller Stops füllen schlechter
als −1,05 R. Ursache: Stop-Slippage (5 bp), Gebühren und Spread. Wer mit
„1 R Risiko" rechnet, plant systematisch 8–9 % zu knapp.

### 2. Die restlichen 1,6 % sind Kurslücken — und nur die

Von den 212 Trades in V1, die das geplante Risiko doch überschreiten, sind
**100 % Stop-Ausführungen**, kein einziger Signal-Ausstieg. Der Stop war
gesetzt, der Markt hat ihn übersprungen. Ein Stop begrenzt den Verlust, er
garantiert ihn nicht — im Mittel −1,27 R in diesen Fällen, im schlimmsten
Fall −1,87 R.

Das ist die ehrliche Antwort auf „mit Stop kann mir nichts passieren": doch,
aber statt 26 R sind es 1,9 R.

### 3. Der Zeitstop feuert kein einziges Mal

V6 ist **zahlengleich mit V5** — an jeder Stelle. Neben einem Trailing-Stop von
2 Bricks kommt kein Trade jemals auf 240 Bars, ohne vorher ausgestoppt zu
werden: **98,9 % aller Trades in V4–V6 enden am Stop**, 1,1 % am Signal.

Eine Regel, die nie feuert, ist keine Regel. In einem von Hand
zusammengestellten Regelwerk hätte man sie nie bemerkt.

---

## Wie die Trades enden (Suchzeitraum, %)

| | Signal | Stop |
|---|---|---|
| V0 | 99,9 | 0,0 |
| V1 | 54,0 | 46,0 |
| V2 | 40,7 | 59,2 |
| V3 | 27,1 | 72,9 |
| V4–V6 | 1,1 | **98,9** |

Ab V4 bestimmt nicht mehr das Signal, wann ein Trade endet, sondern der Stop.
Das Renko-Signal ist dann nur noch der Auslöser des Einstiegs — der Rest des
Trades gehört dem Management. Genau deshalb ist die nächste Frage die
entscheidende: Hätte dasselbe Management mit einem beliebigen Einstieg
dasselbe geliefert?

---

## Das Nullmodell: dieselbe Verwaltung, gewürfelte Einstiege

200 Ziehungen je Variante. Gleiche Anzahl Signale, gleiche Long/Short-Quote,
Zeitpunkte gleichverteilt über dieselben Bars, **identisches Management,
identische Kosten**. Nur der Einstiegszeitpunkt ist gewürfelt.

### Frage A — Erwartungswert

| | echt | Zufall Ø | 5 % | 95 % | **Perzentil** |
|---|---|---|---|---|---|
| V0 | −15,18 | −15,66 | −32,43 | −0,38 | 52,5 % |
| V1 | −15,33 | −16,33 | −24,89 | −6,46 | 57,5 % |
| V2 | −6,75 | −14,87 | −24,48 | −5,65 | **91,5 %** |
| V3 | −10,94 | −16,18 | −24,50 | −7,01 | 81,0 % |
| V4 | −22,19 | −22,44 | −28,12 | −16,49 | 51,5 % |
| V5 | −18,00 | −20,77 | −25,83 | −15,61 | 83,0 % |
| V6 | −18,00 | −21,10 | −26,37 | −16,08 | 83,5 % |

Im Holdout fällt V2 von 91,5 % auf **27,0 %** — schlechter als drei Viertel
aller Zufallsziehungen.

**Keine Stufe erreicht das 95. Perzentil.** Und der Zufall landet fast überall
auf demselben Wert wie das echte Signal: V0 real −15,18 gegen Zufall −15,66.
Anders gesagt:

> **Das Renko-Signal trägt nichts bei, was Zufallseinstiege nicht auch tragen.**
> Was die Kurve formt, ist das Management und sind die Kosten.

### Frage B — und hier wird es interessant

| | echt | Zufall Ø |
|---|---|---|
| V0 Verlust > 1,2 R | 25,8 % | 24,7 % |
| V1 Verlust > 1,2 R | 1,6 % | 1,8 % |
| V4 Verlust > 1,2 R | 1,0 % | 0,7 % |

**Die Risiko-Treue reproduziert der Zufall genauso.** Ein harter Stop drückt
die Risikobrüche auf ~1,8 % — bei gewürfelten Einstiegen exakt so wie bei den
echten.

Das ist keine Enttäuschung, das ist der Punkt:

> Risikomanagement wirkt **unabhängig davon, ob der Einstieg etwas taugt**.
> Genau deshalb ist es der verlässliche Teil — und genau deshalb ist es
> **kein Edge**. Es verbessert jeden Einstieg gleich, auch einen sinnlosen.

---

## Urteil nach den vorab festgelegten Kriterien

### Frage A — erzeugt Management einen Edge?

| Kriterium | Ergebnis |
|---|---|
| 1. bp/Trade > 0 im Suchzeitraum | ❌ beste Stufe −6,75 |
| 2. gleiches Vorzeichen im Holdout | ❌ V2: −6,75 → −20,70 |
| 3. über dem 95. Perzentil der Zufallseinstiege | ❌ höchstens 91,5 % |
| 4. t > 2,69 (Bonferroni, 7 Varianten) | ❌ bestes t = −1,13 |

**Alle vier verfehlt: kein Edge durch Management.** Wie vorab erwartet.

### Frage B — verbessert Management die Risiko-Treue?

| Kriterium | Ergebnis |
|---|---|
| 1. Anteil Verluste > 1,2 R sinkt gegenüber V0 | ✅ 25,8 % → 1,0–1,6 % |
| 2. 95-%-Quantil des Verlusts sinkt | ✅ −1,84 R → −1,13 R |

**Beide erfüllt.** Zusätzlich, ohne dass es Kriterium war: größter Einzelverlust
−25,82 R → −1,87 R, Tage über dem 3-%-Limit 7,1 → 0,4.

Wie vorab festgelegt werden A und B **nicht gegeneinander verrechnet**. Beides
gilt gleichzeitig.

---

## Was das praktisch heißt

1. **Der Stop gehört ausgeführt, nicht geplant.** Kosten: 0,16 bp je Trade.
   Nutzen: der größte Einzelverlust fällt um Faktor 14. Es gibt in dieser
   Untersuchung keinen billigeren Tausch.

2. **Erwarte davon keinen Gewinn.** Kein Managementbaustein hat den
   Erwartungswert positiv gemacht, und der Zufall schafft mit demselben
   Management dasselbe. Wer glaubt, ein besserer Stop mache aus einem
   Nullsignal ein System, hat die Wirkungsrichtung vertauscht.

3. **Trailing ist eine Entscheidung, keine Verbesserung.** 11,25 bp je Trade
   für 3,6 → 0,5 Limit-Tage. Auf einem Prop-Konto mit 3-%-Tageslimit kann das
   der richtige Tausch sein. Auf eigenem Kapital ohne Tageslimit ist es teuer.

4. **Rechne mit 1,09 R, nicht mit 1,00 R.** Wer 0,5 % Kontorisiko einstellt,
   verliert im Schnitt 0,545 % — und bei einer Kurslücke bis 0,94 %.

5. **Weniger Trades war der einzige Baustein mit positivem Vorzeichen.** Der
   Schritt von der Dauerposition zu diskreten Trades (V1 → V2) brachte
   +8,58 bp je Trade, indem er ein Drittel der Trades wegließ. Das ist
   dieselbe Richtung, in die auch [`einfach.md`](einfach.md) und
   [`drei_gruppen.md`](drei_gruppen.md) zeigen: **je mehr gehandelt wird, desto
   schlechter.**

---

## Einschränkungen

* **Ein Signal, eine Brick-Definition.** Geprüft wurde Management auf *diesem*
  Renko-Signal. Dass Management auf einem Signal *mit* Edge nichts ändert,
  folgt daraus nicht — nur, dass es selbst keinen erzeugt.
* **Der Zufallsvergleich ist konservativ gebaut.** Zufallseinstiege in den
  Dauerpositions-Stufen (V0/V1) erzeugen weniger Trades, weil die Engine
  gleichgerichtete Folgesignale ignoriert. Verglichen wird deshalb bp **je
  Trade**, nicht je Zeitraum.
* **Kurslücken sind Binance-Spot-Lücken.** An einer Börse mit dünnerem Buch
  oder bei Wochenendmärkten sind die 1,6 % Restrisiko größer.
* **Keine Positionsgrößen-Optimierung.** 0,5 % je Trade, 5× Hebelgrenze, fest.
* **BTC ist als Holdout verbraucht** und zählt im Holdout-Urteil nicht mit.
