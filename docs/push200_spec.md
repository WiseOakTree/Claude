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

Mit den **gemessenen 8 bp** des Nutzers und 200 $ Ziel auf BTC bei 79.000 $
sind das **31,6 %** — und die Break-even-Trefferquote bei symmetrischem Ziel
und Stop liegt damit bei **65,8 %** statt bei 50 %. Diese Zahl wird der
gemessenen Trefferquote gegenuebergestellt.

Fuer groessere Ziele faellt sie schnell:

| Ziel | in bp | Kosten-Anteil | Break-even-Trefferquote (1:1) |
|---|---|---|---|
| 200 $ | 25,2 | 31,6 % | **65,8 %** |
| 500 $ | 63,1 | 12,7 % | 56,3 % |
| 1.000 $ | 126,1 | 6,3 % | 53,2 % |
| 2.000 $ | 252,3 | 3,2 % | 51,6 % |

## Kostenmodell — aus einem echten Trade des Nutzers abgeleitet

Nachtrag vor der Rechnung: Der Nutzer hat einen realen Trade gezeigt
(Short 0,387 BTC @ 79.272,30, Ausstieg 78.953,20, angezeigter Netto +99,00 $
bei 12 EUR Gebuehr je Seite). Daraus laesst sich die Reibung ausrechnen statt
sie zu schaetzen:

| | |
|---|---|
| Nominal | 30.678,38 $ |
| Bruttogewinn (319,10 $ Bewegung) | 123,49 $ |
| angezeigter Netto | 99,00 $ |
| **Gebuehr gesamt** | **24,49 $** (= 24 EUR) |
| **Roundtrip** | **7,98 bp** (3,99 bp je Seite) |
| Anteil am Bruttogewinn dieses Trades | **19,8 %** |

Gerechnet wird deshalb mit **4 bp je Seite**, plus 2 bp zusaetzlicher Slippage
auf Stop-Ausfuehrungen (Markt-Order in die Bewegung hinein). Roundtrip:
**8 bp bei Gewinn, 10 bp bei Stop.**

Zusaetzlich gerechnet: ein pessimistisches Taker-Modell (16 bp) und ein
**Nullkosten-Lauf**, um zu trennen, was Marktverhalten und was Reibung ist.

**Wichtiger Vorbehalt:** Ob die 12 EUR eine **prozentuale** oder eine **feste**
Gebuehr sind, geht aus einem einzelnen Trade nicht hervor. Bei einer festen
Gebuehr haengt alles an der Positionsgroesse — bei 10.000 $ Nominal waeren es
24,5 bp statt 8, und die Kosten fraessen dann **97 % eines 200-$-Ziels**. Das
wird im Ergebnis mitberichtet.

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
