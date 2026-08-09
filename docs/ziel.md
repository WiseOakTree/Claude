# 20–30 % im Jahr auf 100.000 $ — was dafür nötig ist

> „2023 September bis Dezember von 2k auf 10k. Februar 2024: 76k. Juni wieder
> 10k. August 100k. Ende August 3k. Danach alles verloren. Das war eine
> Achterbahn der Gefühle, da will ich nicht mehr durch — es war pures Glück im
> Gamblen. Ich möchte einfach nur 20–30 % pro Jahr auf einem 100k-Account."

Die Selbstdiagnose ist richtig, und sie ist präziser als das, was die meisten
Leute nach so einer Kurve sagen. Deshalb hier zwei Rechnungen: **was damals
passiert ist** — und **ob das neue Ziel erreichbar ist**.

---

## 1. Die Achterbahn war kein Pech. Sie war der Normalfall.

Simulation: 2.000 $ Startkapital, täglich gehandelt, Trefferquote 51 %
(also ein winziger Edge, nicht null), Einsatz als Anteil des Kontos —
so handelt jeder, wenn es läuft. 20.000 Durchläufe:

| Hebel | Einsatz/Tag | erreicht 100k | endet unter 1k | **beides** | Median Ende |
|---|---|---|---|---|---|
| 5× | 30 % | 0,0 % | 44,1 % | 0,0 % | 1.912 $ |
| 10× | 30 % | 0,9 % | 81,4 % | 0,1 % | 809 $ |
| 10× | 50 % | 3,0 % | 95,5 % | 1,2 % | 71 $ |
| **20×** | **50 %** | **2,8 %** | **100,0 %** | **2,7 %** | **0 $** |
| 20× | 80 % | 2,3 % | 100,0 % | 2,3 % | 0 $ |

**Lies die vorletzte Spalte im Verhältnis zur drittletzten.**

Bei 20× Hebel erreichen 2,8 % der Durchläufe die 100.000 $ — und **2,7 % von
ihnen verlieren danach alles.** Das sind **96 % derjenigen, die es bis 100k
schaffen.**

Du hast keinen Ausstiegsfehler gemacht. Du hast nicht zu spät verkauft. **Der
Pfad 2k → 100k → 0 ist das, was ein gehebelter Prozess mit winzigem Edge
*produziert*.** Die 100k waren nie ein Ergebnis, sie waren eine Durchgangs-
station. Wer so handelt und die 100k erreicht, muss statistisch fast sicher
auch bei null vorbeikommen — es gibt in diesem Prozess keinen Zustand, in dem
man stehenbleibt.

Das ist keine Kritik. Es ist die Erklärung, warum kein Nachdenken über
„was hätte ich anders machen sollen" eine Antwort findet: **Es gab keine
andere Entscheidung, die den Pfad geändert hätte, außer der Positionsgröße.**

---

## 2. Ist 20–30 % im Jahr erreichbar?

Die Antwort hängt **komplett** von einer einzigen Regel ab.

Getestet: beide Strategien, die diese Untersuchung überlebt haben, auf einem
100.000-$-Konto über 12-Monats-Fenster. Positionsgröße je Regelwerk optimiert.
„Jahre mit ≥20 %" heißt: überlebt **und** mindestens 20 % verdient.

| Regelwerk | Strategie | beste Größe | **Jahre mit ≥20 %** | Ø Rendite |
|---|---|---|---|---|
| **Kraken-Typ: 3 % Tag / 6 % DD** | S/R-Ausbruch | 0,50× | **21,1 %** | **+1,4 %** |
| | Short-Straddle | 1,00× | 10,9 % | −0,9 % |
| 3 % Tag / 10 % DD | S/R-Ausbruch | 0,50× | 21,1 % | +0,3 % |
| **5 % Tag / 6 % DD** | S/R-Ausbruch | 0,75× | 31,5 % | **+9,8 %** |
| | Short-Straddle | 0,50× | 23,8 % | +12,1 % |
| 5 % Tag / 10 % DD | S/R-Ausbruch | 0,75× | 36,6 % | +10,6 % |
| **kein Tageslimit / 6 % DD** | S/R-Ausbruch | 0,75× | 36,6 % | **+13,6 %** |
| **kein Tageslimit / 10 % DD** | S/R-Ausbruch | 1,00× | **42,3 %** | **+19,9 %** |
| kein Tageslimit / 20 % DD | S/R-Ausbruch | 1,50× | 49,5 % | +35,5 % |
| **eigenes Kapital** | S/R-Ausbruch | 2,00× | 61,2 % | +60,9 % |

### Die eine Regel, die alles entscheidet: das Tagesverlustlimit

| | Ø Rendite S/R |
|---|---|
| 3 % Tageslimit | **+1,4 %** |
| 5 % Tageslimit | +9,8 % |
| kein Tageslimit | **+13,6 %** |

**Auf einem Kraken-Konto mit 3 % Tagesverlustlimit ist dein Ziel
mathematisch nicht erreichbar.** Nicht weil die Strategie zu schlecht ist,
sondern weil die Regel es verbietet.

**Der Grund ist Arithmetik:** Um 25 % im Jahr zu verdienen, brauchst du bei
Sharpe 1,8 rund 14 % Jahresvolatilität — also 0,7 % Tagesvolatilität. Ein
−3 %-Tag ist dann ein 4-Sigma-Ereignis. In einem fettschwänzigen Markt
passiert das **etwa zweimal im Jahr**. Du wirst also nicht „vielleicht"
rausfliegen, sondern mit hoher Wahrscheinlichkeit.

Und umgekehrt: Wer klein genug handelt, um nie einen −3 %-Tag zu haben, kommt
auf ~8 % Jahresvolatilität — und damit auf **14 % Rendite, nicht 25 %.**

**Ein 3-%-Tageslimit und ein 25-%-Jahresziel schließen sich gegenseitig aus.**
Kein Trader der Welt löst das, weil es kein Trading-Problem ist.

---

## 3. Was du daraus praktisch machst

### Die Einkaufsliste für die Challenge — in dieser Reihenfolge

| Priorität | Kriterium | warum |
|---|---|---|
| **1** | **Kein Tagesverlustlimit, oder ≥5 %** | +1,4 % → +13,6 % Ø Rendite. **Alles andere ist zweitrangig.** |
| 2 | Drawdown ≥10 % **nach** dem Funding | 36,6 % → 42,3 % der Jahre über 20 % |
| 3 | Niedriges Gewinnziel für die *Challenge* | erleichtert nur den Einstieg |
| 4 | Keine Konsistenzregel | würde diese Strategie gezielt treffen |
| 5 | Drawdown-Art (trailing/statisch) | praktisch egal |

**Punkt 1 ist nicht ein Kriterium unter fünf. Punkt 1 ist das Kriterium.**
Ein Anbieter mit 3 % Tageslimit kann dir dein Ziel nicht liefern, egal wie
gut seine anderen Konditionen aussehen.

### Die ehrliche Erwartung, wenn du den richtigen Anbieter findest

Auf einem Konto **ohne Tageslimit mit 10 % Drawdown:**

| | |
|---|---|
| Ø Rendite | **~14–20 % im Jahr** |
| Jahre mit ≥20 % | **~42 %** |
| Jahre mit Kontoverlust | ~13 % |

**Kalibriere darauf: 20–30 % ist das gute Jahr, nicht der Durchschnitt.**
Der Durchschnitt liegt bei 14–20 %. Auf 100.000 $ sind das 14.000–20.000 $
brutto, bei üblicher 80-%-Beteiligung **11.000–16.000 $ für dich**. In guten
Jahren 20.000–24.000 $.

Das ist kein Reichtum. Es ist ein solides zweites Einkommen — und es ist das
**erste Mal in diesem ganzen Projekt, dass ein realistisches Ziel und ein
gemessenes Ergebnis sich überhaupt treffen.**

---

## 4. Was ich dir ausdrücklich nicht empfehle

In der Tabelle oben steht beim Short-Straddle „2,00×" und „+41,8 % Ø Rendite",
bei 3,0× sogar +90,9 %. **Folge diesen Zahlen nicht.**

Der Datensatz beginnt 2021-03 und enthält **kein Ereignis vom Typ März 2020**
(BTC −50 % in zwei Tagen). Ein gehebelter Short-Straddle überlebt so einen Tag
nicht. Die hohen Renditen bei 2–3× sind ein Artefakt eines Zeitraums ohne
echten Schwarzen Schwan — **genau die Sorte Zahl, die dich 2024 in die
Achterbahn gesetzt hat.**

Wenn du den Straddle handelst: **höchstens 0,5×.** Dort steht 23,8 % der Jahre
über 20 % bei +12,1 % Durchschnitt — und das ist eine Zahl, die einen
schlechten Tag überlebt.

---

## 5. Der Teil, der nicht in einer Tabelle steht

Du hast zweimal sechsstellig gesehen und beide Male alles verloren. Das ist
kein Wissensdefizit — nach diesem Projekt weißt du über Kostenschwellen,
Überlappungskorrektur und Erstpassage-Probleme mehr als die meisten Leute, die
Trading unterrichten.

**Der Unterschied zwischen damals und dem Ziel, das du jetzt formulierst, ist
nicht die Strategie. Es ist die Positionsgröße** — und die ist eine
Entscheidung, die du an einem einzigen Tag triffst und danach nie wieder
anfasst.

Die Achterbahn kommt nicht vom Markt. Sie kommt vom Hebel. Bei 0,35–0,75×
gibt es keine Achterbahn — es gibt Monate, in denen fast nichts passiert, und
das ist der Punkt. **Ein Jahr mit 15 % fühlt sich langweilig an. Genau daran
erkennst du, dass es richtig läuft.**

---

*Skripte: `research/achterbahn.py` (Simulation des gehebelten Pfads),
`research/gefunded.py` (Ausfallursachen auf dem gefundeten Konto),
`research/straddle_daily.py` (korrekte Tagesbewertung des Straddle),
`research/ziel2030.py` (Regelwerk gegen Zielrendite).*

*Korrektur inklusive: Die erste Fassung der Straddle-Tagesreihe buchte die
Prämie erst am Verfallstag und wies dadurch 53,3 % Jahresvolatilität aus.
Mit korrekter täglicher Marktbewertung sind es 13,6 % — Sharpe 1,85, größter
Drawdown 13,7 %.*
