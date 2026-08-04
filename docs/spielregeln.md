# Die Spielregeln ändern — welche du kaufen musst und welche dir schon gehören

Nach 35 gescheiterten Ansätzen ist der Satz „man müsste die Spielregeln
ändern" die richtige Schlussfolgerung. Denn der Edge ist nicht der einzige
Parameter der Gleichung — er ist nur der, an dem alle herumsuchen.

Es gibt zwei Sorten Regeln.

---

## A. Regeln, die der Anbieter setzt

Gemessen in [`prop_rules.md`](prop_rules.md), hier nur die Rangfolge:

| Priorität | Regel | Wirkung auf die Pass-Rate |
|---|---|---|
| **1** | Tagesverlust-Limit ≥ 5 % oder keins | 40 % → **61–78 %** |
| **2** | Gewinnziel 6 % statt 10 % | 33 % → **49 %** |
| 3 | Zeitlimit ≥ 180 Tage oder keins | 33 % → 40 % |
| 4 | Drawdown-Limit | **ab 6 % wirkungslos** |
| 5 | statisch vs. trailing | wirkungslos |

Das 3-%-Tagesverlustlimit ist die Regel, die dich umbringt — **95 % aller
Fehlschläge kommen von dort**, nicht vom Drawdown. Ein Anbieter mit 5 %
Tagesverlust wäre rechnerisch das Anderthalbfache wert.

**Die Falle dabei:** Das Geschäftsmodell passt sich an. Wer lockere Limits
bewirbt, holt es sich über Gebühren, Gewinnbeteiligung oder
**Konsistenzregeln** zurück — und eine Konsistenzregel („kein Tag darf mehr
als X % des Gesamtgewinns beitragen") trifft genau diese Strategie, deren
Rendite aus wenigen großen Ausbrüchen kommt. Vor jedem Kauf gezielt danach
suchen.

Und der praktische Einwand: **Du hast Kraken bereits gekauft.** Die Regeln A
sind für diesen Versuch fix.

---

## B. Regeln, die dir schon gehören

Das ist der Teil, der bisher unterschätzt wurde. Vier Stellschrauben, keine
davon verlangt eine Prognose:

| Stellschraube | Wirkung | Status |
|---|---|---|
| Positionsgröße 0,5× statt 1,0× | 39,6 % → **49,4 %** | gemessen |
| Asset: nur BTC statt alle vier | 29,6 % → **49,4 %** | gemessen |
| Geduld (kein Zeitlimit nutzen) | 33,1 % → **40,2 %** | gemessen |
| **Anzahl der Versuche** | **siehe unten** | **neu** |

### Die vierte ist die stärkste — und die einzige, die nichts mit Trading zu tun hat

Kraken hat **kein Zeitlimit** und ein Versuch kostet **85 $**. Damit ist die
Challenge kein Einzelschuss, sondern ein Wiederholungsspiel. Das ändert die
Frage von „wie gut muss meine Strategie sein?" zu „wie oft kann ich antreten?"

Empirisch gerechnet — Versuche werden **verkettet**: Scheitert einer, startet
der nächste am Folgetag mit den echten Marktdaten. Damit steckt die
Korrelation aufeinanderfolgender Versuche drin.

| Versuche | BTC | ETH | SOL | XRP | Ø Einsatz (BTC) |
|---|---|---|---|---|---|
| 1 | 50,9 % | 27,5 % | 20,6 % | 23,2 % | 85 $ |
| **2** | **63,0 %** | 54,4 % | 32,7 % | 35,4 % | **114 $** |
| **3** | **78,7 %** | 88,9 % | 41,7 % | 51,8 % | **132 $** |
| 5 | 78,7 %\* | 90,5 %\* | 55,6 % | 72,6 % | 136 $ |

\* Sättigung ist ein **Datenartefakt**: Bei 1.948 Handelstagen Historie und
~120 Tagen je Versuch passen nur zwei bis drei Ketten in die Daten. Die
Zeile ist keine Obergrenze, sondern das Ende des Datensatzes.

Der durchschnittliche Einsatz liegt **weit unter** 3 × 85 $, weil die meisten
Ketten schon beim ersten oder zweiten Versuch enden. Auf BTC: **rund 132 $
erwarteter Gesamteinsatz für 78,7 % Erfolgswahrscheinlichkeit**, das sind
~168 $ je gefundetem Konto.

---

## Die Kontrolle, die den Optimismus dämpft

Die naive Rechnung wäre 1 − (1 − p)ⁿ. Die unterstellt **unabhängige**
Versuche. Sind sie nicht. Direkt gemessen:

| Asset | P(bestehen) | **P(2. besteht \| 1. gescheitert)** | Differenz |
|---|---|---|---|
| BTC | 60,1 % | **35,9 %** | **−24,2 pp** |
| ETH | 30,4 % | 42,7 % | +12,3 pp |
| SOL | 20,7 % | 15,7 % | −5,0 pp |
| XRP | 23,5 % | 16,8 % | −6,6 pp |

**Fehlschläge clustern.** Wer in einem zerhackten Markt scheitert, startet den
nächsten Versuch im selben zerhackten Markt. Auf BTC kostet das über
20 Prozentpunkte gegenüber der Unabhängigkeitsannahme — und genau deshalb
liegt der gemessene Wert bei 2 Versuchen bei 63,0 % statt der naiven 75,9 %.

Wer die naive Formel benutzt, verkauft sich selbst zu gute Zahlen. Der
Mechanismus funktioniert trotzdem, nur schwächer als er aussieht.

### Die Zeitasymmetrie, die dabei hilft

| Asset | Ø Dauer Erfolg | Ø Dauer Fehlschlag |
|---|---|---|
| BTC | 133 T | 107 T |
| ETH | 90 T | 74 T |
| SOL | 72 T | **42 T** |
| XRP | 61 T | **40 T** |

Fehlschläge sind **schneller** als Erfolge — das 3-%-Tageslimit greift früh
oder gar nicht. Ein gescheiterter Versuch kostet dich also nicht nur wenig
Geld, sondern auch überdurchschnittlich wenig Zeit. Das ist die einzige
Eigenschaft dieser Challenge, die strukturell auf deiner Seite steht.

---

## Was das zusammen bedeutet

**Die Regel, die zu ändern sich am meisten lohnt, ist nicht die Strategie,
sondern die Anzahl der Anläufe.** Von 50,9 % auf 63,0 % für 85 $ zusätzlich —
das ist ein größerer Sprung als alles, was 35 getestete Strategien,
8 Filter und XGBoost zusammen geliefert haben.

Drei ehrliche Einschränkungen:

1. **Die BTC-Zahlen sind der obere Rand.** SOL (41,7 % bei 3 Versuchen) und
   XRP (51,8 %) zeigen, wie es aussieht, wenn der S/R-Effekt schwach ist. Wenn
   der BTC-Vorsprung teilweise Glück war, liegst du näher an diesen Zahlen.
2. **Die Korrelation ist real und teuer.** Rechne nicht mit der naiven Formel.
3. **Gefundet ≠ verdient.** Das gefundete Konto unterliegt weiter dem
   Drawdown-Limit; die Ein-Jahres-Überlebensrate lag bei 8–48 %
   ([`trading_as_job.md`](trading_as_job.md)). Ein besserer Einstieg ist kein
   besserer Bestand. Die 168 $ je gefundetem Konto sind billig — was danach
   kommt, ist die eigentlich offene Frage.

---

*Skripte: `research/attempts.py` (Verkettung), `research/attempts2.py`
(Korrelation und Zeitasymmetrie).*
