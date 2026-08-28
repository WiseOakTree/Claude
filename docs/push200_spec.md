# 200-$-Push auf dem 15-Minuten-Chart — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-23, committet bevor gerechnet wurde.

## Die Idee, wie beschrieben

> „Nur am 15-min-Chart einen Push von 200 $ nach oben oder nach unten
> mitnehmen, 1 Trade pro Tag."

## Die Regel, wie sie implementiert wird

| | |
|---|---|
| Chart | BTC, 15 Minuten |
| Bezugspunkt | Eröffnung des Handelstages (00:00 UTC) |
| Auslöser | erste 15-min-Kerze, die **`push` $ entfernt vom Tagesstart** schließt |
| Einstieg | zum Schluss genau dieser Kerze (kein Look-ahead) |
| Richtung | **mit** dem Push (Momentum). Gegenrichtung wird als Kontrolle mitgerechnet |
| Ziel | **200 $** vom Einstieg |
| Stop | Parameter (siehe Gitter) |
| Zeitausstieg | Tagesschluss 23:45 UTC, falls weder Ziel noch Stop |
| Häufigkeit | **maximal 1 Trade je Kalendertag**, nur der erste Auslöser zählt |

## Die Zahl, die vorab alles entscheidet

200 $ auf BTC sind **kein fester Prozentsatz** — sie sind heute 0,26 %, waren
2021 bei 60.000 $ aber 0,33 % und bei 20.000 $ im Jahr 2022 ganze **1,00 %**.
Die Regel bedeutet also über die Jahre etwas völlig Verschiedenes. Deshalb wird
**beides** gerechnet: fixe 200 $ **und** ein fixer Prozentsatz.

Und der Kostenanteil:

> Kosten je Roundtrip ÷ Zielgröße = **Anteil des Ziels, der an die Börse geht.**

Bei 200 $ Ziel auf BTC bei 77.000 $ und einem sehr wohlwollenden Kostenmodell
(9 bp bei Gewinn) sind das **35 %**. Bei reinem Taker-Handel (16 bp) sind es
**62 %**. Die daraus folgende Break-even-Trefferquote wird vorab ausgerechnet
und **im Ergebnis der gemessenen gegenübergestellt**.

## Kostenmodell — bewusst wohlwollend

Damit ein negatives Ergebnis nicht an zu strengen Annahmen liegt:

| Vorgang | Annahme | Kosten |
|---|---|---|
| Einstieg | Taker (Momentum, muss sofort rein) | 4 bp Gebühr + 1 bp halber Spread + 2 bp Slippage = **7 bp** |
| Ausstieg am Ziel | **Maker**-Limit, liegt vorher im Buch | 2 bp Gebühr, keine Slippage = **2 bp** |
| Ausstieg am Stop | Taker in die Bewegung hinein | 4 + 1 + 3 = **8 bp** |
| Ausstieg zum Tagesschluss | Taker | **7 bp** |
| Funding | Position wird am selben Tag geschlossen | **0** |

Roundtrip: **9 bp bei Gewinn, 15 bp bei Verlust.** Zusätzlich gerechnet:
reines Taker-Modell (16 bp flat) und ein **Nullkosten-Lauf**, um zu trennen,
was Marktverhalten und was Reibung ist.

## Gitter

| Parameter | Werte |
|---|---|
| Auslöser `push` | 200, 500, 1.000, 2.000 $ (und die %-Entsprechungen) |
| Ziel | 200 $ (Hauptfall) und „= push" (symmetrisch) |
| Stop | 100, 200, 400, 800 $ |
| Richtung | Momentum (Hauptfall), Fade (Kontrolle) |

**Hauptkombination, vorab benannt:** push 200 $, Ziel 200 $, Stop 200 $,
Momentum. Alles andere ist Empfindlichkeitsprüfung und dient **nicht** der
Auswahl.

## Der Vergleichsmaßstab

Wie bei der Renko-Klammer: Eine Trefferquote ist nur im Verhältnis zum
**Basissatz** aussagekräftig. Für Ziel und Stop in gleicher Entfernung liegt er
ohne Vorhersagbarkeit bei **50 %**. Gemessen wird er zusätzlich empirisch: von
einem **zufälligen 15-min-Bar desselben Tages** aus, mit denselben Barrieren
und demselben Tagesende-Ausstieg. Nur die Differenz ist ein möglicher Edge.

## Daten und Zeiträume

BTC 15 min, 2021-03 bis 2026-07 (≈ 190.000 Bars, ≈ 1.980 Handelstage).
ETH und SOL mit derselben Regel in **Prozent** als Quermarkt-Kontrolle.

* **Suchzeitraum:** bis 2024-12-31
* **Holdout:** ab 2025-01-01

## Vorab festgelegte Auswertung

1. Anzahl Tage mit Auslöser (feuert die Regel überhaupt?)
2. Trefferquote gegen Break-even und gegen den gemessenen Basissatz
3. bp je Trade und $ je Trade nach Kosten; zusätzlich brutto
4. Anteil Ziel / Stop / Tagesende
5. CAGR bei fester Positionsgröße und bei 1 % Risiko je Trade
6. Empfindlichkeit über das Gitter; Fade als Kontrolle
7. Holdout und Quermarkt

## Urteilskriterien — festgelegt vor der Rechnung

Tragfähig nur, wenn **alle vier** erfüllt sind:

1. **$ je Trade nach Kosten > 0** im Suchzeitraum
2. **gleiches Vorzeichen im Holdout**
3. Trefferquote **signifikant über dem gemessenen Basissatz** (Binomialtest,
   einseitig, α = 0,05)
4. t über der Bonferroni-Schwelle für die **4 Hauptkombinationen**
   (2 Kostenmodelle × 2 Richtungen): **t > 2,50**

Danach wird nichts nachjustiert.
