# Liquidität + MACD auf 1h und 4h — die Methode zerlegt

Spezifikation vor der Rechnung: [`liq_macd_spec.md`](liq_macd_spec.md).
6 Märkte, 1 h, 2021-03 bis 2026-07. Klammer 0,6 % / 0,6 %, max. 24 h.
Kosten **12 bp**, aus den echten Trades des Nutzers abgeleitet.

---

> ## Der Befund in drei Sätzen
>
> **Die 4h-Bestätigung schadet.** Sie kostet **−1,29 bp** im Suchzeitraum und
> **−1,86 bp** im Holdout — konsistent in beiden, in dieselbe Richtung. Sie
> halbiert die Signalzahl und macht das Ergebnis schlechter.
>
> **Die Liquidität ist der einzige Baustein mit konsistent positivem Beitrag:**
> +2,02 bp (Suche) und +2,96 bp (Holdout), wenn das Level als **Ziel** in
> Handelsrichtung liegt. Dein Instinkt zeigt in die richtige Richtung.
>
> **Es reicht trotzdem nicht — nicht annähernd.** Nötig wären 60,0 %
> Trefferquote, gemessen sind 42–48 %. Der Zufallseinstieg liegt bei 44,1 %,
> also **über** allen MACD-Varianten des Suchzeitraums.

---

## Vorher: zwei Gewinner sind kein Befund

Bei einer Trefferquote von 50 % passieren zwei Gewinner in Folge in **25 %**
aller Fälle rein zufällig. Deine beiden Trades sagen über die Methode nichts —
und das ist kein Vorwurf, sondern der Grund, warum diese Rechnung überhaupt
gemacht wird. Du hast selbst gefragt, wie du sie gemacht hast. Genau das war
die richtige Frage.

---

## Die Leiter — welcher Baustein trägt was?

### Suchzeitraum (6 Märkte, bis 2024-12)

| | Aufbau | n | Treffer | brutto bp | netto bp | t | Märkte + |
|---|---|---|---|---|---|---|---|
| **L0** | **Zufallseinstieg (Kontrolle)** | — | **44,1 %** | — | **−19,06** | — | — |
| L1 | nur 1h-MACD-Kreuzung | 13.583 | 43,2 % | −8,14 | −20,14 | −39,5 | 0/6 |
| L2 | **1h + 4h gleichgerichtet** | 5.850 | **42,1 %** | −9,44 | **−21,44** | −27,7 | 0/6 |
| L3a | L2 + Einstieg **am** Level (Fade) | 2.049 | 42,6 % | −8,87 | −20,87 | −16,0 | 0/6 |
| L3b | L2 + Level als **Ziel** (Magnet) | 2.104 | 43,8 % | −7,42 | −19,42 | −15,0 | 0/6 |
| L4 | nur Level-Nähe, **ohne** MACD | 30.399 | 44,2 % | −7,00 | −19,00 | −55,6 | 0/6 |

### Holdout (5 Märkte ohne BTC, ab 2025-01)

| | Aufbau | n | Treffer | brutto bp | netto bp | t | Märkte + |
|---|---|---|---|---|---|---|---|
| **L0** | **Zufallseinstieg** | — | **46,2 %** | — | **−16,55** | — | — |
| L1 | nur 1h-MACD-Kreuzung | 4.658 | 47,3 % | −3,18 | −15,18 | −17,3 | 0/5 |
| L2 | 1h + 4h gleichgerichtet | 1.976 | 45,8 % | −5,04 | −17,04 | −12,7 | 0/5 |
| L3a | L2 + Einstieg am Level | 694 | 45,8 % | −5,01 | −17,01 | −7,5 | 0/5 |
| L3b | L2 + Level als Ziel | 721 | **48,3 %** | −2,08 | −14,08 | −6,3 | 0/5 |
| L4 | nur Level-Nähe, ohne MACD | 10.713 | 46,5 % | −4,25 | −16,25 | −28,1 | 0/5 |

**0 von 6 bzw. 0 von 5 Märkten positiv, in jeder Stufe.**

Der Zufallseinstieg hat im Suchzeitraum eine **höhere** Trefferquote (44,1 %)
als jede MACD-Variante (42,1–43,8 %). Im Holdout schlägt nur L3b die Kontrolle
(48,3 % gegen 46,2 %) — und L3b lag in der Suche darunter. Vorzeichenwechsel.

*(Der faire Vergleichsmaßstab ist 44 %, nicht 50 %: Bei einer 1:1-Klammer mit
24-h-Zeitgrenze zählt der Stop bei Gleichstand in derselben Kerze, und
unaufgelöste Trades gehen zum Marktpreis raus. Deshalb wird gegen den
gemessenen Zufallseinstieg verglichen, nicht gegen die Theorie.)*

---

## Die entscheidende Tabelle: bringt die Konfluenz mehr als ihre Teile?

| Schritt | Suche | Holdout | Signale |
|---|---|---|---|
| L1 → L2 **(4h-Bestätigung dazu)** | **−1,29 bp** | **−1,86 bp** | 13.583 → 5.850 |
| L2 → L3a (Einstieg am Level) | +0,57 bp | +0,03 bp | 5.850 → 2.049 |
| L2 → L3b **(Level als Ziel)** | **+2,02 bp** | **+2,96 bp** | 5.850 → 2.104 |

Das ist die Antwort auf deine Frage, in zwei Zeilen:

* **Die 4h-Bestätigung macht es schlechter** — in beiden Zeiträumen, in
  dieselbe Richtung. Sie wirft 57 % der Signale weg und verbessert nichts.
  Konfluenz fühlt sich sicherer an; gemessen ist sie hier ein Filter, der
  gute und schlechte Signale gleichermaßen entfernt und dabei die Stichprobe
  schrumpft.
* **Die Liquidität trägt** — aber nur in der Lesart „das Level ist mein
  **Ziel**", nicht „ich steige **am** Level ein". +2,02 und +2,96 bp,
  konsistent im Vorzeichen. Das ist der einzige Baustein deiner Methode, der
  reproduzierbar etwas beiträgt.

**Und trotzdem:** L3b braucht +19,42 bp, um bei null zu landen. Der Beitrag von
+2,02 bp ist ein Zehntel davon.

---

## Break-even gegen gemessen

Ziel und Stop je 0,6 % = 60 bp, Kosten 12 bp → **nötige Trefferquote 60,0 %**.

| | L2 | L3a | L3b |
|---|---|---|---|
| Suche | 42,1 % (−17,9 pp) | 42,6 % (−17,4 pp) | 43,8 % (−16,2 pp) |
| Holdout | 45,8 % (−14,2 pp) | 45,8 % (−14,2 pp) | 48,3 % (−11,7 pp) |

---

## Was der Markt gibt und was die Börse nimmt

Anders als beim 200-$-Push ([`push200.md`](push200.md)) ist hier **schon die
Bruttozahl negativ**:

| | brutto | 8 bp | 12 bp |
|---|---|---|---|
| L1 nur 1h-MACD | −8,14 | −16,14 | −20,14 |
| L2 1h + 4h | −9,44 | −17,44 | −21,44 |
| L3b Level als Ziel | −7,42 | −15,42 | −19,42 |
| L4 nur Level | −7,00 | −15,00 | −19,00 |

Beim 200-$-Push war brutto −2,53 bp und die Reibung hat den Rest erledigt.
Hier verliert die Regel **auch ohne jede Gebühr**. Das ist ein anderer Befund:
Dort war das Problem die Kostenstruktur, hier ist es das Signal.

---

## Long gegen Short

Beide gezeigten Trades waren Short. Ein Short-spezifischer Vorteil ist nicht zu
finden:

| | Long | Short |
|---|---|---|
| L2 Suche | −21,03 bp (n=2.939) | −21,85 bp (n=2.911) |
| L2 Holdout | −17,59 bp (n=1.019) | −16,45 bp (n=957) |
| L3b Holdout | −15,39 bp (n=354) | −12,82 bp (n=367) |

Praktisch symmetrisch. Deine beiden Shorts waren keine Short-Stärke, sie waren
zwei Trades.

---

## Urteil nach den vorab festgelegten Kriterien

| Kriterium | L2 | L3a | L3b |
|---|---|---|---|
| 1. netto bp > 0 in der Suche | ❌ −21,44 | ❌ −20,87 | ❌ −19,42 |
| 2. gleiches Vorzeichen im Holdout | (beide negativ) | (beide negativ) | (beide negativ) |
| 3. Trefferquote über dem Zufall | ❌ darunter | ❌ darunter | ❌ Suche darunter |
| 4. t > 2,64 | ❌ −27,7 | ❌ −16,0 | ❌ −15,0 |

**Keine Stufe tragfähig.** Zusatzfrage aus der Spezifikation — *bringt die
Konfluenz mehr als ihre Teile?* — **nein für den 4h-Filter, ja (aber viel zu
klein) für die Liquidität als Ziel.**

---

## Was daraus praktisch folgt

1. **Wirf die 4h-Bestätigung raus.** Sie kostet messbar, in beiden Zeiträumen.
   Das ist der klarste Einzelbefund dieser Rechnung.
2. **Behalte die Liquiditätsfrage — aber als Zielsetzung, nicht als
   Einstiegsort.** „Wohin läuft der Kurs, wenn er läuft?" trägt (+2 bis +3 bp).
   „Ich steige am Level ein" trägt praktisch nichts (+0,57 / +0,03 bp).
3. **Der MACD ist hier der teure Teil.** Die beste Bruttozahl hat die Variante
   *ohne* MACD (L4, −7,00 bp) — und die ist vom Zufallseinstieg nicht zu
   unterscheiden (−19,00 gegen −19,06 netto).
4. **Deine Trefferquote müsste von ~45 % auf 60 % steigen.** Das ist die ganze
   Aufgabe, und keine Indikator-Kombination in diesem Projekt hat je mehr als
   1–2 Punkte über dem Zufall gehalten.
5. **Führe ein Journal, bevor du der nächsten Idee traust.** Zwei Trades sind
   25 % Zufall. Bei 30 Trades ist die Spanne einer fairen Münze immer noch
   32–68 % Trefferquote. Erst ab ~100 Trades wird eine Trefferquote von 60 %
   von 50 % unterscheidbar.

---

## Einschränkungen

* **„Liquidität" ist hier als Pivot-Level mit ≥ 3 Berührungen umgesetzt** —
  das, was in einer normalen App sichtbar ist. Eine Liquidations-Heatmap
  (Coinglass-Modell) ist etwas anderes; sie wurde in diesem Projekt getrennt
  geprüft und war als Magnet ein Münzwurf ([`footprint_liquidation.md`](footprint_liquidation.md)).
* **Eine Klammer, ein Zeitfenster.** 0,6 % / 0,6 % / 24 h ist an den beiden
  gezeigten Trades orientiert (0,40 % und 0,77 %, 11 h). Andere Klammern geben
  andere Zahlen — die Lücke von 12–18 Punkten zur Trefferquote schließt keine.
* **Diskretionäres Urteil ist nicht abbildbar.** Du hast auf den Chart
  geschaut; das Skript prüft Regeln. Wenn dein Vorteil in der Auswahl liegt,
  die sich nicht als Regel schreiben lässt, misst diese Rechnung ihn nicht —
  dann ist ein geführtes Journal über 100 Trades der einzige Weg, ihn zu zeigen.
