# Welchen Edge verlangt die Challenge? — die Umkehrung der Frage

Neun Ideen systematisch getestet, keine besteht. Die naheliegende
Schlussfolgerung wäre „die Challenge ist unmöglich". Statt einer zehnten Idee
hier die Frage, die ich früher hätte stellen sollen:

**Wie gut müsste eine Strategie sein — und wie gut ist gut genug?**

Methode: Strategien mit **vorgegebenem** Sharpe simulieren (40.000 Läufe je
Zelle, 90 Tage) und die Pass-Rate messen. Das gibt die Anforderung als Zahl,
unabhängig davon, welche Strategie man findet.

## Die Antwort: nicht unmöglich, aber brutal

| Sharpe | 10 % Vola | **15 %** | 20 % | 30 % | 50 % |
|---|---|---|---|---|---|
| **0,00** (reiner Zufall) | 2,5 % | **8,2 %** | 7,2 % | 0,5 % | 0,0 % |
| 0,50 | 4,5 % | 12,1 % | 10,7 % | 0,8 % | 0,0 % |
| 1,00 | 7,3 % | 17,9 % | 15,4 % | 1,2 % | 0,0 % |
| **1,33** (Vol-Prämie) | 10,0 % | **22,5 %** | 18,9 % | 1,5 % | 0,0 % |
| 2,00 | 16,9 % | 33,1 % | 26,9 % | 2,7 % | 0,0 % |
| 3,00 | 32,2 % | 51,9 % | 40,0 % | 4,7 % | 0,0 % |
| 5,00 | 70,7 % | 82,7 % | 66,5 % | 12,7 % | 0,0 % |

**Die Challenge ist nicht unmöglich — sie ist zu ~8 % Glückssache.** Selbst
eine Strategie ohne jeden Edge besteht in 8 von 100 Versuchen, einfach weil
Zufall manchmal +10 % ohne 6 % Drawdown liefert.

## Was für welche Erfolgsquote nötig wäre

| Ziel-Erfolgsquote je Versuch | benötigter Sharpe |
|---|---|
| 25 % | **1,47** |
| 50 % | **2,91** |
| 75 % | 4,41 |
| 90 % | 5,74 |

Zur Einordnung mit real dokumentierten Werten:

| | Sharpe | Pass-Rate |
|---|---|---|
| S&P 500, langfristig | 0,40 | 12,1 % |
| guter Hedgefonds | 1,00 | 18,7 % |
| **Volatilitätsprämie (hier gemessen)** | **1,33** | **23,0 %** |
| sehr guter systematischer Fonds | 2,00 | 33,7 % |
| Renaissance Medallion (geschätzt) | 3,00 | 51,4 % |

**Um die Challenge in der Hälfte der Versuche zu bestehen, bräuchte man
Medallion-Niveau.** Das ist der berühmteste Fonds der Geschichte, geschlossen
für Außenstehende, mit Infrastruktur und Personal jenseits jeder
Vergleichbarkeit.

## Die Bestätigung: meine Messung trifft die Theorie

Das Vol-Targeting kam empirisch auf **20–25 %** Pass-Rate
([`volatility_targeting.md`](volatility_targeting.md)). Die Simulation sagt für
Sharpe 1,33 bei optimaler Volatilität **23,6 %** voraus.

Zwei völlig unabhängige Wege, dasselbe Ergebnis. Das heißt: Der Backtest war
nicht kaputt und die Suche nicht unvollständig — **das Ergebnis ist genau das,
was die Mathematik für eine Strategie dieser Güte vorhersagt.**

## Der praktisch wichtigste Befund: Positionsgröße schlägt Edge

Man vergleiche zwei Zeilen der Tabelle:

| | Pass-Rate |
|---|---|
| **kein Edge** (Sharpe 0), Volatilität 15 % | **8,2 %** |
| **echter Edge** (Sharpe 1,33), Volatilität 30 % | **1,5 %** |

**Wer keinen Edge hat, aber richtig dimensioniert, schlägt den mit echtem Edge
und falscher Größe um den Faktor fünf.**

Die optimale Volatilität liegt über alle Sharpe-Niveaus bei **15–16 %
annualisiert**. Das ist eine konkrete, aus der Mathematik folgende Vorgabe,
die keinerlei Prognose voraussetzt — und sie erklärt rückwirkend, warum
Vol-Targeting das Beste war und jede Richtungsüberlagerung
([`ensemble_test.md`](ensemble_test.md)) es verschlechtert hat.

## Die Kosten

| Sharpe | Pass-Rate | Versuche bis Erfolg | Kosten bei 85 $ |
|---|---|---|---|
| 0,00 | 8,2 % | 12,2 | 1.037 $ |
| 1,00 | 18,9 % | 5,3 | 451 $ |
| **1,33** | **23,6 %** | **4,2** | **360 $** |
| 3,00 | 52,1 % | 1,9 | 163 $ |

## Fazit: beide Hälften der Aussage stimmen

**„Die Challenge ist unmöglich"** — nein, aber die realistische Erwartung ist
*ein Versuch von vier*, und der Großteil davon ist Glück, nicht Können. Der
Unterschied zwischen keinem Edge (8 %) und dem besten realistisch erreichbaren
(24 %) ist real, aber kleiner als die meisten annehmen.

**„Es muss einen Edge geben"** — den gibt es, und er ist in dieser
Untersuchung gefunden und vermessen: die **Volatilitäts-Risikoprämie**, Sharpe
1,33 nach realistischen Kosten, statistisch signifikant über 5,4 Jahre
([`volatility_premium.md`](volatility_premium.md)).

Beide Sätze zusammen ergeben die eigentliche Erkenntnis: **Der Edge existiert
— nur nicht dort, wo die Challenge ihn verlangt.** Er sitzt in Optionen, die
Kraken nicht anbietet, und arbeitet auf einer Zeitskala, die ein
90-Tage-Fenster mit 6-%-Limit nicht hergibt. Ein Sharpe-1,33-Verfahren ist
über Jahre eine sehr gute Anlage und über 90 Tage ein Münzwurf mit leichtem
Vorteil.

Das ist kein Scheitern der Suche. Es ist das Geschäftsmodell: Eine Hürde, die
Medallion-Niveau für eine 50-%-Quote verlangt, ist so gebaut, dass die Gebühr
die verlässliche Einnahme ist.
