# SL 3 Bricks, TP 6 Bricks, 1 % Risiko — die Klammer gerechnet

Ergänzung zu [`renko_macd_oi.md`](renko_macd_oi.md), jetzt mit dem vom Nutzer
definierten Ausstieg. Spezifikation vor der Rechnung:
[`renko_macd_klammer_spec.md`](renko_macd_klammer_spec.md).
6 Märkte, 1 h, 2023-01 bis 2026-07, alle Zahlen nach Kosten.

---

> ## Der Befund in drei Zahlen
>
> **Ein CRV von 1:2 ist ein fairer Münzwurf.** Von *jedem beliebigen Bar* aus
> wird +6 % vor −3 % in **34,7 %** der Fälle erreicht (Theorie: 3/(3+6) = 33,3 %).
> Die Klammer verbessert die Chancen nicht, sie teilt dieselben Chancen anders auf.
>
> **Der Break-even liegt bei 35,0 % Trefferquote. Gemessen wurden 31,7 %** —
> unter dem Münzwurf, nicht darüber.
>
> **CAGR: −9,0 % im Suchzeitraum, +0,3 % im Holdout.** 0 von 6 Konten im
> Suchzeitraum im Plus. Im selben Suchzeitraum machte Kaufen-und-Halten
> **+147 % pro Jahr**.

---

## 1. Warum das CRV die Frage nicht löst

Bei fester Klammer hängt der Erwartungswert an genau einer Zahl:

> E = p · 2R − (1 − p) · 1R − Kosten

Break-even ohne Kosten: **p = 33,33 %**. Und genau dort liegt auch die
Wahrscheinlichkeit, dass ein Kurs ohne Vorhersagbarkeit die 6-%-Marke vor der
3-%-Marke berührt — sie hängt nur vom Verhältnis der Abstände ab.

**Gemessen, von jedem Bar der sechs Märkte aus:**

| Markt | Suche long | Suche short | Holdout long | Holdout short |
|---|---|---|---|---|
| BTC | 39,4 % | 27,6 % | 34,2 % | 34,8 % |
| ETH | 36,3 % | 33,0 % | 34,7 % | 34,0 % |
| SOL | 33,8 % | 32,3 % | 32,8 % | 35,1 % |
| XRP | 34,4 % | 33,1 % | 31,9 % | 39,3 % |
| DOGE | 33,1 % | 34,4 % | 30,5 % | 38,2 % |
| ADA | 31,3 % | 36,7 % | 30,4 % | 38,5 % |
| **Mittel** | **34,7 %** | **32,8 %** | **32,4 %** | **36,7 %** |

Über 100.000 Startpunkte je Periode, unaufgelöst < 1,3 %. **Die Theorie stimmt
auf einen Prozentpunkt.** Wo die Abweichung auftritt, folgt sie der Marktrichtung
(BTC long 39,4 % im Bullenmarkt, ADA short 38,5 % im Bärenmarkt) — das ist
Drift, kein Chartmuster.

Daraus folgt: Ein anderes CRV zu wählen ändert nichts am Erwartungswert. Es
ändert nur, ob du oft klein gewinnst oder selten groß. **Der einzige Hebel ist
die Trefferquote über dem Münzwurf** — und die muss aus dem Einstieg kommen,
nicht aus der Klammer.

---

## 2. Trifft der Aufbau öfter als der Münzwurf?

| | Aufbau | n | Trefferquote | Basissatz | bp/Trade | Ø R | Binomial p |
|---|---|---|---|---|---|---|---|
| **K1** | OI-Filter, feste Klammer | 1.063 | **31,7 %** | 33,8 % | −30,25 | −0,101 | 0,927 |
| K3 | ohne OI-Filter, feste Klammer | 1.950 | 32,2 % | 33,8 % | −25,19 | −0,084 | 0,929 |

*(Suchzeitraum, 6 Märkte. Holdout: K1 35,5 % gegen Basissatz 34,5 %, p = 0,308.)*

**K1 ist der Aufbau vom Chart, exakt wie beschrieben.** Seine Trefferquote liegt
im Suchzeitraum **unter** dem Basissatz derselben Märkte und **unter** dem
kostenbereinigten Break-even von 35,0 %. Im Holdout liegt sie 1,0 Prozentpunkte
darüber — p = 0,308, also nicht von Rauschen zu unterscheiden.

### Wie die Trades enden (K1, Suchzeitraum)

| | Anteil | Ø Dauer | Ø Ergebnis |
|---|---|---|---|
| Ziel (+6 %) | 31,6 % | 1,5 Tage | **+1,96 R** |
| Stop (−3 %) | 68,0 % | 1,1 Tage | **−1,06 R** |
| Periodenende | 0,4 % | 0,8 Tage | −0,44 R |

Die Klammer funktioniert technisch einwandfrei: +1,96 R statt +2,00 R und
−1,06 R statt −1,00 R sind Kosten und Stop-Slippage, sonst nichts. **Das
Problem ist nicht der Ausstieg, sondern das Verhältnis 31,6 zu 68,0.**

### Eine Warnung zur Trefferquote von „Klammer + Drehen"

K2 und K4 (Klammer **plus** Drehen am Gegensignal) zeigen mit 36,7 % und 38,0 %
scheinbar bessere Trefferquoten und p-Werte von 0,024 bzw. < 0,001. **Diese
Zahlen sind nicht vergleichbar.** Bei K2 enden 22,7 %, bei K4 sogar 32,2 % der
Trades am Gegensignal — mit durchschnittlich **−0,36 R**. Diese Verlierer
verschwinden aus der Trefferquote, weil sie weder Ziel noch Stop erreicht haben.
Der Erwartungswert bleibt trotzdem negativ (−13,83 bzw. −17,07 bp).

Eine Trefferquote ist nur aussagekräftig, wenn jeder Trade an einer der beiden
Klammerseiten endet. Sonst misst man die Auswahl, nicht die Treffer.

---

## 3. CAGR

Ø über die sechs Märkte, 1 % Risiko je Trade, 0,33× Nominal:

| | Periode | Rendite | **CAGR** | Trades/Jahr | Ø R | Konten im Plus |
|---|---|---|---|---|---|---|
| **K1** | Suche (2 J.) | −16,5 % | **−9,0 %** | 89 | −0,101 | **0/6** |
| **K1** | Holdout (1,6 J.) | +0,5 % | **+0,3 %** | 79 | +0,012 | 3/6 |
| K2 | Suche | −11,3 % | −6,0 % | 117 | −0,046 | 1/6 |
| K2 | Holdout | +2,5 % | +1,5 % | 104 | +0,023 | 5/6 |
| K3 | Suche | −25,5 % | −13,9 % | 162 | −0,084 | 0/6 |
| K4 | Suche | −25,3 % | −14,1 % | 246 | −0,057 | 0/6 |

**Zum Vergleich, dieselben Zeiträume, Kaufen und Halten:**

| | BTC | ETH | SOL | XRP | DOGE | ADA | Ø CAGR |
|---|---|---|---|---|---|---|---|
| Suche | +136 % | +67 % | +336 % | +145 % | +112 % | +87 % | **+147 %** |
| Holdout | −21 % | −30 % | −45 % | −35 % | −62 % | −64 % | −43 % |

Der Suchzeitraum war einer der stärksten Bullenmärkte der Kryptogeschichte.
**Der Aufbau hat darin 9 % pro Jahr verloren.** Das ist der aussagekräftigste
Einzelbefund dieser Rechnung: Es lag nicht am Markt.

### Die Reibung allein

89 Trades im Jahr × 16 bp Roundtrip × 0,33 Nominal = **4,72 % des Kontos pro
Jahr**, bevor irgendein Trade richtig oder falsch war. Bei K4 (246 Trades) sind
es **13,0 % pro Jahr**.

---

## 4. Was ein positiver CAGR erfordern würde

Bei 89 Trades im Jahr, 1 % Risiko und ~0,05 R Kosten je Trade:

| Ziel-CAGR | nötig je Trade | nötige Trefferquote |
|---|---|---|
| **0 %** (nur Kosten decken) | ±0,000 R | **35,0 %** |
| +10 % | +0,113 R | **38,8 %** |
| +20 % | +0,226 R | **42,5 %** |
| +30 % | +0,339 R | **46,3 %** |

Gemessen: **31,7 %.** Münzwurf: **33,3 %.**

Für 20 % CAGR bräuchte der Einstieg also **9,2 Prozentpunkte über dem
Münzwurf** — dauerhaft, über Jahre, in sechs Märkten. Zur Einordnung: In diesem
Projekt wurden über 1.000 Varianten geprüft; kein einziges Richtungssignal hat
je mehr als 1–2 Prozentpunkte über dem Zufall gehalten, und keines davon hat
den Holdout überstanden.

**Es gibt zwei Stellschrauben, und nur zwei:**

1. **Trefferquote** — muss aus dem Einstieg kommen. Der MACD auf Renko-Bricks
   liefert sie nicht (31,7 % gegen 33,8 % Basissatz).
2. **Anzahl der Trades** — sie multipliziert *beides*, den Edge und die Kosten.
   Ohne Edge ist weniger handeln immer besser: K1 (89 Trades) verliert 9 %/Jahr,
   K4 (246 Trades) verliert 14 %/Jahr. Dieselbe Idee, dreimal so oft gehandelt,
   fast doppelter Verlust.

---

## 5. Empfindlichkeit — und warum daraus nichts ausgewählt wird

bp je Trade, Zeilen = Stop in Boxen, Spalten = Ziel in R:

**Suchzeitraum**

| Stop \ Ziel | 1R | 2R | 3R | 4R |
|---|---|---|---|---|
| 2 Boxen | −9,8 | −16,1 | −15,2 | −19,0 |
| **3 Boxen** | −12,9 | **−23,4** | −4,5 | **+2,4** |
| 4 Boxen | −25,8 | −23,9 | −24,6 | −34,2 |

**Holdout**

| Stop \ Ziel | 1R | 2R | 3R | 4R |
|---|---|---|---|---|
| 2 Boxen | −13,9 | −6,8 | −1,9 | −1,8 |
| **3 Boxen** | −6,4 | **+1,6** | −16,5 | −9,9 |
| 4 Boxen | **+11,8** | **+29,9** | +2,0 | +5,6 |

**Keine einzige Zelle ist in beiden Zeiträumen positiv.** Die beste Zelle der
Suche (3 Boxen / 4R: +2,4) liefert im Holdout −9,9. Die beste des Holdouts
(4 Boxen / 2R: +29,9) liefert in der Suche −23,9.

Die Trefferquoten dagegen sind bemerkenswert stabil — und exakt dort, wo die
Barrieren-Arithmetik sie hinlegt: 1R ≈ 50 %, 2R ≈ 33 %, 3R ≈ 25 %, 4R ≈ 20 %.
**Das ist die Formel p ≈ Stop/(Stop+Ziel), nicht der MACD.**

---

## 6. Urteil nach den vorab festgelegten Kriterien

| Kriterium | Ergebnis |
|---|---|
| 1. Trefferquote über kostenbereinigtem Break-even (35,0 %) | ❌ **31,7 %** |
| 2. bp/Trade > 0 in der Suche **und** gleiches Vorzeichen im Holdout | ❌ −30,25 / +4,28 |
| 3. Trefferquote signifikant über dem Basissatz | ❌ p = 0,927 (unterhalb) |
| 4. t > 2,50 (Bonferroni, 4 Kombinationen) | ❌ t = −2,67 |

**Alle vier verfehlt.** Es wird nichts nachjustiert — das stand vorher fest.

---

## 7. Was daran trotzdem richtig ist

Damit das nicht untergeht: **Die Ausstiegsdefinition ist gut.** Sie ist besser
als das, was vorher da war, und sie hat drei messbare Vorzüge:

* **Die Klammer hält.** +1,96 R am Ziel, −1,06 R am Stop — die Abweichung von
  ±2,00/−1,00 sind ausschließlich Kosten und Slippage. Kein einziger Trade ist
  durch eine Kurslücke weiter gelaufen als geplant.
* **Feste Klammer schlägt „Drehen am Gegensignal" im Risikoprofil**: 9,5 gegen
  13,2 Tage über dem 3-%-Limit, 30,1 % gegen 33,3 % Zeit im Markt.
* **1 % Risiko bei 0,33× Nominal ist konservativ dimensioniert.** Der maximale
  Drawdown liegt bei 24 % — bei einem System ohne jeden Edge. Mit 3 % Risiko
  wären daraus rechnerisch ~70 % geworden.

Das Risikomanagement ist also nicht das Problem. Es tut genau das, was es soll —
es kann nur nicht ersetzen, was fehlt: eine Trefferquote über 35 %.

---

## Einschränkungen

* **Basissatz brutto gerechnet** (ohne Kosten) — es ist eine Kursfrage, keine
  Handelbarkeitsfrage. Der Vergleich Strategie-gegen-Basis ist dadurch
  konservativ zu Gunsten der Strategie.
* **Überlappende Startpunkte** im Basissatz (jeder Bar). Der Punktschätzer ist
  unverzerrt, das Konfidenzintervall wäre breiter als bei unabhängigen Ziehungen.
* **Horizont 90 Tage** für den Basissatz; unaufgelöste Fälle < 1,3 %.
* **Nur 2023-01 bis 2026-07**, begrenzt durch die OI-Daten.
* **Stop zählt vor Ziel**, wenn beide in derselben Stunde liegen. Ohne Tickdaten
  ist das die konservative Wahl; die wahre Trefferquote liegt geringfügig höher.
