# Wochenend-Saisonalität — die Prämisse stimmt, der Filter nicht

**Idee (Vorschlag des Beraters):** Am Wochenende zieht die institutionelle
Liquidität ab. Ausbrüche in dünnen Büchern sind überdurchschnittlich oft
Fehlausbrüche. Also: Signale zwischen **Freitag 22:00 und Sonntag 22:00 UTC**
verwerfen.

Geprüft auf dem einzigen Signal, das diese Untersuchung überlebt hat:
S/R-Ausbruch nach ≥6 Berührungen, 1h, BTC/ETH/SOL/XRP, Halten 48 h,
0,5× Positionsgröße, 16 bp Kosten je Roundtrip.

## 1. Die Prämisse stimmt — und zwar auf allen vier Assets

| Asset | Volumen WE / Werktag | Bewegung WE / Werktag |
|---|---|---|
| BTC | 0,60× | 0,64× |
| ETH | 0,63× | 0,70× |
| SOL | 0,69× | 0,78× |
| XRP | 0,65× | 0,75× |

Am Wochenende wird rund ein Drittel weniger gehandelt und der Kurs bewegt sich
rund ein Viertel weniger. Das ist keine Vermutung, das ist gemessen.

**Aber:** Weniger Liquidität heißt nicht automatisch schlechtere Ausbrüche.
Das ist der Sprung, den die Idee macht — und der muss separat belegt werden.

## 2. Effekt je Ereignis: der Richtung nach ja, statistisch nein

Effekt = mittlere Rendite über 24 h nach dem Ausbruch, in Basispunkten,
p-Wert überlappungskorrigiert.

**Suchzeitraum (bis 2024-12)**

| Asset | Wochenende | n | p | Werktag | n | p | Differenz |
|---|---|---|---|---|---|---|---|
| BTC | +29,6 | 60 | 0,241 | +45,4 | 202 | 0,047 | −15,9 |
| ETH | +3,0 | 67 | 0,938 | +46,9 | 232 | 0,043 | −44,0 |
| SOL | −30,8 | 83 | 0,575 | +49,1 | 231 | 0,134 | −79,9 |
| XRP | +26,9 | 106 | 0,398 | −7,2 | 288 | 0,803 | **+34,1** |

**Holdout (ab 2025-01)**

| Asset | Wochenende | n | p | Werktag | n | p | Differenz |
|---|---|---|---|---|---|---|---|
| BTC | +33,9 | 35 | 0,377 | +63,8 | 107 | 0,002 | −29,9 |
| ETH | +35,4 | 21 | 0,644 | +29,0 | 73 | 0,513 | **+6,4** |
| SOL | −65,2 | 37 | 0,156 | +0,0 | 121 | 0,999 | −65,2 |
| XRP | −26,4 | 49 | 0,617 | −54,1 | 155 | 0,114 | **+27,7** |

Auf 3 von 4 Assets im Suchzeitraum und 2 von 4 im Holdout sind
Wochenendausbrüche schwächer. **Kein einziger Wochenend-Wert ist für sich
signifikant** (p zwischen 0,156 und 0,938) — bei 21 bis 106 Ereignissen je
Zelle ist das auch nicht zu erwarten. Die Richtung stimmt öfter als nicht,
mehr sagt diese Tabelle nicht aus.

## 3. Als Filter sieht es zunächst gut aus

Pass-Rate nach den korrigierten Challenge-Regeln (kein Zeitlimit, statischer
Drawdown, Ziel gilt sobald berührt), volle Historie, 0,5×:

| Asset | ohne Filter | mit Wochenendfilter | Änderung |
|---|---|---|---|
| BTC | 49,4 % | 55,2 % | +5,9 pp |
| ETH | 26,7 % | 30,6 % | +3,9 pp |
| SOL | 20,0 % | 29,8 % | +9,9 pp |
| XRP | 22,5 % | 20,8 % | −1,7 pp |
| **Mittel** | **29,6 %** | **34,1 %** | **+4,5 pp** |

3 von 4 Assets besser, im Mittel +4,5 Prozentpunkte. Das ist das
konsistenteste Bild, das ein Filter in dieser Untersuchung je geliefert hat.

## 4. Die entscheidende Kontrolle: gegen 200 Zufallsfilter

Der Wochenendfilter entfernt rund ein Viertel aller Signale. **Weniger zu
handeln ist bei einer Kostenschwelle von 16 bp für sich genommen schon gut.**
Die Frage ist also nicht „hilft der Filter?", sondern:

> Hilft er **mehr** als das Weglassen einer beliebigen gleich großen
> Zufallsauswahl von Signalen?

Dafür: 200 Zufallsfilter, die je Asset und Zeitraum **exakt gleich viele**
Signale entfernen wie der Wochenendfilter. Perzentil = Anteil der
Zufallsfilter, die der Wochenendfilter schlägt.

| Asset | Zeitraum | ohne | Wochenende | Zufall (Mittel) | Streuung | **Perzentil** |
|---|---|---|---|---|---|---|
| BTC | Suchzeitraum | 49,3 % | 57,4 % | 43,2 % | 9,8 | **96 %** |
| BTC | Holdout | 49,5 % | 49,7 % | 51,5 % | 3,4 | **22 %** |
| ETH | Suchzeitraum | 33,8 % | 32,7 % | 32,0 % | 3,8 | 42 % |
| ETH | Holdout | 8,6 % | 25,3 % | 17,8 % | 10,8 | 74 % |
| SOL | Suchzeitraum | 18,9 % | 30,7 % | 21,5 % | 5,3 | **94 %** |
| SOL | Holdout | 11,5 % | 16,0 % | 10,2 % | 5,5 | 84 % |
| XRP | Suchzeitraum | 21,8 % | 20,8 % | 17,0 % | 5,2 | 76 % |
| XRP | Holdout | 22,2 % | 18,8 % | 20,1 % | 7,4 | 30 % |

Zusammengefasst:

| | ohne | Wochenendfilter | Zufallsfilter | Vorsprung | mittleres Perzentil |
|---|---|---|---|---|---|
| Suchzeitraum | 30,9 % | 35,4 % | 28,5 % | **+6,9 pp** | **77 %** |
| **Holdout** | 23,0 % | 27,4 % | 24,9 % | **+2,5 pp** | **53 %** |

## 5. Das Urteil

**Im Suchzeitraum ist der Effekt echt.** +6,9 pp gegenüber Zufallsfiltern
gleicher Größe, mittleres Perzentil 77 % — der Filter schlägt drei von vier
Zufallsauswahlen. Das ist deutlich mehr als „weniger handeln hilft".

**Im Holdout ist er Münzwurf.** +2,5 pp und ein mittleres Perzentil von
**53 %** — der Wochenendfilter ist dort statistisch nicht von einer beliebigen
Zufallsauswahl zu unterscheiden. Die Einzelwerte streuen wild (22 %, 74 %,
84 %, 30 %), was genau das Muster von Rauschen ist.

**Damit ist der Wochenendfilter der achte Filter, der out-of-sample
durchfällt** — nach Mindest-Durchbruch, Rollenlogik, Cooldown, XGBoost,
Heikin-Ashi-Richtung, Session-Filter und Tagesbremse.

Er ist dabei der am wenigsten widerlegte von allen: Er kippt nicht ins
Negative, er liegt in beiden Zeiträumen knapp über dem Zufall. Nur eben im
Holdout so knapp, dass man daraus keine Regel bauen darf. **Ein Filter, der
den Zufall um 3 Prozentpunkte schlägt, wenn die Streuung 3–11 Punkte beträgt,
ist keine Erkenntnis.**

## 6. Warum die Prämisse stimmen und der Filter trotzdem scheitern kann

Das ist der lehrreiche Teil. Beides ist gleichzeitig wahr:

- Am Wochenende ist die Liquidität dünner (0,60–0,69×) — **belegt**.
- Ausbrüche am Wochenende sind deshalb systematisch schlechter — **nicht belegt**.

Dünne Bücher machen Bewegungen *kleiner*, nicht *falscher*. Die Verluste aus
Fehlausbrüchen schrumpfen am Wochenende genauso wie die Gewinne aus echten
Ausbrüchen. Übrig bleibt hauptsächlich, dass man ein Viertel weniger handelt —
und das kann jeder Zufallsfilter auch.

---

*Skript: `research/weekend.py` (Prämisse, Effekt, Filter),
`research/weekend_ctrl.py` (Kontrolle gegen 200 Zufallsfilter).*
