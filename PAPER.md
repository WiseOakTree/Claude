# Kein reproduzierbarer Edge

## Indikatoren, Intuition und Zufall im Kryptohandel — eine vorregistrierte Untersuchung mit 1.067 getesteten Varianten

---

**Zusammenfassung**

Wir prüfen, ob ein privater Kryptohändler mit öffentlich bekannten Regeln
einen statistisch signifikanten Vorteil gegenüber einem fairen Zufallsprozess
erzielen kann. Über 1.067 Varianten, 14 Märkte und fünfeinhalb Jahre
Stundendaten finden wir keinen. Fünfundzwanzig kanonische Handelsregeln mit
Lehrbuchparametern verlieren in 24 von 25 Fällen; über 1.121.000 Trades liegt
der Median bei **−15,18 Basispunkten je Trade** nach Kosten. Ein *Reality
Check* nach White ergibt für die beste Regel einen familienweisen p-Wert von
0,0170 — dieselbe Regel liefert jedoch **+16,92 bp in der ersten und −17,61 bp
in der zweiten Hälfte** des Zeitraums. Zehn Heuristiken, die intuitive
Chartwahrnehmung nachbilden, sind von den Regeln und vom Zufall statistisch
nicht zu trennen (Kruskal-Wallis, *p* = 0,5971). Bei 15.776 on-chain
verifizierten Händlerkonten zeigt sich ein monotoner Zusammenhang: **je höher
der Umschlag, desto schlechter das Ergebnis je gehandeltem Dollar** — von
+1.736 bp bei unter fünffachem Umschlag auf −6,72 bp bei über
tausendfachem. Wir dokumentieren neun methodische Fallen, die im Verlauf der
Untersuchung *am eigenen Material* aufgetreten sind, und argumentieren, dass
dieser Fehlerkatalog der belastbarere Beitrag ist.

**Schlagworte:** Data Snooping, Reality Check, Markteffizienz,
Kryptowährungen, Vorregistrierung, technische Analyse

---

## 1. Fragestellung

Die Literatur zur technischen Analyse leidet seit Jahrzehnten an einem
Problem: Wer genug Regeln auf genug Daten prüft, findet immer eine, die
funktioniert. Der übliche Ausweg — Signifikanzkorrektur im Nachhinein — greift
zu kurz, weil die Zahl der tatsächlich probierten Varianten selten
dokumentiert ist.

Wir stellen deshalb eine engere Frage:

> **Kann ein privater Kryptohändler mit öffentlich bekannten Regeln einen
> statistisch signifikanten Vorteil gegenüber einem fairen Zufallsprozess
> erzielen?**

Und eine zweite, die den Vergleich vervollständigt:

> **Unterscheiden sich regelbasierter Handel, intuitiver Handel und Zufall
> überhaupt im Ergebnis?**

Beide Untersuchungspläne wurden **vor der Rechnung** schriftlich festgelegt
und versioniert (`docs/finaltest_spec.md`, `docs/dreigruppen_spec.md`). Die
Commit-Reihenfolge im Versionsverlauf belegt, dass Urteilskriterien und
Parameter vor Kenntnis der Ergebnisse feststanden.

---

## 2. Daten

| Quelle | Umfang |
|---|---|
| Stundenkerzen, 14 Kryptowährungen | 2021-03 bis 2026-08, je ~46.700 Bars |
| Einzeltrades (Tickdaten) mit Aggressorkennung | **110.886.718** Trades, 72 Tage |
| Optionsimplizite Volatilität (DVOL) | 2021-03 bis 2026-08, täglich |
| Positionierungsdaten (Open Interest, 5 min) | 2024-06 bis 2026-07 |
| On-chain verifizierte Händlerkonten | **41.362** Konten |
| Frische Märkte für den Vorwärtstest | 8 nie verwendete Instrumente |
| Frischer Zeitraum | 2026-07-01 bis 2026-08-07, 14 Märkte |

Märkte: BTC, ETH, SOL, BNB, XRP, ADA, ATOM, AVAX, BCH, DOGE, DOT, LINK, LTC,
TRX.

**Transaktionskosten** durchgehend 8 Basispunkte je Seite, also **16 bp je
Roundtrip**. Das entspricht den realen Konditionen eines Privatkontos
einschließlich Slippage und Halbspread.

---

## 3. Methodik

### 3.1 Regelfamilie

Fünfundzwanzig Regeln mit **kanonischen Lehrbuchparametern**: MACD (12/26/9),
RSI (14, Schwellen 30/70), Stochastik (14/3/3), Bollinger (20/2), Keltner
(EMA 20, 2×ATR 10), Donchian (20 und 55), Goldenes Kreuz (50/200), SMA
(20/50), ATR-Ausbruch, Momentum (90), CCI (20), Williams %R (14), ADX (14),
Ichimoku (9/26), Aroon (25), MFI (14), OBV, Heikin-Ashi, VWAP sowie zwei im
Projekt selbst entwickelte Regeln.

**Es wurde kein einziger Parameter gesucht.** Jede Optimierung hätte das
Mehrfachtestproblem erneut eingeführt.

### 3.2 Der Nullprozess

Für jede Regel und jeden Markt wird die vollständige Signalreihe **zirkulär
verschoben**. Das erhält

- die Anzahl der Signale,
- die Long/Short-Quote,
- die Autokorrelations- und Clusterstruktur der Signale,
- die Kursreihe selbst mit Drift, Volatilitäts-Clustern und fetten Rändern,

und zerstört ausschließlich die zeitliche Ausrichtung zwischen Signal und
Kurs. Getestet wird damit allein, ob die Regel Information über **Zeitpunkt
und Richtung** trägt.

*Eine erste Fassung zog stattdessen unabhängige Zufallszeitpunkte. Für die
einzige zustandsbasierte Regel (mittlere Signalserie 3,1 Bars gegenüber 1,0
bei allen übrigen) erzeugte das eine zu enge Nullverteilung. Die Korrektur
änderte den p-Wert von 0,0145 auf 0,0170.*

### 3.3 Teststatistik

Wir verwenden **White's Reality Check**: Beobachtet wird das Maximum der
Kennzahl über alle Regeln; unter der Nullhypothese wird dieses Maximum in
2.000 Runden simuliert. Der familienweise p-Wert ist der Anteil der Runden,
in denen das Zufallsmaximum das beobachtete erreicht. Ergänzend berichten wir
einen Romano-Wolf-Schrittabstieg für die Einzelregeln.

Eine Nullkontrolle bestätigt die Kalibrierung: Die Streuung der
Nullverteilung beträgt 7,09 bp gegenüber einem echten Standardfehler von
6,52 bp (Verhältnis 0,92) — das Null ist eher zu breit als zu eng.

### 3.4 Effektive Stichprobengröße

Bei überlappenden Haltedauern ist die naive Stichprobengröße irreführend. Wir
verwenden die Summe der *Einzigartigkeit* jedes Trades: Ein Trade, der zu
jedem Zeitpunkt mit *k* anderen gleichzeitig offen ist, zählt 1/*k*.

Diese Korrektur ersetzt eine frühere Fassung (n_eff = n ÷ Haltedauer), die um
**Faktor 5,48 zu streng** war und in einer Simulation einen eingebauten
Vorteil von 200 bp je Trade in **null Prozent** der Fälle als signifikant
erkannte (Abschnitt 5.2).

---

## 4. Ergebnisse

### 4.1 Fünfundzwanzig Regeln, 1.121.000 Trades

**24 von 25 Regeln verlieren.**

| Regel | Trades | bp je Trade |
|---|---|---|
| Keltner-Ausbruch | 71.082 | **+6,08** |
| Goldenes Kreuz 50/200 | 4.158 | −3,12 |
| ATR-Ausbruch | 27.533 | −3,88 |
| Donchian 55 | 24.712 | −4,41 |
| Donchian 20 | 46.518 | −7,97 |
| S/R-Ausbruch (Projektregel) | 16.656 | −9,84 |
| Gegen-Bounce (Projektregel) | 14.712 | −10,76 |
| MACD 12/26/9 | 51.280 | −13,14 |
| VWAP-Kreuzung | 139.404 | −14,92 |
| Bollinger-Rückkehr | 38.212 | −20,39 |
| Stochastik 14/3/3 | 36.393 | −28,42 |
| MFI 14 | 17.109 | −32,34 |
| **RSI 14 (30/70)** | 18.746 | **−32,40** |

Bemerkenswert ist die Spalte der unkorrigierten Einzel-p-Werte: MACD
(*p* = 0,0045) und VWAP (*p* = 0,0060) sind einzeln **signifikant schlechter
als Zufall**.

### 4.2 Reality Check

| | |
|---|---|
| beobachtetes Maximum | +6,08 bp (Keltner) |
| Zufallsmaximum, Median | −7,06 bp |
| Zufallsmaximum, 95. Perzentil | +2,29 bp |
| **familienweiser p-Wert** | **0,0170** |

Nach dem vorregistrierten Kriterium (*p* < 0,05) wäre die Antwort **ja**.

### 4.3 Und der Gewinner hält nicht

| Zeitraum | Trades | Effekt | *t* |
|---|---|---|---|
| gesamt | 71.082 | +6,08 bp | 0,93 |
| **erste Hälfte 2021-24** | 48.770 | **+16,92 bp** | 2,01 |
| **zweite Hälfte 2025-26** | 22.312 | **−17,61 bp** | −1,88 |

Zusätzlich: positiv in **5 von 14 Märkten**, getragen von zwei (DOGE +96,5 bp,
SOL +71,3 bp); über 18 Nachbarparameter reicht die Spanne von −6,65 bis
+17,85 bp, acht davon negativ.

Der Effekt ist weder über die Zeit noch über die Märkte noch über die
Parameter stabil.

### 4.4 Indikator, Intuition und Zufall

Zehn Heuristiken bilden intuitive Wahrnehmung nach („sieht bullish aus",
„ist überverkauft", „fühlt sich nach Breakout an", „runde Zahl",
„große Kerze" …), ohne Schwellen aus der Literatur.

| Gruppe | *n* | Median | 25 % | 75 % |
|---|---|---|---|---|
| Indikatorregeln | 24 | **−15,18** | −18,88 | −10,53 |
| Intuitionsheuristiken | 10 | **−2,70** | −28,35 | +15,55 |
| Zufall | 60 | **−15,30** | −19,46 | −8,23 |

| Test | Ergebnis |
|---|---|
| Kruskal-Wallis über drei Gruppen | *H* = 1,031, ***p* = 0,5971** |
| Indikator gegen Intuition (Holm) | *p* = 0,7488 |
| Indikator gegen Zufall (Holm) | *p* = 0,7476 |
| Intuition gegen Zufall (Holm) | *p* = 1,0000 |

**Die drei Gruppen sind nicht unterscheidbar.**

### 4.5 Echte Händler: der Umschlag-Gradient

15.776 on-chain verifizierte Konten mit über 1 Mio $ Handelsvolumen,
gemessen als PnL je gehandeltem Volumen:

| Umschlag (Volumen ÷ Kontowert) | *n* | Median | Anteil > 0 |
|---|---|---|---|
| unter 5× | 692 | **+1.736,14 bp** | 80,6 % |
| 5–25× | 1.928 | +323,83 | 75,0 % |
| 25–100× | 2.088 | +114,55 | 74,7 % |
| 100–1.000× | 4.557 | +13,32 | 61,7 % |
| **über 1.000×** | 6.511 | **−6,72 bp** | **36,1 %** |

Der Zusammenhang ist **monoton über fünf Größenklassen**. Die günstigsten
Werte erzielen Konten, die kaum gehandelt haben — bei ihnen misst die Kennzahl
den Kursanstieg, nicht die Handelsleistung.

Ergänzend: „In zwei aufeinanderfolgenden, disjunkten Perioden profitabel"
tritt bei 26,1 % der Konten auf; unter Unabhängigkeit wären **26,3 %** zu
erwarten. Persistenz zeigt sich nur in den Rändern (oberstes Dezil zweimal:
1,88 % gegenüber 1,00 % Zufallserwartung).

### 4.6 Liquiditätsbereitstellung

An 7.812.435 Einzeltrades gemessen, erzielt die passive Gegenseite jedes
Trades **−0,575 bp** (20 von 20 Tag-Horizont-Zellen negativ). Erst ein Rabatt
von −1,0 bp dreht das Vorzeichen (+0,425 bp). Entgegen der Erwartung sind
**kleine Trades die ungünstigsten Gegenparteien** (−0,715 bp) und große die
günstigsten (−0,246 bp).

---

## 5. Was nicht hält — und was das Projekt gelernt hat

### 5.1 Streichliste

Folgende zwischenzeitlich berichtete Befunde halten der Prüfung nicht stand:

| Befund | Grund |
|---|---|
| S/R-Ausbruch (+50,5 bp, *t* = 2,16) | Vorwärtstest: 2 von 8 frischen Märkten, gepoolt −36,9 bp |
| Gegen-Bounce (+78 bp, *t* = 3,28) | Vorwärtstest gescheitert; −10,76 bp im Regelvergleich |
| neun Signalfilter | sämtlich out-of-sample gescheitert |
| Value-Area-Ausbruch (SOL) | 4 von 14 Märkten; Zufallserwartung 3,5 (*p* = 0,479) |
| sämtliche Pass-Raten | aus derselben Historie, auf der die Regeln entstanden |

Erhalten bleibt mit ausdrücklicher Einschränkung die **Volatilitätsrisiko-
prämie** (BTC *t* = 4,12; S&P 500 *t* = 4,67; über der projektweiten
Bonferroni-Schwelle von 4,07) — allerdings **ohne jeden Holdout**. Sie rettet
sich allein dadurch, dass sie eine vorbestehende, publizierte Hypothese ist
und kein gesuchtes Muster.

### 5.2 Neun methodische Fallen, alle am eigenen Material

Wir halten diesen Katalog für den belastbareren Beitrag als jedes
Einzelergebnis.

| # | Falle | gemessener Effekt |
|---|---|---|
| 1 | Look-ahead im Ausführungspreis | Pass-Rate **93 % → 7 %** |
| 2 | Überlappung nicht korrigiert | *p* = 10⁻²⁴⁰ → *p* = 0,27 |
| 3 | Überlappungskorrektur **zu streng** | Faktor 5,48; erkennt 200 bp Vorteil in **0 %** der Fälle |
| 4 | Bestes von N | 54,7 % → 31,9 % out-of-sample |
| 5 | Transaktionskosten doppelt gezählt | 16 bp → faktisch 32 bp |
| 6 | Zeitraummittel als Gegenwartsaussage | Vault +37,3 % p.a. gegenüber aktuell +0,3 % |
| 7 | Holdout mehrfach verwendet | über zwanzigmal derselbe Zeitraum |
| 8 | Nullmodell zu eng | Clusterstruktur nicht abgebildet |
| 9 | Look-ahead durch Zeitreihen-Reindexierung | Heuristik +176 → **+37 bp**; zweite kippt +116 → **−35 bp** |

Fall 3 verdient Hervorhebung: Eine *zu konservative* Korrektur ist ebenso
fehlerhaft wie eine zu liberale und in der Literatur seltener diskutiert. Wir
haben sie nur gefunden, weil wir die Auswertung gegen einen **eingebauten,
bekannten Vorteil** geeicht haben — ein Test, der vor jeder Anwendung stehen
sollte.

---

## 6. Einschränkungen

1. **Überlebensauswahl ist ungelöst.** Alle 14 Märkte existieren 2026 noch.
   Ausgefallene Projekte fehlen vollständig; sämtliche Renditeaussagen sind
   dadurch nach oben verzerrt, um einen nicht bezifferbaren Betrag. Dasselbe
   gilt für die Kontendaten (geschlossene Nullkonten fehlen).
2. **Finanzierungskosten fehlen** in nahezu allen Tests. Bei 48 Stunden
   Haltedauer entspricht das etwa 3,9 bp je Long-Trade.
3. **Die Intuitionsgruppe umfasst nur zehn Mitglieder.** Die Trennschärfe
   gegen sie ist gering; „nicht unterscheidbar" schließt einen mittelgroßen
   Unterschied nicht aus.
4. **Heuristiken sind keine Menschen.** Sie bilden Wahrnehmung nach, ersetzen
   aber keine Verhaltensstudie.
5. **Eine Anlageklasse, ein Zeitraum.** Fünfeinhalb Jahre Kryptomarkt
   enthalten zwei Zyklen. Verallgemeinerungen auf andere Märkte sind nicht
   gedeckt.
6. **Unterschiedliche Kostenbasis** zwischen den Kontendaten und den
   simulierten Gruppen.
7. **Die Literaturangaben** wurden aus dem Gedächtnis zitiert und nicht gegen
   die Originale geprüft.

---

## 7. Schlussfolgerung

Über 1.067 getestete Varianten, 14 Märkte, 1.121.000 simulierte Trades und
110,9 Millionen echte Einzeltrades hinweg:

> **Nein. Nach Kosten, Out-of-Sample-Prüfung und sauberer Statistik bleibt
> kein reproduzierbarer Vorteil.**

Bemerkenswert ist die Form des Scheiterns. Es liegt nicht daran, dass die
Märkte kein Gedächtnis hätten — eine Markov-Analyse weist Zustandsabhängigkeit
mit *p* ≈ 0 nach und bestätigt sie in 15 von 16 Fällen out-of-sample. Der
Bruttovorteil beträgt dabei **unter einem Basispunkt**, gegen eine
Kostenschwelle von sechzehn.

**Das Problem ist nicht, dass Märkte zufällig wären. Sie sind *fast* zufällig
— und die Transaktionskosten liegen genau in der verbleibenden Lücke.**

Der einzige über alle Untersuchungen hinweg konsistente Zusammenhang ist
zugleich der unspektakulärste: **Wer weniger handelt, verliert weniger.** Er
zeigt sich im Umschlag-Gradienten echter Konten, in der Kostenrechnung der
Regelfamilie und in der Differenz zwischen aktiver und passiver Ausführung.

---

## Literatur

*Aus dem Gedächtnis zitiert und nicht gegen die Originale geprüft — bitte vor
Weiterverwendung verifizieren.*

- White, H. (2000). A Reality Check for Data Snooping. *Econometrica*.
- Sullivan, R., Timmermann, A., White, H. (1999). Data-Snooping, Technical
  Trading Rule Performance, and the Bootstrap. *Journal of Finance*.
- Romano, J., Wolf, M. (2005). Stepwise Multiple Testing as Formalized Data
  Snooping. *Econometrica*.
- Politis, D., Romano, J. (1994). The Stationary Bootstrap. *JASA*.
- Bailey, D., López de Prado, M. (2014). The Deflated Sharpe Ratio.
  *Journal of Portfolio Management*.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*
  (Konzept der Einzigartigkeit überlappender Beobachtungen).
- Barber, B., Odean, T. (2000). Trading Is Hazardous to Your Wealth.
  *Journal of Finance*.
- Carr, P., Wu, L. (2009). Variance Risk Premiums. *Review of Financial
  Studies*.
- Engle, R. (1982). Autoregressive Conditional Heteroscedasticity.
  *Econometrica*.

---

## Verfügbarkeit

Sämtliche Daten, Skripte und Zwischenergebnisse liegen im Repository. Die
Vorregistrierungen (`docs/finaltest_spec.md`, `docs/dreigruppen_spec.md`,
`docs/vorwaertstest_spec.md`) sind vor den jeweiligen Ergebnissen committet;
die Reihenfolge ist im Versionsverlauf nachprüfbar.

Zentrale Skripte: `research/finaltest.py`, `research/finaltest2.py`,
`research/dreigruppen.py`, `research/dreigruppen2.py`,
`research/vorwaerts.py`, `research/power2.py`, `research/mm2.py`,
`research/hl_kern.py`, `research/audit_methodik.py`.

Vollständige Ergebnisliste: `docs/ergebnisse.txt` (63 Untersuchungen).
