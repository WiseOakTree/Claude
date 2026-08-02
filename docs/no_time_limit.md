# Ohne Zeitlimit ändert sich alles — Korrektur und bestes Ergebnis

**Korrektur:** Die gesamte bisherige Auswertung nutzte 90-Tage-Fenster als
„einen Challenge-Versuch". Das war **meine Modellannahme, keine Kraken-Regel** —
Kraken Prop hat keine begrenzte Laufzeit. In der Preset-Tabelle stand auch nie
eine Frist; ich habe sie stillschweigend hinzugefügt und nie hinterfragt.

Ohne Zeitlimit ist die richtige Frage ein **Erstpassage-Problem**: Wird +10 %
erreicht, *bevor* eine Abbruchbedingung greift — egal wie lange es dauert.

## Was sich dadurch ändert

| Strategie | 90 T (meine falsche Annahme) | **ohne Zeitlimit** |
|---|---|---|
| BTC einfach halten | 24,9 % | 24,1 % |
| Vol-Targeting 15 % | 24,8 % | **32,8 %** |
| S/R-Ausbruch (≥6, 48 h) | 33,9 % | **41,5 %** |

## Der eigentliche Befund: nicht der Drawdown wirft dich raus

| Strategie | Scheitern durch **6 % Drawdown** | durch **3 % Tagesverlust** |
|---|---|---|
| BTC einfach halten | 4,8 % | **95,2 %** |
| Vol-Targeting | 43,4 % | 56,6 % |
| S/R-Ausbruch | 4,2 % | **95,8 %** |

**Über 95 % aller Fehlschläge kommen vom Tagesverlustlimit, nicht vom
Drawdown.** Das erklärt rückwirkend auch, warum das Drawdown-Limit in der
Regel-Sensitivität ([`prop_rules.md`](prop_rules.md)) ab 6 % wirkungslos war.

## Die Konsequenz: kleiner handeln, länger brauchen

Ohne Frist gibt es keinen Grund, schnell zu sein. Und ein Tagesverlust von 3 %
ist ein **Tail-Ereignis** — halbiert man die Position, sinkt seine
Wahrscheinlichkeit überproportional:

| Positionsgröße | Tage unter −3 % (S/R) |
|---|---|
| 1,00× | 2,00 % |
| 0,50× | 0,36 % |
| 0,35× | 0,10 % |
| 0,25× | 0,05 % |

Das ist theoretisch sauber: Für einen Prozess mit **positivem** Erwartungswert
steigt die Wahrscheinlichkeit, die obere Schranke vor der unteren zu erreichen,
wenn man die Volatilität senkt. Nur die Dauer wächst.

**Damit kehrt sich meine frühere Empfehlung um.** Die „optimalen 15–16 %
Zielvolatilität" aus [`required_edge.md`](required_edge.md) gelten nur **unter
Zeitdruck** — bei einer 90-Tage-Frist muss man groß genug handeln, um das Ziel
zu erreichen. Ohne Frist gilt das Gegenteil.

## Die ehrlichen Zahlen (S/R-Strategie, 365-Tage-Deckel)

Bei kleinen Positionen laufen viele Versuche am Datenende noch — die werden
hier **als gescheitert gewertet** (konservative Untergrenze), sonst wäre die
Quote geschönt.

| Größe | Quote (nur gelöste) | **Untergrenze** | zensiert | Ø Dauer |
|---|---|---|---|---|
| 1,00× | 41,5 % | 39,6 % | 4,6 % | 43 Tage |
| 0,70× | 37,7 % | 34,7 % | 8,0 % | 71 Tage |
| **0,50×** | **60,1 %** | **49,4 %** | 17,9 % | 119 Tage |
| 0,35× | 66,0 % | 48,6 % | 26,4 % | 191 Tage |
| 0,25× | 59,3 % | 33,4 % | 43,6 % | 249 Tage |

Out-of-Sample (Untergrenze als Maßstab):

| Größe | 1. Hälfte | 2. Hälfte | Urteil |
|---|---|---|---|
| 1,00× | 38,0 % | 33,5 % | stabil |
| **0,50×** | 33,7 % | **40,1 %** | **stabil** |
| 0,35× | 48,3 % | 37,0 % | fällt ab |
| 0,25× | 48,2 % | **18,7 %** | **bricht ein** |

**0,5× ist der belastbare Punkt.** Darunter wird die Zensierung so groß, dass
die Zahlen nicht mehr tragen — die 97,9 % bei 0,15× sind reines Artefakt
(46,9 % der Versuche unaufgelöst).

## Zusammenfassung

| | Pass-Rate |
|---|---|
| Ausgangspunkt: Renko-Reversal, look-ahead-frei | **7 %** |
| S/R-Ausbruch, volle Größe, 90-Tage-Annahme | 33,9 % |
| S/R-Ausbruch, volle Größe, ohne Zeitlimit | 41,5 % |
| **S/R-Ausbruch, halbe Größe, ohne Zeitlimit** | **~40–50 %** |

Praktisch: **etwa die Hälfte der Positionsgröße handeln, die eine
15-%-Zielvolatilität ergäbe, und mit rund vier Monaten bis zum Ziel rechnen.**

## Was weiterhin gilt

- Die Parameterwahl der S/R-Strategie (≥6 Berührungen, 48 h) ist aus
  24 Varianten ausgewählt; der *Effekt* ist robust belegt
  ([`sr_breakout.md`](sr_breakout.md)), die konkrete Quote ist optimistisch.
- Das gefundete Konto unterliegt danach weiter dem Drawdown-Limit
  ([`trading_as_job.md`](trading_as_job.md)). Ein besserer Einstieg ist kein
  besserer Bestand — und bei kleiner Positionsgröße dauert auch das Verdienen
  entsprechend lange.
- Alles gemessen auf BTC 1h über 4,5 Jahre, mit 16 bp Kosten je Roundtrip.
