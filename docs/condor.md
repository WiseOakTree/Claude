# Der echte Iron Condor — Näherung ersetzt, Zahlen korrigiert

> ## 🛑 HINFAELLIG — DIE ECHTEN REGELN WIDERLEGEN DIESES DOKUMENT
>
> Das Vanquish-Regelwerk-PDF sagt woertlich: **„SPX, XSP and VIX can only be
> traded long as single-leg calls/puts. No spreads, no selling to open."**
> Dazu **Intraday Trailing Drawdown** (nicht statisch) und **keine
> Overnight-Positionen**.
> Damit ist jede Rechnung in diesem Dokument gegenstandslos.
> **Siehe [`vanquish_regeln.md`](vanquish_regeln.md).**

Zwei Einwände haben meine Näherung erledigt:

1. **Delta-Drag / negatives Gamma** — der Condor blutet durch die
   Delta-Verschiebung, lange bevor der Flügel greift.
2. **Skew** — Puts sind teurer, der symmetrische Flügelkauf frisst den Kredit.
   Realistisch 20–25 % der Straddle-Prämie, nicht 40 %.

Statt darüber zu diskutieren, habe ich die Näherung durch ein **echtes Modell**
ersetzt: explizite Strikes, Black-Scholes mit VIX als ATM-Vol, linearer
Volatilitäts-Skew, **Abrechnung am Verfall aus der tatsächlichen Bewegung**
(damit ist der Delta-Drag vollständig drin — kein Hedge).

---

## 🛑 Ergebnis: du hattest recht, und es ist schlimmer als deine Schätzung

| Strangle | Flügel | Skew | Kredit | Straddle | **Anteil** |
|---|---|---|---|---|---|
| ±3,0 % | 0,8 % | 0,0 | 0,349 % | 4,23 % | **8,3 %** |
| ±3,0 % | 0,8 % | 0,7 | 0,339 % | 4,23 % | **8,0 %** |
| ±3,0 % | 0,8 % | 1,0 | 0,327 % | 4,23 % | **7,7 %** |
| ±2,0 % | 0,8 % | 0,7 | 0,450 % | 4,23 % | 10,6 % |
| ±5,0 % | 0,8 % | 0,7 | 0,174 % | 4,23 % | **4,1 %** |

**Nicht 40 % (meine Zahl), nicht 20–25 % (deine), sondern 4–11 %.**

### Aber der Skew ist nicht der Hauptgrund

Von Skew 0,0 auf 1,0 fällt der Anteil nur von 8,3 % auf 7,7 %. **Weniger als
ein Prozentpunkt.**

Der Grund: Ein Iron Condor ist **symmetrisch**. Du verkaufst einen teuren Put
*und kaufst einen noch teureren, weiter aus dem Geld liegenden Put*. Die
Skew-Effekte auf beiden Legs heben sich weitgehend auf. Auf der Call-Seite
dasselbe mit umgekehrtem Vorzeichen.

**Der eigentliche Killer ist die Flügelbreite.** Ein 0,8-%-Flügel liegt so nah
am Short-Strike, dass die gekaufte Option fast so viel kostet wie die
verkaufte. Deine Schlussfolgerung stimmt — die Begründung liegt in der
Geometrie, nicht in der Skew.

*(Ironischerweise heißt das: Mein vorheriger Rat „enge Flügel" war aus einem
Grund richtig — Risikobudget — und aus einem anderen falsch: enge Flügel
zerstören den Kredit.)*

---

## Der Delta-Drag, gemessen

Ohne Hedge, Abrechnung aus der echten Bewegung:

| Strangle | Flügel | p.a. | Vol | Sharpe | Trefferquote | schlecht. Monat |
|---|---|---|---|---|---|---|
| ±2,0 % | 0,8 % | **−0,24 %** | 1,26 % | **−0,18** | 42,0 % | −0,48 % |
| ±3,0 % | 0,8 % | +0,13 % | 1,22 % | 0,11 | 57,1 % | −0,62 % |
| ±4,0 % | 1,5 % | +1,30 % | 1,77 % | 0,74 | 74,8 % | −1,14 % |
| **±5,0 %** | **1,5 %** | **+1,52 %** | 1,51 % | **1,01** | **85,7 %** | −1,28 % |

**Enge Strangles sind ohne Hedge verlustbringend.** Bei ±2 % liegt der Sharpe
bei −0,18. Das ist der Delta-Drag, genau wie du ihn beschrieben hast.

## Und dein zweiter Punkt — früh raus — ist die Lösung

| Stop | p.a. | Vol | **Sharpe** | schlechtester Monat |
|---|---|---|---|---|
| kein Stop | +1,52 % | 1,51 % | 1,01 | −1,28 % |
| 75 % vom Max | +1,79 % | 1,33 % | 1,34 | −0,96 % |
| 50 % vom Max | +2,14 % | 1,11 % | 1,92 | −0,64 % |
| **35 % vom Max** | **+2,36 %** | 0,98 % | **2,38** | **−0,45 %** |

**Der Stop mehr als verdoppelt den Sharpe.** Dein Satz *„du musst das
Delta-Risiko über eiserne Stop-Markierungen kappen, bevor die vollen 0,8 %
greifen"* ist damit gemessen, nicht vermutet.

*(Warnung an mich selbst: 35 % ist der beste von fünf geprüften Werten — die
Bestes-von-N-Falle, die ich in diesem Projekt fünfmal dokumentiert habe.
Rechne mit dem 50-%-Wert: Sharpe 1,92.)*

---

## Näherung gegen echtes Modell

| | Näherung | **echt** |
|---|---|---|
| Anteil der Straddle-Prämie | 40–55 % | **4–11 %** |
| Rendite p.a. auf Nominal | +6,2 % | **+2,4 %** |
| Sharpe | 2,55 | **2,38** |
| Delta-Drag enthalten | **nein** | ja |
| Skew enthalten | **nein** | ja |

**Der Sharpe hält. Die Rendite je Einheit Nominal ist weniger als die Hälfte.**

Das ist die wichtigste Zeile: Die *Qualität* der Strategie war richtig
geschätzt, die *Ertragsdichte* nicht. Und das lässt sich über mehr Nominal
aufholen — was bei definierten Spreads geht, weil die Margin die
Spread-Breite ist, nicht das Nominal.

---

## Die korrigierte Endrechnung

Konfiguration: **Strangle ±5 %, Flügel 1,5 %, Stop bei 35 % des
Maximalverlusts.** Kredit 0,323 % des Nominals je Zyklus, Maximalverlust
1,18 % — durch den Stop gekappt auf **0,41 %**.

| Nominal | Verlust je Stopp | Anteil des 6-%-Puffers | Margin auf 100k | Rendite p.a. |
|---|---|---|---|---|
| 4× | 1,65 % | 27 % | ~4.700 $ | +9,4 % |
| **6×** | **2,47 %** | **41 %** | ~7.100 $ | **+14,1 %** |
| **8×** | **3,29 %** | **55 %** | ~9.400 $ | **+18,8 %** |
| 10× | 4,12 % | 69 % | ~11.800 $ | +23,6 % |

Jahres-Simulation gegen den 6-%-Boden:

| Nominal | überlebt | Ø p.a. | Jahre ≥20 % | **$ auf 100k** |
|---|---|---|---|---|
| 4× | 100,0 % | +9,7 % | 0,9 % | 9.732 $ |
| **6×** | **99,1 %** | **+14,8 %** | 19,6 % | **14.807 $** |
| **8×** | **99,1 %** | **+20,2 %** | **51,4 %** | **20.184 $** |
| 10× | 97,2 % | +25,5 % | 68,2 % | 25.484 $ |

**Die Margin ist nicht die Bremse** — 8× Nominal kostet rund 9.400 $ Margin auf
einem 100.000-$-Konto. **Die Bremse ist der Puffer:** Ein ausgestoppter Zyklus
kostet bei 8× rund 55 % davon.

---

## Was jetzt die größte Schwäche ist

**Zehn Jahre Daten heißen bei Monatszyklen rund 119 Beobachtungen — und die
12-Monats-Fenster überlappen so stark, dass effektiv etwa zehn unabhängige
Jahre dahinterstehen.** Die „99,1 % Überlebensrate" ruht auf ungefähr zehn
unabhängigen Beobachtungen. Das ist die Sorte Zahl, vor der dieses Projekt an
fünf Stellen warnt ([`ergebnisse.txt`](ergebnisse.txt), Falle 2 und 4).

Weitere offene Punkte:

- **Der Stop ist im Modell exakt, in der Praxis nicht.** Ich stoppe zum
  theoretischen Wert; real hast du Slippage auf vier Legs gleichzeitig, und
  genau dann, wenn der Markt sich schnell bewegt.
- **Ich rolle nicht.** Du hast Rollen als Alternative zum Stop genannt — das
  habe ich nicht modelliert, es könnte besser oder schlechter sein.
- **VIX als ATM-Vol für 21 Tage** ist eine Annäherung (VIX misst 30 Tage).
- **Ein Skew-Modell ist linear, echte Smiles sind es nicht.**

---

## Was ich dir nach dieser Rechnung sagen würde

**Realistisch sind 15 % im Jahr, nicht 20–30 %.** Bei 6× Nominal:
+14,8 % p.a., 99,1 % Überlebensrate, ein Stopp kostet 41 % des Puffers.
Auf 100.000 $ mit vollem Split sind das rund **14.800 $**.

Die 8×-Zeile mit +20,2 % ist erreichbar — aber dort kostet ein einziger
gestoppter Zyklus **55 % deines gesamten Risikokapitals.** Zwei schlechte
Monate hintereinander, und das Konto ist weg. Bei zehn unabhängigen
Datenjahren würde ich das nicht als abgesichert bezeichnen.

**Und der Punkt, der sich durch das ganze Projekt zieht, gilt auch hier:**
Der Unterschied zwischen 14,8 % und 20,2 % ist keine bessere Strategie. Es ist
eine Entscheidung darüber, wie viel Puffer ein einzelnes Ereignis fressen darf.

---

*Skripte: `research/condor.py` (echtes Condor-Modell mit Skew und
Verfallsabrechnung), `research/condor2.py` (Positionsgröße gegen den Puffer).
Ersetzt die Näherung in [`vanquish.md`](vanquish.md) und
[`anbieter.md`](anbieter.md).*
