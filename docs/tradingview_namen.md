# Wie die Indikatoren in TradingView heißen

Zuordnung von dem, was in
[`risiko_indikatoren.md`](risiko_indikatoren.md) gemessen wurde, zu dem, was
du in TradingView tatsächlich anklicken kannst.

> **Was ich prüfen konnte und was nicht:** Die Messwerte in den Tabellen unten
> stammen aus eigenen Rechnungen auf echten Kursdaten. Die **Namen der
> eingebauten TradingView-Indikatoren** stammen aus meinem Wissen — ich habe
> von hier keinen Zugang zu TradingView und konnte sie nicht nachschlagen.
> Wenn ein Name nicht exakt stimmt, such nach dem Stichwort in Klammern.

---

## Die drei, die du benutzt

| bei mir | in TradingView | Suchbegriff |
|---|---|---|
| MACD (12/26/9) | **MACD** | „MACD" |
| Stochastik (14/3/3) | **Stochastic** | „Stochastic" *(nicht „Stochastic RSI" — das ist etwas anderes)* |
| Bollinger-Bänder (20/2) | **Bollinger Bands** | „Bollinger Bands" |
| Bollinger %B (die Lage im Band) | **Bollinger Bands %B** | „%B" |
| **Bollinger-Breite** (das Risikomaß) | **Bollinger Bands Width** | „Bollinger Bands Width" oder „BBW" |

---

## Die Risikomaße: was eingebaut ist

| Rang¹ | bei mir | in TradingView eingebaut? | Name dort |
|---|---|---|---|
| 1 | DVOL (implizite Vol) | **nein** — ist ein eigenes Symbol, kein Indikator | siehe unten |
| 2 | **Abwärts-Semivol** | **nein** | — |
| 3 | EWMA (λ 0,94) | **nein** | — |
| 4 | ATR(14) | **ja** | **Average True Range** |
| 5 | realisierte Vol 20 T | **ja** | **Historical Volatility** |
| 6 | größter Rückgang 10 T | teilweise | **Ulcer Index** *(misst Rückgänge, andere Formel)* |
| 7 | Parkinson (Hoch-Tief) | nein | — |
| 9 | **Bollinger-Breite** | **ja** | **Bollinger Bands Width** |
| 10 | Garman-Klass | nein | — |
| 14 | Volumen / Ø20 | teilweise | **Relative Volume** |

*¹ Rang nach Rangkorrelation mit einem Tag von −3 % oder schlechter,
BTC-Holdout 2025-26.*

**Kurz: Von den fünf Maßen, die besser sind als die Bänder, sind zwei
eingebaut (ATR, Historical Volatility) und drei nicht.**

---

## Der wichtigste ist kein Indikator, sondern ein Symbol

**DVOL** (0,210 gegen 0,078 für die Bänder) ist kein Indikator, den man auf
den Chart legt — es ist ein **eigenes Instrument**, wie ein Kurs. Du öffnest
es über die Symbolsuche, nicht über „Indikatoren".

| Markt | Was du suchst |
|---|---|
| Aktien / S&P 500 | **VIX** — Kürzel `TVC:VIX` oder `CBOE:VIX` |
| Nasdaq | **VXN** |
| BTC / ETH | Suchbegriffe: **DVOL**, **BVIV**, **EVIV**, **BitVol** |

Für Krypto **kann ich dir nicht sagen, was in deinem Plan verfügbar ist** —
das hängt vom Datenanbieter ab. Wenn nichts davon auftaucht, geht der Wert
direkt bei Deribit, kostenlos und ohne Anmeldung:

```
https://www.deribit.com/api/v2/public/get_volatility_index_data
   ?currency=BTC&resolution=1D
   &start_timestamp=...&end_timestamp=...
```

Im Indikator unten ist ein Feld dafür: Symbol eintragen, fertig.

---

## Für die drei, die es nicht gibt: fertiger Code

`tradingview/risiko_panel.pine` in diesem Repository. Ein Fensterindikator, der
alle sieben Maße nebeneinander zeigt — inklusive der Bollinger-Breite zum
Vergleich.

**Er setzt zwei gemessene Befunde direkt um:**

1. **Er zeigt Perzentile, keine absoluten Werte.** Weil das Niveau nicht
   prognostizierbar ist (Out-of-Sample-R² fast überall negativ, Bollinger
   −0,134) und feste Schwellen in zwei Jahren falsch geeicht sind.
2. **Er steuert nichts.** Keine Positionsgröße, kein Signal — nur eine
   Tabelle. Weil gemessen ist, dass Vol-Steuerung die Pass-Rate um 9–15
   Punkte senkt.

Die Tabelle oben rechts zeigt je Maß: Rohwert, Perzentil und Lage
(sehr niedrig / niedrig / mittel / hoch / sehr hoch), rot ab dem obersten
Fünftel.

### Die eine Zeile, um die es geht

Wenn du nur eine Sache änderst — die Abwärts-Semivol statt der Bänder:

```pine
r     = math.log(close / close[1])
rNeg  = r < 0 ? r : 0.0
semiv = ta.stdev(rNeg, 20) * math.sqrt(barsPerYear)
rang  = ta.percentrank(semiv, 1000)     // 0..100
```

Dieselbe Standardabweichung wie immer, aber nur über die Verlust-Bars. Für die
Bollinger-Breite sind ein Aufwärtsschub und ein Absturz dasselbe — für dein
Konto nicht.

### Einstellung

| | |
|---|---|
| Chart | 4h (dein Zeitrahmen) |
| Fenster für Vol-Maße | 20 Bars |
| Perzentil-Fenster | 1000 Bars ≈ 6 Monate auf 4h |
| Als Perzentil zeichnen | **an** |

---

## Was du damit machst — und was nicht

| | |
|---|---|
| ✅ **Sehen, ob die Lage gerade ruhiger oder wilder ist als sonst** | dafür sind die Perzentile da |
| ✅ **Wissen, wann du der laufenden Position weniger trauen solltest** | oberstes Fünftel = größere Verlusttage |
| ❌ **Positionsgröße daran koppeln** | gemessen: −9 bis −15 Punkte Pass-Rate |
| ❌ **Feste Schwellen wie „über 60 % halbiere ich"** | Niveau verschiebt sich, R² wird negativ |
| ❌ **Ein Ein- oder Ausstiegssignal daraus bauen** | über die Richtung sagen alle Vol-Maße nichts |

---

*Indikator: `tradingview/risiko_panel.pine`. Messungen:
[`risiko_indikatoren.md`](risiko_indikatoren.md),
[`indikatoren_als_info.md`](indikatoren_als_info.md).*
