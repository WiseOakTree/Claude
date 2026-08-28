# 200-$-Push auf dem 15-min-Chart, 1 Trade pro Tag

Spezifikation vor der Rechnung: [`push200_spec.md`](push200_spec.md).
BTC und ETH, 15 Minuten, 2021-03 bis 2026-07, **189.919 Bars / 1.979 Handelstage**.
Kostenmodell aus einem **echten Trade des Nutzers** abgeleitet: 7,98 bp Roundtrip.

---

> ## Der Befund in drei Zahlen
>
> **Brutto verliert die Regel fast nichts: −2,53 bp je Trade.** Der Markt gibt
> ungefähr null her — wie erwartet.
>
> **Netto verliert sie 11,55 bp.** Über 1.325 Trades im Suchzeitraum sind das bei
> deiner Positionsgröße **−26.412 $ — davon 20.329 $ reine Gebühren.**
> **77 % des Verlusts sind Reibung, nicht Marktrisiko.**
>
> **Nötig wären 58,1 % Trefferquote (heute sogar 69,7 %). Gemessen: 47,3 %** —
> und damit **unter** dem Zufallseinstieg zur gleichen Tageszeit (49,6 %).

---

## 1. Deine echten Kosten, aus deinem Trade gerechnet

| | |
|---|---|
| Nominal (0,387 BTC @ 79.272,30) | 30.678,38 $ |
| Bewegung 319,10 $ | 0,403 % |
| Bruttogewinn | 123,49 $ |
| angezeigter Netto | 99,00 $ |
| **Gebühr** | **24,49 $** (= 24 €) |
| **Roundtrip** | **7,98 bp** (3,99 bp je Seite) |

**Auf diesem Trade — einem Gewinner mit einer 319-$-Bewegung — hat die Gebühr
19,8 % des Bruttogewinns genommen.** Bei einer 200-$-Bewegung wären es 31,6 %
gewesen.

Das ist keine schlechte Kostenstruktur; 8 bp Roundtrip ist für einen
Privatanleger gut. Das Problem ist nicht der Preis, sondern das Verhältnis:

> **Kosten ÷ Ziel = der Anteil, der an die Börse geht, bevor du recht haben musst.**

---

## 2. 200 $ sind kein fester Wert

Ein Dollarbetrag ist über die Jahre etwas völlig Verschiedenes:

| Jahr | BTC Median | 200 $ entsprechen | Kosten als Anteil des Ziels |
|---|---|---|---|
| 2021 | 48.888 $ | 0,409 % | 19,6 % |
| 2022 | 23.150 $ | **0,864 %** | **9,3 %** |
| 2023 | 27.716 $ | 0,722 % | 11,1 % |
| 2024 | 64.208 $ | 0,311 % | 25,7 % |
| 2025 | 103.546 $ | **0,193 %** | **41,4 %** |
| 2026 | 70.322 $ | 0,284 % | 28,1 % |

Dieselbe Regel war 2022 ein Swing über fast ein Prozent und ist 2025 ein Scalp
über zwei Zehntel. **Die Regel driftet mit dem Kurs — sie muss in Prozent
formuliert sein, nicht in Dollar.**

---

## 3. Das Ergebnis

Hauptkombination: Push 200 $, Ziel 200 $, Stop 200 $, Momentum, Klammer bis
Tagesschluss.

| | n | Treffer | brutto bp | netto bp | t | Ø Dauer |
|---|---|---|---|---|---|---|
| **Suche**, ohne Kosten | 1.325 | 47,3 % | −2,53 | −2,53 | −1,57 | 2,0 h |
| **Suche**, deine Kosten | 1.325 | 47,3 % | −2,53 | **−11,55** | −7,05 | 2,0 h |
| Suche, reiner Taker (16 bp) | 1.325 | 47,3 % | −2,53 | −19,55 | −11,93 | 2,0 h |
| Suche, **Fade** (Kontrolle) | 1.325 | 51,1 % | +1,30 | −7,65 | −4,66 | 2,0 h |
| **Holdout**, ohne Kosten | 577 | 46,0 % | −1,98 | −1,98 | −2,04 | 0,8 h |
| **Holdout**, deine Kosten | 577 | 46,0 % | −1,98 | **−11,06** | −10,95 | 0,8 h |
| Holdout, Fade (Kontrolle) | 577 | 49,7 % | +0,02 | −8,98 | −8,86 | 0,8 h |

Die Regel feuert an **1.325 von 1.402 Tagen** (94 %) — sie ist also gut
umsetzbar, sie verdient nur nichts.

**Das Wichtigste steht in der Brutto-Spalte:** −2,53 bp. Der Markt nimmt dir
praktisch nichts weg. Was dich umbringt, ist der Sprung von −2,53 auf −11,55.

---

## 4. Der Push ist schlechter als ein Würfel

Kontrolle: derselbe Trade, dieselbe Klammer, dieselbe Tagesbegrenzung — aber der
Einstiegszeitpunkt zufällig irgendwann im Tag gewählt (36.400 Ziehungen):

| | Zufallseinstieg | nach dem 200-$-Push | Differenz | Binomial p |
|---|---|---|---|---|
| Suche | **49,6 %** | 47,3 % | **−2,3 pp** | 0,952 |
| Holdout | **48,5 %** | 46,0 % | **−2,5 pp** | 0,891 |

**Nach einem 200-$-Push einzusteigen ist schlechter, als blind zu einem
zufälligen Zeitpunkt einzusteigen.** Nicht dramatisch schlechter — aber es ist
das Gegenteil dessen, was die Idee unterstellt. Wer der Bewegung hinterherläuft,
kauft im Schnitt einen Tick zu spät.

Passend dazu: Die **Gegenrichtung** (Fade) hat die bessere Bruttozahl (+1,30 bp
gegen −2,53 bp) und eine Trefferquote von 51,1 %. Auch sie verliert nach Kosten
(−7,65 bp), aber sie zeigt, in welche Richtung der schwache Effekt zeigt:
**Rückkehr, nicht Fortsetzung.**

---

## 5. Break-even gegen gemessen

| | Ziel Ø | nötige Trefferquote | gemessen | Lücke |
|---|---|---|---|---|
| Suche | 55,4 bp | **58,1 %** | 47,3 % | **−10,8 pp** |
| Holdout | 22,9 bp | **69,7 %** | 46,0 % | **−23,7 pp** |

Im Holdout ist BTC teuer, 200 $ sind nur noch 22,9 bp — und damit muss man
**sieben von zehn Trades** gewinnen, nur um bei null zu landen. Bei einem
Würfel, der 48,5 % liefert.

---

## 6. In Geld, bei deiner Positionsgröße (0,387 BTC)

| | Trades | Ø je Trade | Summe | je Jahr | davon Gebühren |
|---|---|---|---|---|---|
| Suche (3,8 J.) | 1.325 | **−19,93 $** | −26.412 $ | −6.886 $ | **20.329 $** |
| Holdout (1,6 J.) | 577 | **−38,20 $** | −22.040 $ | −13.976 $ | **18.441 $** |

Ohne Gebühren wären es −6.084 $ bzw. −3.599 $ gewesen. **77 % bzw. 84 % des
Verlusts sind Gebühren.**

Anders gesagt: In 5,4 Jahren hättest du **38.770 $ an die Börse überwiesen**, um
am Ende 48.452 $ ärmer zu sein.

---

## 7. Empfindlichkeit — größere Ziele helfen, aber nicht genug

Symmetrisch (Ziel = Stop = Push), netto bp je Trade, deine Kosten:

| Push | Suche n | Suche Treffer | Suche netto | Holdout netto | Urteil |
|---|---|---|---|---|---|
| 200 $ | 1.325 | 47,3 % | −11,5 | −11,1 | beide negativ |
| 500 $ | 1.062 | 52,5 % | −4,3 | −9,6 | beide negativ |
| 1.000 $ | 731 | 51,8 % | −3,8 | **+4,3** | Vorzeichenwechsel |
| 2.000 $ | 311 | 57,0 % | **+10,2** | −6,1 | Vorzeichenwechsel |

**Keine einzige Zelle ist in beiden Zeiträumen positiv** — auch nicht im vollen
Gitter über Push × Stop (32 Kombinationen). Die beiden positiven Felder liegen
in *verschiedenen* Zeiträumen. Das ist exakt das Muster, an dem in diesem
Projekt schon dutzende Regeln gescheitert sind.

Aber die Richtung stimmt: Je größer das Ziel, desto kleiner der Kostenanteil.
Die Rechnung dazu:

> Damit die Gebühr **unter 10 % des Ziels** bleibt, muss das Ziel bei 8 bp
> Roundtrip mindestens **80 bp** groß sein — bei BTC zu 79.000 $ also
> **rund 6.300 $**, nicht 200 $.

Ein 6.300-$-Ziel ist kein 15-min-Scalp mehr. Es ist ein Swing über Tage.

---

## 8. Quermarkt

Dieselbe Regel in Prozent (0,25 % für Push, Ziel und Stop):

| | n | Treffer | brutto bp | netto bp |
|---|---|---|---|---|
| BTC Suche | 1.397 | 41,8 % | −4,09 | −13,26 |
| BTC Holdout | 577 | 47,0 % | −1,49 | −10,55 |
| ETH Suche | 1.401 | 40,3 % | −4,84 | −14,03 |
| ETH Holdout | 577 | 39,3 % | −5,34 | −14,55 |

Vier von vier negativ, in beiden Märkten, in beiden Zeiträumen.

---

## 9. Urteil nach den vorab festgelegten Kriterien

| Kriterium | Ergebnis |
|---|---|
| 1. $ je Trade nach Kosten > 0 in der Suche | ❌ −19,93 $ |
| 2. gleiches Vorzeichen im Holdout | ❌ (beide negativ, aber Kriterium 1 schon verfehlt) |
| 3. Trefferquote über dem Basissatz | ❌ **darunter**, p = 0,95 |
| 4. t > 2,50 | ❌ t = −7,05 |

**Alle vier verfehlt.** Es wird nichts nachjustiert.

---

## 10. Was das praktisch heißt

1. **Die Idee scheitert nicht am Markt, sondern an der Größe des Ziels.** Brutto
   −2,53 bp ist ein Münzwurf. Ein Ziel von 200 $ ist bei den heutigen
   BTC-Kursen zu klein, um 8 bp Reibung zu tragen.
2. **Ein Push ist kein Einstiegssignal.** Er ist messbar *schlechter* als ein
   zufälliger Einstiegszeitpunkt — in beiden Zeiträumen, in dieselbe Richtung.
3. **Wenn schon, dann in Prozent und größer.** Ein Ziel muss mindestens
   ~80 bp groß sein, damit die Gebühr unter 10 % bleibt. Bei BTC heute rund
   6.000 $. Das ist ein anderer Handelsstil.
4. **1 Trade pro Tag ist immer noch viel.** 1.325 Trades in 3,8 Jahren mal 8 bp
   sind **~3,1 % Reibung pro Jahr**, bevor irgendetwas passiert ist.
5. **Prüfe, ob deine 12 € eine feste oder eine prozentuale Gebühr sind.** Ist
   sie fest, kostet dieselbe Regel bei 10.000 $ Nominal **24,5 bp statt 8** — und
   die Gebühr frisst dann **97 % eines 200-$-Ziels**. Bei fester Gebühr ist
   Kleinhandeln rechnerisch ausgeschlossen.

---

---

## 11. Nachtrag: zweiter Trade — Gebühr geklärt, dafür etwas Neues

Ein zweiter Trade mit vollen Details (Short 0,434 BTC, 18./19.08.2026, 11 h
gehalten) beantwortet die offene Frage aus Punkt 10.5 und wirft eine neue auf.

### Die Gebühr ist prozentual — nicht fest

| | Betrag | Bezug | in bp |
|---|---|---|---|
| Opening fee | 11,23 $ | 28.080,49 $ | **4,00 bp** |
| Closing fee | 11,15 $ | 27.864,41 $ | **4,00 bp** |
| *Trade 1 zum Vergleich* | 24,49 $ | 30.678,38 $ | 7,98 bp Roundtrip |

**Exakt 4,00 bp je Seite, auf beiden Trades, bei verschiedenen Größen.** Damit
ist die Sorge aus Punkt 10.5 erledigt: Kleinhandeln wird nicht überproportional
teuer. Das Kostenmodell dieser Untersuchung war richtig.

### Aber: „Net PnL" ist nicht das, was ankommt

| | |
|---|---|
| Brutto (Kursdifferenz × Menge) | 216,08 $ |
| − beide Gebühren | 193,70 $ → angezeigt als **Net PnL 193,71 $** |
| angezeigter **Settled PnL** | **182,48 $** |
| **Differenz** | **11,23 $ — exakt die Opening fee, ein zweites Mal** |

Die tatsächliche Reibung ist damit **33,60 $ auf 28.080 $ = 11,97 bp**, nicht
7,98 bp. Entweder zieht die Abrechnung die Eröffnungsgebühr zweimal ab, oder
die Anzeige „Net PnL" ist um genau diesen Betrag zu optimistisch.

**Wer seine Ergebnisse nach „Net PnL" führt, überschätzt sich systematisch um
eine Eröffnungsgebühr je Trade.** Das ist mit einem Blick auf den
Kontostandsverlauf zu klären — und es lohnt sich:

| Kostenannahme | Kosten als Anteil eines 200-$-Ziels | Break-even-Trefferquote |
|---|---|---|
| 8,0 bp („Net PnL") | 31,6 % | **65,8 %** |
| **11,97 bp („Settled PnL")** | **47,3 %** | **73,6 %** |

Gemessen im Holdout: **46,0 %**. Zufallseinstieg: 48,5 %.

### Und der Hebel — die eigentliche Zahl fürs Konto

Beide Trades laufen mit **10x**. Der Hebel ändert nichts am Ergebnis je
Nominal, aber alles am Ergebnis je eingesetztem Kapital:

| | je Trade auf Nominal | **je Trade auf die Margin** |
|---|---|---|
| Suche | −11,55 bp | **−1,16 %** |
| Holdout | −11,06 bp | **−1,11 %** |

Die Regel feuert an 94 % aller Tage, also **rund 349 Trades im Jahr**:

> (1 − 0,0111)^349 = **−97,9 % der Margin pro Jahr.**

Das Konto ist nach einem Jahr praktisch leer — nicht durch einen Crash, sondern
durch 349-mal minus ein Prozent.

Zum Vergleich: Dein Beispiel-Trade brachte **+6,50 % auf die Margin**. Ein
guter Trade. Die Regel braucht −1,11 %, dreihundertneunundvierzig Mal.

### Was deine eigenen Trades zeigen

Beide gezeigten Trades haben **größere** Bewegungen mitgenommen als die Regel
vorsieht — 319 $ und 498 $ — und der zweite lief **11 Stunden**, nicht 15 Minuten.

Das ist bemerkenswert: Was du tatsächlich machst, liegt näher an dem, was die
Rechnung nahelegt (größere Ziele, weniger Trades), als die Regel, die du testen
wolltest. Die 200-$-Regel wäre für dich ein **Rückschritt**.

---

## Einschränkungen

* **Ein Bezugspunkt.** Der Push wird ab Tageseröffnung 00:00 UTC gemessen. Ein
  anderer Anker (rollierendes Fenster, Session-Start) gibt andere Zahlen —
  aber die Kostenarithmetik ändert sich dadurch nicht.
* **Kein Intrabar-Pfad.** Bei 15-min-Kerzen wird pessimistisch angenommen, dass
  der Stop vor dem Ziel getroffen wurde, wenn beide in derselben Kerze liegen.
* **Kein Funding**, weil die Position am selben Tag geschlossen wird.
* **Gebühr als Prozentsatz modelliert** — abgeleitet aus einem einzigen Trade.
  Siehe Punkt 5 oben.
