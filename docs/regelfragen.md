# Zwei Dinge aus der Google-Antwort — eines davon kippt alles

> ## 🛑 HINFAELLIG — DIE ECHTEN REGELN WIDERLEGEN DIESES DOKUMENT
>
> Das Vanquish-Regelwerk-PDF sagt woertlich: **„SPX, XSP and VIX can only be
> traded long as single-leg calls/puts. No spreads, no selling to open."**
> Dazu **Intraday Trailing Drawdown** (nicht statisch) und **keine
> Overnight-Positionen**.
> Damit ist jede Rechnung in diesem Dokument gegenstandslos.
> **Siehe [`vanquish_regeln.md`](vanquish_regeln.md).**

Der Text ist gut und trifft die richtigen Themen. Aber er enthält **einen
direkten Widerspruch zu deiner eigenen früheren Recherche**, und er zwingt
mich zu einer **Korrektur an meiner eigenen Messung**.

---

## 🛑 1. Der Widerspruch, der über das ganze Vorhaben entscheidet

**Deine frühere Recherche sagte:**

> *„Live-Konto (Funded): Sobald du die Evaluierung bestehst und finanziert
> bist, wechselt das System auf einen **Static Drawdown**. Die Verlustschwelle
> bleibt fest verankert."*

**Google sagt jetzt:**

> *„5 % **Trailing** Drawdown laufen auf jedem Konto separat auf Basis des
> jeweiligen **High-Water-Marks**."*

**Das kann nicht beides stimmen. Und es ist die wichtigste Zahl im ganzen
Angebot.** Gemessen an der Strategie (Wochen-Condor, 12 Monate):

| Nominal | Stopverlust | % Puffer | **STATISCH** überlebt / p.a. | **TRAILING** überlebt / p.a. |
|---|---|---|---|---|
| 4× | 2,25 % | 38 % | **95,1 % / +19,9 %** | 77,2 % / +16,2 % |
| 6× | 3,38 % | 56 % | **86,1 % / +29,5 %** | **15,9 % / −1,0 %** |
| 8× | 4,51 % | 75 % | **81,4 % / +39,9 %** | **13,1 % / −0,6 %** |
| 10× | 5,63 % | 94 % | 76,1 % / +49,9 % | **5,8 % / −4,3 %** |

**Bei statischem Boden funktioniert das Geschäft. Bei trailendem Boden
funktioniert es bei keiner einzigen Größe.** Ab 6× kippt die erwartete Rendite
ins Negative, weil der Boden jedem neuen Hoch nachläuft.

> **Kläre das zuerst. Alles andere ist danach entweder Feinschliff oder
> hinfällig.**

---

## 🛑 2. Korrektur an mir: ich habe die Konsistenzregel falsch gemessen

In [`vanquish.md`](vanquish.md) steht von mir: *„Die Konsistenzregel ist kein
Problem"* — belegt mit **10,1 %** Anteil des besten **Tages** am Jahresgewinn.

**Google präzisiert: Vanquish misst „Best Trade / Total Profits" — je TRADE,
nicht je Tag.** Das ist eine völlig andere Größe. Neu gemessen, Monatszyklen:

| | Anteil des besten **Trades** am Jahresgewinn |
|---|---|
| Median | **22,6 %** |
| 75. Perzentil | 35,4 % |
| 90. Perzentil | **63,5 %** |
| **Jahre über 30 %** | **38,3 %** |

**In gut einem Drittel der Jahre reißt du die Regel.** Meine frühere Entwarnung
war falsch — sie beruhte auf der falschen Bezugsgröße.

Und es wird schlimmer, je früher du auszahlen willst:

| Sammelzeitraum | Median | **Anteil über 30 %** |
|---|---|---|
| 3 Monate | 46,6 % | **100,0 %** |
| 6 Monate | 31,5 % | 50,0 % |
| 12 Monate | 22,6 % | 38,3 % |
| 24 Monate | 17,5 % | **3,2 %** |

Wer monatlich auszahlen will, reißt die Regel **immer**.

---

## Die Lösung: kürzere Zyklen, nicht längeres Warten

Die Regel bestraft Konzentration. Bei 12 Zyklen im Jahr trägt ein guter Zyklus
zwangsläufig ~10–20 %. Bei 50 Wochenzyklen sind es ~2 %.

SPX hat Wochenverfalle. Getestet mit an die Laufzeit angepassten Strikes
(gleiche Trefferwahrscheinlichkeit je Zyklus):

| Laufzeit | Zyklen/Jahr | Strikes | p.a. | Sharpe | bester Trade (Median) | **> 30 %** |
|---|---|---|---|---|---|---|
| **1 Woche** | **50** | **±2,4 %** | **+4,90 %** | **2,59** | **11,5 %** | **9,1 %** |
| 2 Wochen | 25 | ±3,5 % | +3,84 % | 2,09 | 15,7 % | 27,4 % |
| 1 Monat | 12 | ±5,0 % | +3,47 % | 2,08 | 22,6 % | 38,3 % |
| 2 Monate | 6 | ±7,1 % | +1,81 % | 1,07 | 41,2 % | 69,0 % |

**Wochenzyklen sind auf jeder Dimension besser:** mehr Rendite (+4,90 % statt
+3,47 %), höherer Sharpe (2,59 statt 2,08), und die Konsistenzregel wird von
einem Problem in 38 % der Jahre zu einem in 9 %.

Der Grund ist kein Trick: Du erntest Theta fünfzigmal im Jahr statt zwölfmal,
bei gleicher Trefferwahrscheinlichkeit je Zyklus.

*(Einschränkung: Wochenoptionen haben nahe am Verfall deutlich mehr Gamma. Ein
Wochenend-Gap trifft härter relativ zur eingenommenen Prämie. Mein Modell
rechnet die Verfallsabrechnung korrekt, aber nicht den genauen Zeitpunkt eines
Stops innerhalb des Zyklus.)*

---

## Wo Google sich irrt: die Konsistenz „multipliziert" sich nicht

> *„Wenn du auf mehreren Konten dieselbe Strategie fährst, kopierst du dir
> dieses Konsistenz-Problem auf alle Konten gleichzeitig."*

**Das stimmt nicht, solange je Konto gemessen wird.** Der Anteil „bester Trade
/ Gesamtgewinn" ist ein **Verhältnis** und damit skaleninvariant. Drei Konten
mit identischen Positionen haben jeweils **denselben** Anteil wie eines. Drei
mal 23 % ist 23 %, nicht 69 %.

Es würde nur dann schlimmer, wenn die Firma die Konten für die Konsistenz-
prüfung **zusammenfasst** — und dann wäre auch der Puffer-Vorteil aus
[`parallel.md`](parallel.md) weg. **Beides hängt an derselben Frage**, und die
steht unten.

---

## Wo Google recht hat

**Der Gesamtkapital-Deckel (300–500 k).** Drei 100-k-Konten liegen bei 300 k —
genau an der unteren Kante. Das ist die natürliche Obergrenze des Vorhabens
und der Grund, warum „einfach zehn Konten" nicht funktioniert.

**Die Shotgunning-Unterscheidung.** Getrennte Konten auf deinen echten Namen,
manuell gehandelt, ohne kontenübergreifendes Hedging — das ist die Grenze, die
zu respektieren ist. Automatisiertes gleichzeitiges Feuern identischer Orders
ist genau das Muster, das Risikosysteme markieren.

---

## Der Endstand, mit Wochenzyklen und statischem Boden

| Aufbau | überlebt | Ø p.a. je Konto | **3 Konten $/Jahr** |
|---|---|---|---|
| **3 Konten, 4× je Konto** | **95,1 %** | **+19,9 %** | **59.797 $** |
| 3 Konten, 6× je Konto | 86,1 % | +29,5 % | 88.355 $ |
| 3 Konten, 8× je Konto | 81,4 % | +39,9 % | 119.701 $ |

**Die erste Zeile ist die, die ich freigebe.** 95,1 % Überlebensrate heißt
umgekehrt: **etwa jedes zwanzigste Jahr verlierst du alle drei Konten
gleichzeitig** — sie sind perfekt korreliert. Das ist der Preis, und er ist
tragbar, weil eine neue Evaluierung 1.320 $ kostet und nicht 300.000 $.

---

## Die Fragen an Vanquish, in dieser Reihenfolge

```
1. Ist der Drawdown auf dem LIVE-Konto statisch oder trailing?
   Falls trailing: auf Basis des High-Water-Marks, End-of-Day oder intraday?
   -> Bei trailing ist das Vorhaben nicht durchfuehrbar. Zuerst klaeren.

2. Wird die Konsistenzregel je TRADE oder je TAG gemessen?
   Und ueber welchen Zeitraum -- je Auszahlung oder kumuliert?

3. Darf ich auf zwei oder drei gefundeten Konten dieselbe Strategie mit
   identischen Strikes gleichzeitig handeln -- oder werden die Konten fuer
   Risiko-, Konsistenz- und Auszahlungszwecke zusammengefasst?

4. Wie hoch ist die Obergrenze fuer gesamtes gefundetes Kapital je Person?

5. Sind Wochenoptionen (SPX Weeklys) zugelassen, und gibt es eine
   Mindesthaltedauer je Position?
```

Frage 5 ist neu und folgt aus dieser Rechnung: **Wenn Wochenoptionen nicht
zugelassen sind oder eine Mindesthaltedauer gilt, fällt die Lösung für die
Konsistenzregel weg** — und du bist zurück bei 38 % gerissenen Jahren.

---

*Skripte: `research/konsistenz.py` (Konsistenzregel je Trade),
`research/wochen.py` (Wochen- gegen Monatszyklen),
`research/endstand.py` (statisch gegen trailing mit Wochenzyklen).
Regelangaben aus zwei nicht übereinstimmenden Quellen, keine davon
unabhängig verifiziert.*
