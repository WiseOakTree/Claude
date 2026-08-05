# Vanquish, mit den echten Regeln durchgerechnet

Die fünf Antworten haben einen **strukturellen Fehler** in meiner vorherigen
Rechnung aufgedeckt. Punkt 4 ist der wichtigste, den jemand in diesem Projekt
beigetragen hat.

---

## 🛑 Korrektur: mein Hebel-Sweep war nicht zu optimistisch, er war falsch gedacht

Ich habe den Hebel auf das **Nominal** bezogen (100.000 $). Bindend ist aber
der **Maximalverlust gegen den Puffer** (6.000 $).

Ein Iron Condor mit Kappe *c* und Hebel *L* verliert im Ereignisfall
**c × L** des Kontos:

| Kappe | Hebel | Verlust je Ereignis | Anteil des 6-%-Puffers | |
|---|---|---|---|---|
| 1,2 % | 3× | 3,6 % | 60 % | |
| 1,2 % | **6×** | **7,2 %** | **120 %** | **Konto weg** |
| 2,0 % | **3×** | **6,0 %** | **100 %** | **Konto weg** |
| 2,0 % | 6× | 12,0 % | 200 % | Konto weg |

**Meine Tabelle mit „6× → +29 % p.a." beschrieb ein Konto, das nach dem ersten
Volatilitätsschub nicht mehr existiert.** Dein Satz *„dein reales Risikokapital
liegt nicht bei 100.000 $, sondern faktisch bei 6.000 $"* ist die richtige
Formulierung. Risikobudget zuerst, Hebel danach.

---

## Neu gerechnet: was der 6.000-$-Puffer wirklich trägt

Iron Condor, statischer Drawdown 6 %, kein Tageslimit:

| Kappe | Hebel | max. Einzelverlust | überlebt | Ø p.a. | Jahre ≥20 % | Urteil |
|---|---|---|---|---|---|---|
| **0,8 %** | 2,0× | 1,6 % (27 % Puffer) | **100 %** | +10,3 % | 9,7 % | tragbar |
| **0,8 %** | 2,5× | 2,0 % (33 %) | **100 %** | +13,0 % | 16,7 % | tragbar |
| **0,8 %** | **3,0×** | **2,4 % (40 %)** | **100 %** | **+15,9 %** | **23,6 %** | Grenze |
| **0,8 %** | 4,0× | 3,2 % (53 %) | 98,5 % | **+21,0 %** | **33,9 %** | Kante |
| 1,2 % | 3,0× | 3,6 % (60 %) | 96,8 % | +18,3 % | 25,4 % | Kante |
| 1,2 % | 4,0× | 4,8 % (80 %) | 93,3 % | +23,9 % | 46,6 % | 1 Ereignis = Ende |
| 2,0 % | 3,0× | 6,0 % (100 %) | 83,7 % | +17,3 % | 29,5 % | 1 Ereignis = Ende |
| 2,0 % | 4,0× | 8,0 % (133 %) | 77,2 % | +22,9 % | 46,2 % | 1 Ereignis = Ende |

### Die nicht offensichtliche Erkenntnis: enger ist besser

| Konfiguration | Ø p.a. | überlebt |
|---|---|---|
| Kappe **0,8 %**, 4× | +21,0 % | **98,5 %** |
| Kappe 2,0 %, 4× | +22,9 % | **77,2 %** |

Fast dieselbe Rendite, **21 Prozentpunkte mehr Überlebensrate.** Der Grund ist
genau dein Argument: Bei einem engen Puffer entscheidet nicht die Prämie,
sondern wie tief ein einzelnes Ereignis ins Risikokapital greift.

> **Enge Flügel, mehr Kontrakte** schlägt **weite Flügel, weniger Kontrakte** —
> bei gleicher eingenommener Prämie.

---

## Die Konsistenzregel ist kein Problem

Gemessen: Anteil des **besten Tages** am Jahresgewinn.

| | |
|---|---|
| Median | **10,1 %** |
| 90. Perzentil | 17,4 % |
| Jahre über 30 % | **3,1 %** |
| Jahre über 40 % | 0,7 % |

Optionsverkauf verdient über **Theta** — also jeden Tag ein bisschen. Das ist
genau das Profil, für das eine Konsistenzregel gemacht ist. Deine Sorge betrifft
die *Verlustseite*, und die ist zu Recht geäußert — aber sie wird durch die
Kappe erschlagen, nicht durch die Konsistenzregel.

---

## Die Evaluierung

Enger Condor (Kappe 0,8 %), Ziel 8 %, EOD-Drawdown 6 %:

| Hebel | max. Einzelverlust | **bestanden** | Median Dauer |
|---|---|---|---|
| 1,0× | 0,8 % | 14,7 % | 188 T |
| 2,0× | 1,6 % | 57,9 % | 184 T |
| **3,0×** | **2,4 %** | **90,9 %** | **142 T** |
| 4,0× | 3,2 % | 96,1 % | 105 T |

**Bei 3× Hebel: 90,9 % Bestehenswahrscheinlichkeit, Median 142 Tage.**

Erwartete Gesamtkosten bei 400 $ je Versuch: **~440 $** (nicht 700–900 $).
Deine Budget-Empfehlung ist trotzdem die richtige Haltung — Fehlschläge
clustern ([`spielregeln.md`](spielregeln.md)), also rechne mit dem oberen Rand.

**Wichtig:** In der Evaluierung darfst du aggressiver sein als danach. Der
Verlust bei Scheitern sind 400 $, nicht das Konto. Danach kehrt sich das um.

---

## Die Endrechnung

100 % Profit-Split — brutto ist netto:

| Hebel | Puffer-Anteil je Ereignis | überlebt | Ø p.a. | Jahre ≥20 % | **Ø $ auf 100k** |
|---|---|---|---|---|---|
| 2,5× | 33 % | 100 % | +13,0 % | 16,7 % | **13.024 $** |
| **3,0×** | **40 %** | **100 %** | **+15,9 %** | 23,6 % | **15.861 $** |
| 4,0× | 53 % | 98,5 % | **+21,0 %** | **33,9 %** | **21.036 $** |

**Dein Ziel von 20–30 % ist erreichbar — bei 4× Hebel, und nur an der Kante.**
Ein einziges Maximalverlust-Ereignis frisst dann 53 % deines Puffers. Danach
handelst du ein Jahr lang mit halbem Spielraum.

**Die robuste Konfiguration ist 3×: ~15.900 $ im Jahr, 100 % Überlebensrate in
allen geprüften Jahresfenstern, ein Ereignis kostet 40 % des Puffers.**

---

## Was an dieser Rechnung weiterhin schwach ist

**1. Der Iron Condor bleibt eine Näherung.** Ich habe die Straddle-Reihe gekappt
und die Prämie skaliert. Keine echten Optionsketten, keine Strikes, keine
Bid-Ask-Spannen der Flügel, keine Skew.

**2. Die Prämien-Annahme ist meine, nicht gemessen.** Ich unterstelle, dass ein
Condor mit 0,8-%-Kappe rund 40 % der Straddle-Prämie behält. Behält er real nur
25 %, sinkt alles um ein Drittel. **Das ist die Zahl, die du an echten Ketten
prüfen musst, bevor du zahlst.**

**3. Der größte Modellfehler: meine Reihe stammt aus einem delta-gehedgten
Straddle. Ein Iron Condor wird üblicherweise nicht delta-gehedgt.** Ohne Hedge
schlagen gerichtete Bewegungen härter durch. **Meine Zahlen sind dadurch eher
zu gut.** Wenn du delta-hedgen darfst und willst, gelten sie näherungsweise;
wenn nicht, rechne mit weniger.

**4. Zehn Jahre Daten** — mit Volmageddon, COVID und 2022 drin, aber es sind
zehn Jahre.

**5. Dein Vega-Spike-Argument ist richtig und im Modell nur teilweise erfasst.**
Ich rechne die Kappe als *aggregierten* Maximalverlust über alle Spreads
gleichzeitig — das ist der richtige Ansatz. Aber wie *oft* ein marktweiter
Vol-Schub alle Spreads gleichzeitig auf Maximalverlust bringt, hängt an der
Strike-Wahl, und die habe ich nicht.

---

## Der konkrete Plan

```
1. VOR DEM KAUF an echten SPX/XSP-Optionsketten pruefen:
   Wie viel Praemie behaelt ein Condor, dessen Maximalverlust
   0,8 % des Nominals betraegt? Meine Annahme: 40 % der
   Straddle-Praemie. Stimmt sie nicht, faellt die Rechnung.

2. EVALUIERUNG mit ~3x Hebel.
   90,9 % Bestehenswahrscheinlichkeit, Median 142 Tage.
   Budget: 800 $ fuer zwei Anlaeufe.

3. LIVE-KONTO mit 3x, NICHT 4x.
   +15,9 % p.a., 100 % Ueberlebensrate, ein Ereignis
   kostet 40 % des Puffers.
   Erst nach zwoelf Monaten Live-Erfahrung ueber 4x nachdenken.

4. ENGE FLUEGEL. Kappe 0,8 % statt 2,0 %.
   Fast dieselbe Rendite, 21 Punkte mehr Ueberlebensrate.

5. ERWARTUNG: ~16.000 $ im Jahr auf 100k, bei 100 % Split.
   In guten Jahren 20-25 %. Das ist kein Gehalt, das ist ein
   Geschaeft mit Ausfallrisiko -- aber es ist das erste Mal in
   diesem Projekt, dass Ziel und Messung sich treffen.
```

---

*Skripte: `research/vanquish.py` (Risikobudget statt Nominal, Konsistenzregel),
`research/vanquish2.py` (Evaluierung, Kosten, Endrechnung). Regelwerk nach
Angaben des Nutzers, nicht unabhängig verifiziert.*
