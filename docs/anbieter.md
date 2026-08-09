# Vier Anbieter gegen die Strategie gerechnet

> ## 🛑 HINFAELLIG — DIE ECHTEN REGELN WIDERLEGEN DIESES DOKUMENT
>
> Das Vanquish-Regelwerk-PDF sagt woertlich: **„SPX, XSP and VIX can only be
> traded long as single-leg calls/puts. No spreads, no selling to open."**
> Dazu **Intraday Trailing Drawdown** (nicht statisch) und **keine
> Overnight-Positionen**.
> Damit ist jede Rechnung in diesem Dokument gegenstandslos.
> **Siehe [`vanquish_regeln.md`](vanquish_regeln.md).**

> ## 🛑 ZAHLEN UEBERHOLT
>
> Die Iron-Condor-Zahlen in diesem Dokument beruhen auf einer **Naeherung**
> (gekappte Straddle-Reihe, Praemienanteil 40-55 %). Ein echtes Condor-Modell
> mit Strikes, Skew und Verfallsabrechnung ohne Hedge ergibt **4-11 %** der
> Straddle-Praemie und **+2,4 % statt +6,2 %** Rendite je Einheit Nominal.
> Der Sharpe haelt (2,38 gegen 2,55), die Ertragsdichte nicht.
> **Massgeblich sind die Zahlen in [`condor.md`](condor.md).**

Die Liste ist gut recherchiert und trifft den richtigen Punkt: **kein
Tagesverlustlimit**. Das war die Sperre ([`ziel.md`](ziel.md)).

Aber das Fazit der Liste — „MFF und TradeDay bieten durch die
End-of-Day-Berechnung die sauberste Umgebung" — kehrt sich um, sobald man es
rechnet. Und zwei Punkte fehlen ganz, die alles entscheiden.

---

## 1. Der erste fehlende Punkt: drei der vier Anbieter können die Strategie gar nicht traden

| Anbieter | Instrument | kann den S&P-Straddle? |
|---|---|---|
| **Vanquish** | **Index-Optionen** | **ja** |
| My Funded Futures | Futures | nein |
| TradeDay | Futures | nein |
| Apex | Futures | nein |

Der einzige Ansatz, der in diesem Projekt zwei unabhängige Anlageklassen
überstanden hat, ist die **Volatilitäts-Risikoprämie** — und die braucht
**Optionen** ([`andere_maerkte.md`](andere_maerkte.md)).

Für die drei Futures-Anbieter bräuchtest du eine Futures-Strategie. Die einzige
mit belastbarer akademischer Evidenz ist Trendfolge — und die liegt seit 2017
bei **Sharpe −0,17** über alle Horizonte und alle vier Sektoren.

**Damit ist die Auswahl faktisch keine Auswahl von vier, sondern von einem.**

---

## 2. Der zweite fehlende Punkt: trailing gegen statisch, nicht EOD gegen intraday

Die Liste behandelt „End-of-Day" als das entscheidende Merkmal. Das ist eine
Verfeinerung zweiter Ordnung. **Erster Ordnung ist: folgt der Boden deinen
Gewinnen oder nicht.**

S&P-Straddle, 3× Hebel, kein Tageslimit bei beiden:

| Drawdown | **STATISCH** überlebt / Ø p.a. / ≥20 % | **EOD-TRAILING** überlebt / Ø p.a. / ≥20 % |
|---|---|---|
| 2 % | 44,9 % / +15,8 % / 31,5 % | **0,0 %** / −2,0 % / 0,0 % |
| **3 %** | **54,5 % / +17,9 % / 35,4 %** | **0,0 %** / −3,0 % / **0,0 %** |
| 5 % | 62,8 % / +19,3 % / 37,8 % | 10,7 % / −1,4 % / 10,3 % |
| 8 % | 73,8 % / +21,6 % / 41,5 % | 23,2 % / +1,3 % / 18,7 % |
| 10 % | 78,2 % / +22,3 % / 42,5 % | 36,8 % / +8,0 % / 29,9 % |

**Bei 3 % Drawdown: 54,5 % Überlebensrate statisch — 0,0 % trailing.**

Der Grund ist strukturell: **Trailing bestraft den Erfolg.** Jedes neue
Kontohoch hebt den Boden mit. Ein 3-%-Trailing-Drawdown bedeutet, dass du nie
wieder 3 % von irgendeinem Hoch zurückgeben darfst — nicht ein einziges Mal im
Jahr. Das schafft keine Strategie mit nennenswerter Volatilität.

### Und weniger Hebel rettet es nicht

EOD-Trailing, überlebt / Anteil Jahre ≥20 %:

| Hebel | 3 % DD | 5 % DD | 8 % DD | 10 % DD |
|---|---|---|---|---|
| **0,5×** | 82 % / **0 %** | 89 % / **0 %** | 100 % / **0 %** | 100 % / **0 %** |
| 1,0× | 42 % / 7 % | 64 % / 9 % | 89 % / 10 % | 89 % / 10 % |
| 2,0× | 8 % / 2 % | 24 % / 12 % | 56 % / 25 % | 60 % / 26 % |
| 3,0× | 0 % / 0 % | 11 % / 10 % | 23 % / 19 % | 37 % / 30 % |

Bei 0,5× überlebst du praktisch immer — und erreichst **in 0 % der Jahre**
dein Ziel. Trailing zwingt dich in die Ecke, in der du entweder rausfliegst
oder nichts verdienst.

**Damit dreht sich die Rangfolge deiner Liste um:**

| Rang | Anbieter | Mechanik | Urteil |
|---|---|---|---|
| **1** | **Vanquish (funded)** | **statisch** | einziger, der die Strategie traden kann *und* die richtige Mechanik hat |
| 2 | TradeDay | **statisch wählbar** | die Wahlmöglichkeit ist mehr wert als alles andere in ihrem Pitch |
| 3 | MFF | EOD-trailing | „EOD" repariert das Grundproblem nicht |
| 4 | Apex | intraday-trailing | dieselbe Falle, nur schneller |

Deine eigene Notiz zu Apex — *„kann der Live-Trailing-Drawdown trotz fehlendem
Tageslimit toxisch wirken"* — ist richtig. Sie gilt für **EOD-Trailing genauso**,
nur langsamer.

---

## 3. Die Zahl, die in keiner der vier Beschreibungen steht

**Wie groß ist der Drawdown eigentlich?**

Übliche Futures-Prop-Konten auf 100.000 $ Nominal liegen bei **2.000–4.000 $
= 2–4 %.** Kraken Prop hat **6 % statisch**.

> **Die Futures-Anbieter sind beim Drawdown ENGER als Kraken, nicht weiter.**
> Der Vorteil „kein Tageslimit" wird dadurch teilweise wieder aufgefressen.

Das musst du vor jedem Kauf nachsehen — es ist die wichtigste Zahl im Angebot
und steht selten in der Werbung. *(Ich nenne hier Größenordnungen aus
allgemeiner Marktkenntnis, keine geprüften Daten der einzelnen Anbieter.
Nachrechnen, nicht glauben.)*

Bester Hebel je Drawdown-Größe, statisch:

| Drawdown | bester Hebel | überlebt | Ø p.a. | Jahre ≥20 % |
|---|---|---|---|---|
| 2 % | 4× | 40,3 % | +21,1 % | 35,0 % |
| **3 %** | 5× | 43,0 % | +29,8 % | 39,9 % |
| 6 % | 5× | 56,2 % | +34,5 % | 49,1 % |
| 10 % | 5× | 64,8 % | +37,4 % | 55,5 % |

---

## 4. Der Haken, der in keiner Anbieterliste steht: nackte Optionen

**Ein Short-Straddle ist eine nackte Short-Option — unbegrenztes Risiko.
Nahezu alle Prop-Firmen verbieten das.** Erlaubt sind definierte Risiken:
Iron Condor, Credit Spread. Genau darauf zielt Vanquishs Formulierung
„komplexe Multi-Leg-Strategien".

**Das musst du vor dem Kauf klären.** Wenn Vanquish nackte Short-Optionen
verbietet, ist die getestete Strategie dort nicht handelbar — und die ganze
Auswahl fällt in sich zusammen.

### Und jetzt die Überraschung: die erlaubte Version ist besser

Näherung eines Iron Condor: Short-Straddle mit **gekappter Verlustseite**.
Die Flügel kosten Prämie, begrenzen aber den Schwanz.

| Variante | p.a. | Vol | **Sharpe** | schlechtester Tag |
|---|---|---|---|---|
| Short-Straddle (nackt) | +8,6 % | 5,5 % | 1,52 | **−5,58 %** |
| Iron Condor (~70 % Prämie) | +7,0 % | 3,3 % | **2,03** | −1,40 % |
| **Iron Condor (~55 % Prämie)** | **+6,2 %** | **2,4 %** | **2,55** | **−0,66 %** |
| Iron Condor (~40 % Prämie) | +5,1 % | 1,6 % | **3,11** | −0,32 % |

Du gibst Rendite ab und bekommst **Sharpe und einen zahmen schlechtesten Tag**.
Und weil auf einem Prop-Konto der Drawdown die Bindung ist, nicht die Rendite,
kannst du dafür **deutlich höher hebeln**:

**Iron Condor (55 %), statischer Drawdown:**

| Drawdown | bester Hebel | überlebt | Ø p.a. | **Jahre ≥20 %** |
|---|---|---|---|---|
| **3 %** | 6× | 68,6 % | **+29,0 %** | **58,6 %** |
| 4 % | 8× | 68,1 % | +41,5 % | 64,0 % |
| **6 %** | 8× | 78,2 % | +47,7 % | **73,0 %** |
| 10 % | 8× | 91,1 % | +53,6 % | 84,5 % |

**Bei 3 % statischem Drawdown und 6× Hebel: +29 % im Jahr, 68,6 %
Überlebensrate, 58,6 % der Jahre über 20 %.** Das ist das beste Ergebnis
dieses gesamten Projekts — und es ist die Variante, die ein Prop-Konto
überhaupt erlaubt.

---

## 5. Was an dieser Rechnung schwach ist

**1. Der Iron Condor ist eine Näherung, kein Backtest.** Ich habe die
Straddle-Reihe gekappt und die Prämie skaliert. Ich habe **keine echten
Optionsketten** — keine Strikes, keine Bid-Ask-Spannen der Flügel, keine
Skew. Die *Richtung* des Effekts (gekappter Schwanz → höherer Sharpe → mehr
Hebel möglich) ist robust. Die konkreten Zahlen sind illustrativ.

**2. Margin bei 6–8× Hebel ist nicht geprüft.** Bei einem Iron Condor ist die
Margin die Spread-Breite. Ob ein 100k-Prop-Konto 6–8× davon trägt, hängt an
Kontraktgrößen, die ich nicht habe. **Das ist die Zahl, an der der ganze Plan
scheitern kann.**

**3. Der S&P-Datensatz umfasst nur 2016–2026.** Drei Krisen sind drin
(Volmageddon, COVID, 2022) — aber es sind zehn Jahre, nicht dreißig.

**4. 68,6 % Überlebensrate heißt: knapp ein Drittel der Jahre verlierst du das
Konto.** Bei 100 % Profit-Split und einer Evaluierungsgebühr ist das
verkraftbar — aber es ist kein Gehalt, es ist ein Geschäft mit Ausfallrisiko.

---

## 6. Was du konkret prüfst, bevor du zahlst

Bei **Vanquish**, in dieser Reihenfolge:

```
1. Sind NACKTE Short-Optionen erlaubt -- oder nur definierte Risiken?
   (Wenn nur definiert: gut, siehe Iron-Condor-Zahlen. Aber wissen musst du es.)

2. Wie GROSS ist der statische Drawdown auf dem Live-Konto, in Prozent?
   Das ist die wichtigste Zahl im ganzen Angebot.

3. Gibt es eine Consistency Rule auf dem LIVE-Konto?
   Eine solche Regel trifft genau diese Strategie -- die Rendite kommt aus
   vielen kleinen Praemien und wenigen grossen Verlusten.

4. Welche Indizes, welche Laufzeiten, welche Margin je Spread?
   Ohne diese Zahl ist der noetige Hebel nicht pruefbar.

5. Was kostet die Evaluierung, und wie oft darf man antreten?
   (Bei ~50-60 % Bestehenswahrscheinlichkeit ist der zweite Versuch
   einzupreisen -- siehe spielregeln.md.)
```

Bei **TradeDay**, falls du doch Futures willst: **statischen Drawdown wählen**,
auch wenn der Puffer kleiner ist. Die Tabelle in Abschnitt 2 zeigt, dass ein
kleiner statischer Puffer einen großen trailenden schlägt.

**MFF und Apex** würde ich nach dieser Rechnung nicht nehmen — nicht wegen des
Tageslimits, das haben sie richtig gemacht, sondern wegen der Trailing-Mechanik.

---

*Skripte: `research/firmen.py` (Drawdown-Mechanik, Hebelsweep),
`research/firmen2.py` (Trailing bei niedrigem Hebel, Iron-Condor-Näherung).
Regelwerke nach Angaben des Nutzers, nicht unabhängig verifiziert.*
