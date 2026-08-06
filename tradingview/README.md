# TradingView-Indikator: Renko-Reversal Levels

`renko_reversal_levels.pine` — die Strategie als TradingView-Indikator (Pine v6).

## Das Wichtigste: du brauchst KEINEN Renko-Chart

Der Indikator berechnet die Renko-Bricks **intern aus normalen Kerzen**. Damit
umgeht er die Einschränkung, dass Renko-/Kagi-/PnF-Charts im Gratis-Plan nicht
frei verfügbar sind. Leg ihn einfach auf einen **normalen Kerzenchart im
1-Stunden-Timeframe** — genau den Timeframe, auf dem die Strategie validiert ist.

## Installation

1. TradingView öffnen → **Pine Editor** (unten am Chart; auf dem Handy dafür die
   Desktop-Ansicht im Browser nutzen — die App hat keinen Pine Editor).
2. Inhalt von `renko_reversal_levels.pine` hineinkopieren.
3. **Zum Chart hinzufügen**.
4. Chart auf **1h** und ein Paar wie BTCUSD stellen.

## Was er anzeigt

- **Buy-Stop / Sell-Stop**: das kommende Trigger-Level — **dort die Order vorab
  platzieren**. Das ist der ganze Punkt (siehe [../docs/realism.md](../docs/realism.md)).
- **SL** (2 Bricks) und **TP1/TP2** (R-Vielfache).
- **Info-Tabelle**: Position, Brick-Größe, Order-Level, SL/TP, Positionsgröße —
  und eine Warnung, wenn der Timeframe nicht 1h ist.
- **Anker-Linie**: das Renko-Gitter (Schlusskurs des letzten Bricks).
- **Marker** für historische Signale.

Voreinstellungen entsprechen der validierten Config: `ATR(14) × 0.75`,
2-Brick-Reversal, SL 2 Bricks, 0.3 % Risiko.

Bricks werden nur auf **geschlossenen** Kerzen fortgeschrieben → kein Repainting.
Die Level wandern mit ATR und Trend, also Orders regelmäßig nachziehen (dafür
gibt es den Alarm „Level verschoben").

## Alarme

Über das Glocken-Symbol einrichten:
- `Renko: LONG-Reversal` / `Renko: SHORT-Reversal` — Signal hat ausgelöst
- `Renko: Level verschoben` — Trigger-Level haben sich geändert, Orders anpassen

## Validierung

Die Pine-Logik wurde 1:1 nach Python portiert und gegen die Backtest-Bibliothek
geprüft: **45/45 identische Signale**, maximale Preisabweichung `0.00000000`.
Der Indikator rechnet also genau wie der getestete Backtester.

## ⚠️ Warum nicht Tages-Renko

Auf Tages-Bricks ist es eine **andere, nicht funktionierende Strategie**. Gemessen
über 4 Jahre BTC:

| | 1h (validiert) | 1D (Tages-Bricks) |
|---|---|---|
| Signale pro Jahr | 433 | 19 |
| Stop-Breite | 0,93 % | **5,33 %** |
| Profit Factor | 2,02 | 3,03 |
| **Pass-Rate (90-Tage-Fenster)** | **91 %** | **0 %** |

Die Qualität je Trade ist auf Tagesbasis sogar besser (PF 3,03) — aber mit 19
Signalen pro Jahr und 5,33 % breiten Stops ist es viel zu langsam für ein
10 %-Ziel. Mit mehr Risiko gegengesteuert:

| Risiko | Pass-Rate (180-Tage-Fenster) | Worst-Drawdown |
|---|---|---|
| 0,3 % | 0 % | 2,3 % |
| 1,0 % | 33 % | 7,4 % |
| 2,0 % | 35 % | 14,3 % |
| 3,0 % | 21 % | 20,7 % |

Jede Variante, die überhaupt Ziele trifft, reißt das **6 %-Limit** um das
2–3-Fache. Tages-Renko ist für diese Challenge nicht brauchbar — nutze 1h-Kerzen
(dafür braucht es kein Abo).

---

## `risiko_panel.pine` — Risikomaße statt Bänder

Kein Signalgeber. Ein Fensterindikator, der sieben Volatilitätsmaße als
**Perzentil** nebeneinander zeigt, inklusive der Bollinger-Breite zum
Vergleich.

Hintergrund: Gemessen an der Rangkorrelation mit einem Tag von −3 % oder
schlechter (dem Kraken-Tageslimit), BTC-Holdout 2025-26:

| Maß | Rangkorrelation | in TradingView eingebaut? |
|---|---|---|
| DVOL (implizite Vol) | **0,210** | nein — eigenes Symbol |
| **Abwärts-Semivol** | **0,166** | nein → hier drin |
| EWMA (λ 0,94) | 0,155 | nein → hier drin |
| ATR(14) | 0,143 | ja (Average True Range) |
| realisierte Vol | 0,129 | ja (Historical Volatility) |
| **Bollinger-Breite** | **0,078** | ja (Bollinger Bands Width) |

Zwei Dinge, die der Indikator bewusst **nicht** tut:

- **Keine absoluten Schwellen.** Das Vol-Niveau ist nicht prognostizierbar
  (Out-of-Sample-R² fast überall negativ, Bollinger −0,134) — nur der Rang.
  Deshalb Perzentile.
- **Keine Positionssteuerung.** Gemessen: Vol-gesteuerte Größe senkt die
  Pass-Rate um 9–15 Punkte gegenüber fester Größe, obwohl der Drawdown fällt.
  Das Regelwerk hat ein Ziel, und Volatilität ist der Weg dorthin.

Einstellung: 4h-Chart, Vol-Fenster 20 Bars, Perzentil-Fenster 1000 Bars
(≈ 6 Monate). Details in [`../docs/tradingview_namen.md`](../docs/tradingview_namen.md).
