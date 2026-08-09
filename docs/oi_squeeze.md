# Open-Interest-Squeeze — getestet

Vorschlag: Ein starker Anstieg des Open Interest bei stagnierendem Preis zeigt
Hebelaufbau. Bricht der Preis dann aus, liefert die Liquidation der Gegenseite
Treibstoff. Test: ΔOI > +2σ bei gleichzeitig enger Bollinger-Bandbreite
(< 10. Perzentil), Einstieg in Ausbruchsrichtung.

**Ergebnis: Die vorgeschlagene Kombination feuert praktisch nie. Open Interest
allein sieht auf BTC im Suchzeitraum stark aus, repliziert aber weder auf ETH
noch im Holdout.**

## Datenlage

| | |
|---|---|
| Quelle | Binance Futures Metrics (5-Min), auf 1h verdichtet |
| Zeitraum | 2023-01 bis 2026-06, **30.638 Stunden** je Asset |
| Felder | Open Interest, OI-Wert, Top-Trader-Long/Short-Ratios, Taker-Volumen-Ratio |
| Assets | BTC, ETH |
| Suchzeitraum | 2023-01 bis 2024-12 · **Holdout** ab 2025-01 |

## 1. Die Kombination existiert nicht

| Bedingung | BTC | ETH |
|---|---|---|
| ΔOI > 2σ **und** Bandbreite < 10. Perzentil | **0 Signale / 3,2 J.** | 1 |
| … < 20. Perzentil | **0** | 1 |
| … < 30. Perzentil | 3 | 4 |

Die beiden Bedingungen schließen einander faktisch aus: **Hoher OI-Aufbau geht
mit Bewegung einher, nicht mit Kompression.** Wer Hebel aufbaut, tut das, weil
sich etwas bewegt. Die These setzt einen Zustand voraus, den es in den Daten
nicht gibt.

## 2. Die 2×2-Anordnung

Effekt auf 24 h in bp, überlappungskorrigiert:

| Bedingung | BTC (Suche) | ETH (Suche) | BTC (Holdout) | ETH (Holdout) |
|---|---|---|---|---|
| (A) nur Ausbruch | −3,1 | −21,7 | −4,2 | −23,3 |
| **(B) + ΔOI > 2σ** | **+111,1** (p=0,035) | −9,1 | +17,9 (p=0,73) | +8,7 |
| (C) + Kompression | −23,1 | −62,7 | −3,2 | −12,7 |
| (D) beides | zu wenige | zu wenige | zu wenige | zu wenige |

Zwei Nebenbefunde:

- **Kompression schadet.** Ausbrüche aus enger Bandbreite sind auf beiden
  Assets schlechter als gewöhnliche (−23,1 und −62,7 gegen −3,1 und −21,7).
  Das ist das Gegenteil der verbreiteten „Squeeze"-Erzählung.
- Der reine 20-Bar-Ausbruch liefert wie erwartet nichts — konsistent mit dem
  Donchian-Ergebnis aus [`strategy_search.md`](strategy_search.md).

## 3. Der BTC-Befund ist stabil — innerhalb eines Assets und einer Periode

ΔOI > 2σ ohne Kompressionsfilter, Suchzeitraum:

| OI-Fenster | Ausbruch 12 h | 20 h | 40 h |
|---|---|---|---|
| 12 h | +110,2 | +99,7 | +112,3 |
| **24 h** | +113,5 | **+111,1** | +107,3 |
| 48 h | +41,9 | +53,3 | +71,4 |
| 72 h | +5,5 | −1,3 | +18,1 |

Sechs Zellen um +100 bis +113 bp, und der Abfall bei längeren OI-Fenstern
passt zur Erzählung: Es geht um **frischen** Hebelaufbau, nicht um alten.
6 von 24 Zellen positiv und p < 0,05 — bei einer Zufallserwartung von 1,2.

**Diese Zahl täuscht.** Die 24 Zellen sind **nicht unabhängig**: Sie nutzen
dieselben zwei Jahre, überlappende Fenster und stark korrelierte Signale. Es
sind nicht sechs Belege, sondern **ein Beleg aus sechs Blickwinkeln**.

## 4. Der Holdout entscheidet

Dieselben 24 Zellen, Zeitraum 2025-01 bis 2026-06:

**0 von 24 positiv und signifikant.**

| OI-Fenster | BTC Suche | BTC Holdout |
|---|---|---|
| 12 h | +99,7 bis +112,3 | −8,5 bis −43,9 |
| **24 h** | **+107,3 bis +113,5** | **+9,3 bis +17,9** |
| 72 h | −1,3 bis +18,1 | **+48,7 bis +63,9** |

Die Stärke **wandert**: Was im Suchzeitraum trug (12–24 h), ist im Holdout
schwach oder negativ; was dort schwach war (72 h), sieht jetzt gut aus. Auf
ETH ist der Holdout bei 72 h katastrophal (−104,8 bis −164,7 bp).

Ein wandernder Effekt ist kein Effekt.

## Fazit

| Frage | Antwort |
|---|---|
| Feuert OI-Spike + Kompression? | **Nein** — 0 Signale in 3,2 Jahren auf BTC |
| Hilft Kompression allein? | **Nein**, sie schadet (−23 bis −63 bp) |
| Hilft OI allein? | Auf BTC im Suchzeitraum ja (+111 bp), **sonst nirgends** |
| Hält es out-of-sample? | **Nein** — 0 von 24 Zellen |

Der Ansatz war strukturell der stärkste verbliebene, weil Open Interest eine
**beobachtbare Positionierung** ist und keine Preisableitung. Genau deshalb
war die Erwartung berechtigt — und genau deshalb ist das Ergebnis
aussagekräftig: Auch echte Positionierungsdaten liefern hier keinen
tragfähigen Vorlauf.
