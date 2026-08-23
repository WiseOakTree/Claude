# Gamma Exposure (GEX) — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-23, committet bevor gerechnet wurde.

## Anlass

Der Nutzer setzt einen GEX-Indikator ein (Dealer-Gamma aus Options-Open-Interest,
Gamma-Flip, Call-Wall, Put-Wall). Der Indikator behauptet vier Dinge. Diese
Untersuchung prüft sie.

## Datenlage — und warum sie das Urteil begrenzt

| | |
|---|---|
| Quelle | Binance Options **EOHSummary** (stündlich, je Instrument) |
| Felder | Strike, Typ, **Gamma der Börse**, **Open Interest**, Mark-IV |
| Zeitraum | 2023-05-18 bis 2023-10-23, **147 Tage / 3.493 Stunden** |
| Märkte | BTC, ETH |
| Regime | Net GEX negativ in 32,1 % (BTC) bzw. 55,0 % (ETH) der Stunden |

**Das ist wenig, und es ist nicht Deribit.** Deribit hält den Großteil des
Krypto-Options-Open-Interest; Binance ist der kleinere Buchteil. Ein tieferer
Verlauf ist mit frei zugänglichen Daten nicht zu bekommen: Deribits öffentliche
API liefert nur den **aktuellen** Buchstand, keine Historie je Strike.

Daraus folgt vorab: **Diese Untersuchung kann den Mechanismus prüfen, aber
keinen handelbaren Edge bestätigen.** Ein positiver Befund wäre ein Hinweis,
kein Beleg. Ein negativer Befund ist ebenfalls nur ein Hinweis — bei 147 Tagen
ist die Aussagekraft in beide Richtungen begrenzt. Das steht hier, damit es
hinterher nicht anders erzählt wird.

## Berechnung

Net GEX je Stunde = Σ über alle Strikes:
`Gamma × Spot² × 0,01 × Open Interest × (+1 für Calls, −1 für Puts)`

Gamma kommt von der Börse (nicht selbst gerechnet), Spot ist der Binance-
Stundenschluss desselben Assets. Call-Wall / Put-Wall = Strike mit dem größten
positiven / negativsten GEX-Beitrag der Stunde.

## Die vier Behauptungen

| | Behauptung des Indikators | Prüfung |
|---|---|---|
| **B1** | Negatives Gamma → Volatilität wird verstärkt | Rangkorrelation Net GEX gegen realisierte Vol der nächsten 24 h; Quintile; Mann-Whitney zwischen den Vorzeichengruppen |
| **B2** | Positives Gamma → Mean-Reversion, negatives → Trend | Korrelation ret(−24 h) mit ret(+24 h), getrennt je Regime |
| **B3** | Call-Wall / Put-Wall wirken als Widerstand / Unterstützung | Reaktion an der Wall gegen **Kontrolle**: zufälliger Strike mit gleichem Abstand zum Spot |
| **B4** | Der Gamma-Flip trennt die Regime | Realisierte Vol ober- und unterhalb des Flip-Levels |

## Überlappung — die Falle, die dieses Projekt schon einmal getroffen hat

Stündliche Beobachtungen mit 24-h-Zukunftsfenster überlappen 24-fach. Ein
t-Wert daraus ist wertlos. Deshalb:

* **Signifikanz wird ausschließlich auf nicht-überlappenden Tagesdaten
  gerechnet** — eine Beobachtung je Tag, **n = 147**.
* Die stündliche Auswertung wird nur **beschreibend** berichtet.

## Stabilität statt Holdout

147 Tage sind zu wenig für einen echten Holdout. Stattdessen: **erste Hälfte
gegen zweite Hälfte**. Ein Effekt, der nur in einer Hälfte auftritt, gilt als
nicht bestätigt. Das ist schwächer als ein Holdout, und es wird auch so genannt.

## Urteilskriterien — festgelegt vor der Rechnung

Eine Behauptung gilt als **bestätigt**, wenn:

1. der Effekt das vorhergesagte **Vorzeichen** hat,
2. er auf **Tagesdaten** signifikant ist (Bonferroni für 4 Behauptungen:
   **p < 0,0125**),
3. er in **beiden Hälften** dasselbe Vorzeichen hat,
4. und er in **beiden Märkten** (BTC und ETH) dasselbe Vorzeichen hat.

Sonst: **nicht bestätigt**. Es wird danach nichts nachjustiert, und es wird
keine fünfte Behauptung nachgereicht, falls die vier nicht liefern.
