# Bounce statt Ausbruch, Parametersuche und Liquidität — getestet

Vorschlag: die besten S/R-Parameter suchen, **an der Unterstützung kaufen und
am Widerstand verkaufen**, und die Liquidität an den Levels heranziehen, um zu
wissen, wo Stops sinnvoll liegen.

**Ergebnis in einem Satz: Der Bounce ist widerlegt, der Ausbruch bestätigt sich
out-of-sample deutlich — und die Liquiditätsdaten tragen nichts bei.**

## Aufbau

| | |
|---|---|
| Suchzeitraum | 2021-03 bis 2024-12 (33.635 Bars) — hier wurde optimiert |
| **Holdout** | **2025-01 bis 2026-06 (13.104 Bars) — genau einmal angefasst** |
| Kombinationen im Suchlauf | 420 (Pivot-Weite × Toleranz × Alter × Berührungen) |
| Liquidität | Binance-Orderbuchtiefe, 971 Tage (Glassnode ist ohne Bezahlplan gesperrt) |

Die Level-Logik wurde vorher aus fünf Forschungsskripten nach
`src/prop_backtester/levels.py` gezogen und gegengeprüft: auf den alten
Parametern liefert das Modul **bit-identisch** 775 Ereignisse und +42,88 bp.
14 neue Tests, darunter der Look-ahead-Nachweis über drei Pivot-Weiten.

## 1. Der Bounce funktioniert nicht — und zwar systematisch

420 Kombinationen, Suchzeitraum:

| | Bounce | Ausbruch |
|---|---|---|
| Median-Effekt (24 h) | **−7,62 bp** | +8,26 bp |
| Anteil positiv | 23,3 % | 75,5 % |
| signifikante Ergebnisse | 43 — davon **41 negativ** | 34 |

Die Dosis-Wirkung läuft **monoton in die Gegenrichtung**:

| Berührungen | Bounce | Ausbruch |
|---|---|---|
| 2 | −1,97 bp | +0,88 bp |
| 4 | −8,20 bp | +8,68 bp |
| **6** | **−16,30 bp** | **+18,27 bp** |
| 8 | −13,64 bp | +19,47 bp |

**Korrelation zwischen beiden Effekten: −0,674.** Derselbe Berührungszähler
treibt sie in Gegenrichtungen; ihre Summe ist praktisch null.

Die wenigen positiven Bounce-Werte stammen fast alle von Pivot-Weite 4
(50,6 % positiv, Median +1,20 bp) — Schwankungen auf Rauschniveau. Ab Weite 8
ist der Bounce klar negativ (−9 bis −20 bp). Und 2 positive Signifikanzen bei
347 Tests liegen **unter** der Zufallserwartung von 17.

## 2. Die Parametersuche hat nichts verbessert

Das ist der Teil, den man leicht schönschreiben würde. Die Randverteilung
bevorzugt Weite 12, Toleranz 0,5, Alter 2000, ≥6 Berührungen. Diese Parameter
haben den **größeren Effekt je Ereignis** — und sind als **Strategie
schlechter**:

| | Effekt je Ereignis | als Strategie (Suchzeitraum) |
|---|---|---|
| alt (8 / 0,5 / 1000) | +37,9 bp | **54,7 %** |
| neu (12 / 0,5 / 2000) | **+44,8 bp** | 31,1 % |

Weniger Ereignisse bedeuten weniger Marktzeit und weniger Gelegenheiten, die
+10 % zu erreichen. **Die Ereignis-Statistik optimiert das falsche Ziel.** Der
ursprüngliche Parametersatz bleibt.

## 3. Liquidität: drei Thesen, drei Nullergebnisse

Glassnode ist ohne Bezahlplan gesperrt (HTTP 401). Ersatz: 971 Tage
Binance-Orderbuchtiefe, zu einer Karte in absoluten Preisen verdichtet
(`src/prop_backtester/liquidity.py`). Die Karte ist brauchbar — der bloße
Abstand zum Mittelkurs erklärt nur **8,3 %** ihrer Streuung, es bleibt also
preisspezifische Struktur übrig.

| These | Ergebnis |
|---|---|
| Berührungen verbrauchen Liquidität | Korrelation **+0,021** (p = 0,36) — kein Zusammenhang |
| Dünnes Level bricht heftiger | Q4−Q1 +39,6 bp (p = 0,47), nicht monoton |
| Loch hinter dem Level lässt durchfallen | Q4−Q1 −65,6 bp (p = 0,24), nicht monoton |
| Liquidität sagt die nötige Stop-Weite | dünn 127 bp, mittel 78 bp, dick 143 bp — nicht monoton |

**Damit ist auch meine eigene Erklärung für die Bounce/Ausbruch-Asymmetrie
nicht belegt.** Ich hatte vermutet, dass jede Berührung ruhende Orders
aufbraucht und das Level ausdünnt. Die Buchtiefe an oft getesteten Levels ist
messbar **nicht** niedriger.

*Einschränkung: Gemessen wird die stehende Tiefe im 7-Tage-Fenster vor dem
Ereignis. Liquidität, die im Moment der Berührung verbraucht und danach wieder
gestellt wird, bliebe unsichtbar. Der Mechanismus ist nicht widerlegt — er ist
mit diesen Daten nicht nachweisbar.*

## 4. Stops: bessere Erwartung, keine bessere Pass-Rate

| Stop | ausgelöst | E[Rendite] je Trade | Pass-Rate (1,0×) |
|---|---|---|---|
| **kein** | — | +46,0 bp | **54,7 %** |
| 150 bp | 36 % | +55,6 bp | 38,0 % |
| 200 bp | 26 % | **+58,1 bp** | — |
| 300 bp | 15 % | +56,5 bp | 51,3 % |
| 500 bp | 7 % | +50,5 bp | 52,7 % |

Ein Stop kappt den linken Rand und **verbessert die Erwartung je Trade** um bis
zu 26 %. Für die Challenge hilft er trotzdem nicht: Er kostet Marktzeit und
Umsatz, und realisierte Verluste zählen gegen das Tagesverlustlimit. **Ohne
Stop bleibt am besten** — das bestätigt den bisherigen Aufbau.

## 5. Der Holdout

Vorab festgelegt und nicht nachjustiert: Parameter 8 / 0,5 / 1000, ≥6
Berührungen, Ausbruch, 24 h halten, kein Stop.

### Der Effekt hält — und wird stärker

| | Suchzeitraum | **Holdout** |
|---|---|---|
| Ausbruch | +37,9 bp (p = 0,053) | **+66,8 bp (p = 0,002)** |
| Bounce | −38,0 bp (p = 0,064) | **−62,5 bp (p = 0,002)** |

Beide Richtungen werden out-of-sample **deutlicher**, nicht schwächer. Nach
420 geprüften Kombinationen ist das die eigentlich belastbare Aussage dieser
Untersuchung.

### Die Pass-Rate ist auf 1,5 Jahren nicht sauber messbar

| Variante | Suchzeitraum | Holdout | offen |
|---|---|---|---|
| Ausbruch 24 h, 1,0× | 54,7 % | **31,9 %** | 16,5 % |
| Ausbruch 24 h, 0,5× | 48,6 % | 52,1 % | **47,9 %** |
| Ausbruch 48 h, 0,5× | 49,3 % | 56,5 % | **43,5 %** |
| Bounce 24 h, 1,0× | 5,9 % | **0,0 %** | 14,1 % |

Bei halber Größe dauert ein Versuch 127–211 Tage; auf 1,5 Jahren Holdout
bleiben deshalb 43–48 % der Versuche unaufgelöst. Diese Prozentwerte tragen
nicht.

Bemerkenswert bleibt: Die Variante, die ich anhand des **Suchzeitraums**
ausgewählt hatte (1,0×), fällt out-of-sample von 54,7 % auf 31,9 %. Die aus
theoretischen Gründen bevorzugte (0,5×, wegen des Tagesverlustlimits) hält.
Ein weiterer Beleg dafür, dass Optimierung auf den Suchzeitraum in die Irre
führt.

## Fazit

| Frage | Antwort |
|---|---|
| An der Unterstützung kaufen? | **Nein.** Systematisch negativ, im Holdout mit p = 0,002 bestätigt. |
| Bessere Parameter gefunden? | **Nein.** Der ursprüngliche Satz bleibt der beste. |
| Liquidität als Stop-Hilfe? | **Nein.** Drei Thesen, drei Nullergebnisse. |
| Stops einbauen? | **Nein.** Bessere Erwartung, schlechtere Pass-Rate. |
| Hält der Ausbruch? | **Ja** — out-of-sample +66,8 bp bei p = 0,002. |

Praktisch ändert sich an der Handelsregel damit **nichts**: Level mit ≥6
Berührungen, Einstieg beim Bruch, kein Stop, nach 24–48 Stunden raus, halbe
Positionsgröße. Was sich ändert, ist das Vertrauen — die Regel hat jetzt einen
echten Holdout überstanden, und die naheliegende Gegenidee ist sauber
ausgeschlossen.
