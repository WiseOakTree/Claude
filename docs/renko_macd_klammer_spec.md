# Renko + MACD + OI mit fester Klammer — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-21, committet bevor gerechnet wurde.
Ergänzung zu [`renko_macd_oi_spec.md`](renko_macd_oi_spec.md): dort war der
Ausstieg nicht definiert, hier ist er es.

## Der Ausstieg, wie ihn der Nutzer definiert hat

> Stop-Loss **3 Bricks**, Take-Profit **6 Bricks**, Risiko **1 % je Trade**.

Bei Boxgröße 1 % heißt das:

| | |
|---|---|
| Stop | 3 Boxen = **3 %** Kursabstand |
| Ziel | 6 Boxen = **6 %** Kursabstand |
| CRV | **1 : 2** |
| Risiko je Trade | 1 % des Kontos |
| Positionsgröße | 1 % / 3 % = **0,33× Kontostand** an Nominal |

Damit ist der Trade eine **feste Klammer**: Was zuerst berührt wird, beendet
ihn. Das ist ein anderes System als das bisher gerechnete, wo das Gegensignal
den Ausstieg lieferte.

## Warum diese Klammer die Frage vereinfacht

Bei festem CRV 1:2 hängt der Erwartungswert nur noch an **einer** Zahl:

> E = p · 2R − (1 − p) · 1R − Kosten

Ohne Kosten ist der Break-even bei **p = 33,33 %**. Mit 16 bp Roundtrip auf
0,33× Nominal ≈ 0,053 % des Kontos je Trade, also ≈ 0,053 R, verschiebt sich
der Break-even auf **p ≈ 35,1 %** (inkl. Stop-Slippage etwas höher).

Die ganze Untersuchung reduziert sich damit auf: **Trifft der Aufbau öfter als
etwa 35 %?**

## Die Vergleichsgröße, die darüber entscheidet

Ein Kursverlauf ohne Vorhersagbarkeit trifft die 6-%-Marke vor der 3-%-Marke
mit einer Wahrscheinlichkeit, die allein vom **Verhältnis der Abstände**
abhängt — nicht vom Chart, nicht vom Indikator:

> P(+6 % vor −3 %) ≈ 3 / (3 + 6) = **33,3 %**

Das ist exakt der Break-even. **Ein CRV von 1:2 ist keine Verbesserung der
Chancen, sondern nur eine andere Aufteilung derselben Chancen.** Wer 1:2 wählt,
gewinnt seltener und dafür mehr — der Erwartungswert bleibt gleich, die Kosten
bleiben aber auch.

Deshalb wird die Trefferquote der Strategie **nicht** gegen die Theorie
gemessen, sondern gegen den **gemessenen Basissatz derselben Märkte**: für
**jeden** Bar wird geprüft, ob von dort aus +6 % vor −3 % erreicht wurde (long)
bzw. −6 % vor +3 % (short). Horizont 2.160 Bars (90 Tage); der Anteil
unaufgelöster Fälle wird berichtet.

Nur die **Differenz** zwischen Strategie-Trefferquote und Basissatz ist ein
möglicher Edge.

## Was gerechnet wird

Vier Hauptkombinationen:

| | Einstieg | Ausstieg |
|---|---|---|
| **K1** | MACD-Kreuzung + ΔOI 24 h > 0 | feste Klammer, Gegensignale ignoriert |
| **K2** | MACD-Kreuzung + ΔOI 24 h > 0 | Klammer **und** Drehen am Gegensignal |
| **K3** | MACD-Kreuzung ohne OI-Filter | feste Klammer |
| **K4** | MACD-Kreuzung ohne OI-Filter | Klammer und Drehen |

Zusätzlich als **Empfindlichkeitsprüfung** (ausdrücklich ohne
Signifikanzanspruch, es wird daraus nichts ausgewählt): Ziel bei 1R, 2R, 3R,
4R und Stop bei 2, 3, 4 Boxen.

Alles unverändert: 6 Märkte, 1 h, 2023-01 bis 2026-07, Suche bis 2024-12,
Holdout ab 2025-01 (BTC nur nachrichtlich), 8 bp je Seite, Funding, 5 bp extra
auf Stop-Ausführungen, Gap-Regel, **Stop zählt vor Ziel**, wenn beide in
derselben Bar liegen, Fill zum Bar-Schluss.

## Vorab festgelegte Auswertung

1. Trefferquote je Kombination, gegen den Break-even und gegen den Basissatz
2. bp je Trade und Ø R nach Kosten
3. Anteil der Trades, die am Ziel / am Stop / am Periodenende schließen
4. durchschnittliche Haltedauer bis Ziel und bis Stop
5. Konto-Ebene: Rendite, max. Drawdown, Tage über dem 3-%-Limit
6. Empfindlichkeit über die CRV- und Stop-Gitter
7. Holdout für alles

## Urteilskriterien — festgelegt vor der Rechnung

Tragfähig nur, wenn **alle vier** erfüllt sind:

1. Trefferquote im Suchzeitraum **über dem kostenbereinigten Break-even**
2. bp je Trade **> 0** im Suchzeitraum **und** gleiches Vorzeichen im Holdout
3. Trefferquote **signifikant über dem gemessenen Basissatz** derselben Märkte
   (Binomialtest, einseitig, α = 0,05)
4. t-Wert über der Bonferroni-Schwelle für 4 Hauptkombinationen: **t > 2,50**

Danach wird nichts nachjustiert. Die Empfindlichkeitsprüfung dient der
Einordnung, nicht der Auswahl.
