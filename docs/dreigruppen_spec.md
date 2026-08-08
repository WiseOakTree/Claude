# Drei-Gruppen-Vergleich — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-08, committet bevor gerechnet wurde.

## Die Frage

> Unterscheiden sich **Indikator-Trader**, **Bauchgefühl-Trader** und **Zufall**
> in ihrem Ergebnis je Trade — oder sind sie ununterscheidbar?

Wenn 1 ≈ 2 ≈ 3, ist das eine deutlich stärkere Aussage als „eine Regel hat
den Vorwärtstest nicht bestanden".

## Gruppe 1 — Indikator-Trader

Die 25 kanonischen Regeln aus [`finaltest_spec.md`](finaltest_spec.md).
Lehrbuchparameter, keine Optimierung. **Liegt bereits vor.**

## Gruppe 2 — Bauchgefühl-Trader

Hier steckt die eigentliche Arbeit: „Bauchgefühl" muss operationalisiert
werden, ohne es zu einem Indikator zu machen. Zwei unabhängige Besetzungen.

### 2a — simulierte Intuition (10 Heuristiken)

Keine Schwellen, keine Parameter aus der Literatur — nur das, was ein Mensch
beim Draufschauen tut. Jede Regel beschreibt eine **Wahrnehmung**, nicht eine
Berechnung.

| Heuristik | Umsetzung |
|---|---|
| „sieht bullish aus" | letzte 24 h gestiegen → long |
| „sieht bearish aus" | letzte 24 h gefallen → short |
| „ist überverkauft" | stärkster Rückgang der letzten 7 Tage → long |
| „ist überkauft" | stärkster Anstieg der letzten 7 Tage → short |
| „fühlt sich nach Breakout an" | nahe 7-Tage-Hoch **und** Volumen über Schnitt → long |
| „läuft heiß" | drei grüne Tageskerzen in Folge → long |
| „fällt ins Messer" | drei rote Tageskerzen in Folge → short |
| „runde Zahl" | Kurs kreuzt eine runde Marke → in Kreuzungsrichtung |
| „große Kerze, da passiert was" | Tagesbewegung im obersten Fünftel → in ihre Richtung |
| „war lange ruhig, jetzt geht's los" | Ausbruch nach der ruhigsten Woche → in Ausbruchsrichtung |

### 2b — echte Menschen

Die **41.362 on-chain verifizierten Hyperliquid-Konten**. Kein Modell,
sondern gemessenes Verhalten echter Trader mit echtem Geld.

Vergleichbar gemacht über **PnL je gehandeltem Volumen in Basispunkten**.
Da Börsen jede Seite einzeln als Volumen zählen, wird der Wert **verdoppelt**,
um ihn auf „je Roundtrip" zu bringen.

## Gruppe 3 — Zufall

Wie in der Spezifikation des finalen Tests: gleiche Anzahl Trades, gleiche
Haltedauer, gleiche Long/Short-Quote, gleiche Kosten, dieselbe Kursreihe.
Nur Zeitpunkt und Richtung gewürfelt.

## Gemeinsamer Maßstab

Alle Gruppen werden in **Basispunkten je Trade nach Kosten** gemessen.
14 Märkte, 1 h, 48 h Halten, 16 bp je Roundtrip.

## Vorab festgelegte Auswertung

1. Verteilung je Gruppe: Median, Quartile, Spanne
2. **Kruskal-Wallis-Test** über die drei Gruppen (verteilungsfrei)
3. Paarweise Mann-Whitney-U mit Holm-Korrektur
4. Zusätzlich: Überlappung der Verteilungen

| Ergebnis | Schlussfolgerung |
|---|---|
| kein Gruppenunterschied (p ≥ 0,05) | **1 ≈ 2 ≈ 3** — Indikatoren und Intuition sind von Zufall nicht zu unterscheiden |
| Gruppenunterschied (p < 0,05) | die Gruppen sind unterscheidbar; Richtung wird berichtet |

Es wird **keine Heuristik und keine Regel nach Sichtung der Ergebnisse
geändert**.
