# Renko + MACD + Open Interest — Spezifikation VOR der Rechnung

Festgelegt am 2026-08-21, committet bevor gerechnet wurde.

## Das Setup, wie es auf dem Chart steht

Vom Nutzer beschrieben:

* Renko, **Quelle OHLC** (nicht Close)
* **Boxgröße 1 % vom letzten Kurs** (LTP, prozentual)
* **MACD** auf dem Renko-Chart
* **Long:** MACD-Kreuzung nach oben **und** positives Open Interest
* **Short:** MACD-Kreuzung nach unten **und** das Gegenteil

## Was daran technisch nachgebaut werden muss

Drei Dinge unterscheiden diesen Chart vom bisherigen Renko im Projekt. Alle
drei ändern die Brick-Reihe — und damit den MACD, der auf ihr rechnet.

| | bisher im Projekt | hier nachzubauen |
|---|---|---|
| Quelle | nur Schlusskurs | **OHLC** — auch Dochte erzeugen Bricks |
| Boxgröße | ATR(14) × 1,0 | **1 % vom Kurs**, mit dem Kurs mitwachsend |
| Umkehr | 1-Box-Gitter | **2 Boxen** (TradingView „Traditional") |

**Reihenfolge innerhalb einer Bar:** Ohne Tickdaten ist unbekannt, ob zuerst
das Hoch oder das Tief kam. Es wird pessimistisch das **gegenläufige Extrem
zuerst** verarbeitet (bei steigender Bar erst das Tief, dann das Hoch). Das
erzeugt eher zusätzliche Gegen-Bricks als zusätzliche Trendbricks.

**MACD (12/26/9) rechnet auf den Brick-Schlusskursen**, nicht auf Zeitbars —
genau wie auf dem TradingView-Chart. Kreuzung MACD-Linie über Signallinie =
long, darunter = short.

## Die Falle, um die es hier eigentlich geht

Ein Renko-Brick schließt auf einem **Gitter-Level**, das *innerhalb* einer
Kerze erreicht wurde. Wer dort einsteigt, füllt zu einem Preis, der **vor** der
Information liegt, die das Signal erzeugt hat. Dieses Projekt hat diesen Fehler
schon einmal gemacht und die Ergebnisse zurückgezogen: künstlicher Vorteil von
**~0,34 % je Trade** ([`realism.md`](realism.md)).

Der **TradingView-Strategietester macht auf Renko-Charts genau das.** Deshalb
wird hier beides gerechnet und gegenübergestellt:

| Variante | Fill | entspricht |
|---|---|---|
| **TV-Stil** | zum Brick-Schluss (Gitter-Level) | dem, was der Strategietester zeigt |
| **ehrlich** | zum Schlusskurs der 1-h-Bar, auf der der Brick entstand | dem, was handelbar ist |

Die Differenz zwischen beiden ist die vorab wichtigste Zahl dieser
Untersuchung.

## Open Interest

Quelle: Binance Futures Metrics (5-Min-Snapshots, auf 1 h verdichtet),
2023-01 bis 2026-07. Sechs Märkte: BTC, ETH, SOL, XRP, DOGE, ADA.

„Positives Open Interest" ist mehrdeutig. **Vorab festgelegte Hauptdefinition:**

> OI am Signalbar **höher als 24 h zuvor** (ΔOI > 0). Für long wird steigendes
> OI verlangt, für short ebenfalls steigendes OI — steigendes OI heißt „neues
> Geld baut Positionen auf", unabhängig von der Richtung.

Weil die Formulierung im Alltag auch anders gemeint sein kann, werden **vier
weitere Lesarten** als Empfindlichkeitsprüfung mitgerechnet und **alle**
berichtet — nicht nur die beste:

1. ΔOI über 1 h > 0
2. ΔOI über 168 h (1 Woche) > 0
3. OI über seinem Mittel der letzten 24 h
4. OI-**Wert** (in USD) statt Kontraktzahl, ΔOI über 24 h > 0

Zusätzlich als Kontrolle: **ΔOI < 0** (die umgekehrte Bedingung) und **ohne
OI-Filter**. Wenn der Filter etwas leistet, muss er besser sein als sein
Gegenteil und besser als gar kein Filter.

## Risikomanagement

Es wird die Leiter aus [`renko_trail_spec.md`](renko_trail_spec.md) benutzt,
in drei Ausprägungen:

| | Aufbau |
|---|---|
| **M0** | Stop-and-Reverse (Ausstieg erst beim Gegensignal), kein Stop |
| **M1** | harter Stop, 2 Boxen |
| **M2** | harter Stop + Break-even + Trailing (2 Boxen) |

Stop-Distanz = 2 Boxen = 2 % vom Kurs. Risiko 0,5 % des Kontos je Trade.

## Kosten

Unverändert zur laufenden Untersuchung: **8 bp je Seite** (16 bp Roundtrip),
Funding 0,01 % je 8 h, **5 bp zusätzlich auf jede Stop-Ausführung**,
Gap-Regel (Lücke füllt zur Eröffnung).

## Daten und Zeiträume

1-h-Bars, sechs Märkte. Der Zeitraum ist durch die OI-Daten begrenzt:

* **Suchzeitraum:** 2023-01 bis 2024-12-31
* **Holdout:** 2025-01-01 bis 2026-07-31

BTC gilt in diesem Projekt als Holdout-verbraucht und wird im Holdout-Urteil
nur nachrichtlich geführt.

## Vorab festgelegte Auswertung

1. bp je Trade nach Kosten, gepoolt und je Markt — TV-Stil **und** ehrlich
2. die Differenz zwischen beiden Fill-Modellen, in bp je Trade
3. Erwartungswert in R, Trefferquote, Ø Gewinn/Verlust in R
4. Wirkung des OI-Filters: mit / ohne / umgekehrt, alle fünf Lesarten
5. Anzahl Signale je Lesart (ein Filter, der fast alles durchlässt, ist keiner)
6. Risiko-Treue und Tage über dem 3-%-Limit je Managementstufe
7. Holdout für alles

## Urteilskriterien — festgelegt vor der Rechnung

Die Strategie gilt als tragfähig, wenn **alle vier** Bedingungen erfüllt sind:

1. **ehrlicher** Fill, bp je Trade nach Kosten **> 0** im Suchzeitraum
2. **gleiches Vorzeichen** im Holdout (5 Märkte ohne BTC)
3. der OI-Filter schlägt **sowohl** „kein Filter" **als auch** sein eigenes
   Gegenteil — sonst ist er Dekoration
4. t-Wert über der Bonferroni-Schwelle für die **21 gerechneten Kombinationen**
   (7 OI-Lesarten × 3 Managementstufen): **t > 3,09** (zweiseitig, α = 0,05/21)

Wird eine Bedingung verfehlt, lautet das Urteil: **nicht tragfähig.** Es werden
danach keine Parameter nachjustiert.
