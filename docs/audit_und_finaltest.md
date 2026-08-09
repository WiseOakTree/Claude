# Audit und finaler Test

Vollständige methodische Prüfung des Projekts und der abschließende Test zur
Kernfrage. Geprüft wurde der **Code**, nicht meine eigenen Zusammenfassungen.

---

# 1. Was tatsächlich getestet wurde

| | |
|---|---|
| Forschungsskripte | **167** |
| Dokumente | 62 |
| nummerierte Untersuchungen | 61 |
| **tatsächlich getestete Varianten (bezifferbar)** | **~1.067** |
| Softwaretests | 109, alle grün |

Die 61 „Untersuchungen" sind **nicht** 61 Tests. Dahinter stecken:

| Quelle | Varianten |
|---|---|
| 120 TA-Kombinationen (Ursprungssuche) | 120 |
| Signifikanztests im Mehrfachtest-Kapitel | 347 |
| MACD+Stochastik+Bollinger-Gitter | 324 |
| Risikoprädiktoren × Ziele × Märkte | 84 |
| Footprint-Merkmale × Horizonte | 56 |
| Liquidationsmerkmale × Horizonte | 32 |
| Value-Area-Ausbruch, 14 Märkte × 2 Zeiträume | 28 |
| Markov, Volume Profile, VWAP, Filter, Rainbow | 76 |
| **Summe** | **1.067** |

**Das ist die relevante Zahl für Mehrfachtests.** Die Bonferroni-Schwelle
daraus: **t > 4,07** (p < 4,7·10⁻⁵).

---

# 2. Methodische Sauberkeit — der Ist-Zustand

Automatisiert über alle 167 Skripte (`research/audit_methodik.py`):

| Kriterium | Anteil der Skripte |
|---|---|
| Kosten | 51,5 % |
| Look-ahead-Kontrolle (`shift(1)`, `mode="close"`) | 40,1 % |
| **Holdout / Train-Test-Split** | **30,5 %** |
| Zufallskontrolle | 23,4 % |
| Überlappungskorrektur | 21,6 % |
| **mehrere Märkte** | **13,8 %** |
| **Funding** | **4,2 %** |
| **Bonferroni / FDR** | **4,2 %** |
| **Slippage explizit** | **3,0 %** |

*(Der Nenner ist verzerrt: Viele Skripte sind reine Rechenhilfen ohne
Testcharakter. Slippage bei 3 % und Funding bei 4 % sind trotzdem echte
Lücken.)*

### Kriterium für Kriterium

| Kriterium | Stand |
|---|---|
| **Train/Test-Split** | ✅ bei den Hauptbefunden (2021-24 / 2025-26), ❌ bei der Volatilitätsprämie |
| **echter Holdout** | ⚠️ **mehrfach benutzt** — der BTC-Holdout wurde über zwanzigmal angefasst und ist als Holdout verbraucht |
| **keine Datenüberschneidung** | ✅ Zeiträume disjunkt, ✅ Überlappungskorrektur nach dem Fehlerfund korrigiert |
| **Look-ahead** | ✅ systematisch kontrolliert, **zweimal selbst gefunden** (Footprint-z-Scores, Rainbow-Fit) |
| **Survivorship Bias** | ❌ **ungelöst** — alle 14 Märkte sind Überlebende, tote Coins fehlen vollständig |
| **Multiple Testing** | ⚠️ erst spät ernst genommen; nur 4,2 % der Skripte korrigieren |
| **Transaction Costs** | ✅ 16 bp je Roundtrip durchgehend, nach dem Doppelzählungsfehler korrigiert |
| **Slippage** | ⚠️ nur im Engine-Pfad, nicht in den späteren Ad-hoc-Skripten |
| **Funding** | ❌ **fehlt in fast allen Tests** — bei 48-h-Halten sind das ~0,5 bp je Trade |
| **Regime Changes** | ❌ **die größte Lücke** — siehe finaler Test |

---

# 3. Die methodischen Lücken

### 🛑 3.1 Der Holdout ist verbraucht

Der BTC-Zeitraum 2025-01 bis 2026-06 wurde in über zwanzig Untersuchungen als
„Holdout" benutzt. **Nach dem ersten Zugriff war er keiner mehr.** Jede
weitere Verwendung ist faktisch Suchzeitraum.

Das ist der Grund, warum der Vorwärtstest auf **frischen Märkten und frischem
Zeitraum** nötig war — und warum er beide Projektregeln gekippt hat.

### 🛑 3.2 Survivorship Bias ist ungelöst

Alle Daten stammen von Coins, die es 2026 noch gibt. Wer 2021 in LUNA, FTT
oder eines der hunderten toten Projekte investiert war, taucht in keiner
Zeile auf. **Jede Renditeaussage dieses Projekts ist nach oben verzerrt**, und
zwar um einen Betrag, den ich nicht beziffern kann.

Dasselbe gilt für den HLP-Vault (eine überlebende Börse) und für die
Hyperliquid-Konten (geschlossene Nullkonten fehlen).

### 🛑 3.3 Funding fehlt

Bei 48 Stunden Haltedauer fallen sechs Funding-Zahlungen an. Bei einer
mittleren Rate von 0,0064 % sind das **~3,9 bp je Trade** für Long-Positionen
— und die stecken in fast keinem Test. Bei Effektgrößen von 5 bis 50 bp ist
das relevant.

### 🛑 3.4 Multiple Testing wurde zu spät ernst genommen

Bei ~1.067 Varianten liegt die Schwelle bei t > 4,07. Danach:

| Befund | t | überlebt? |
|---|---|---|
| Volatilitätsprämie | 4,19 | **ja** — aber ohne Holdout |
| Orderflow | p = 3·10⁻¹⁷³ | ja — aber 0,29 bp gegen 16 bp Kosten |
| Markov | p ≈ 0 | ja — aber Bruttovorteil unter 1 bp |
| S/R-Ausbruch | 2,16 | nein |
| Gegen-Bounce | 2,82 | nein |
| Marktphasen-Filter | 2,07 | nein |

---

# 4. Streichliste

## 🛑 Aus der wissenschaftlichen Betrachtung zu streichen

| Befund | Grund |
|---|---|
| **S/R-Ausbruch (+50,5 bp, t 2,16)** | Vorwärtstest: 2 von 8 frischen Märkten, gepoolt **−36,9 bp**; im 25-Regel-Test **−9,84 bp** |
| **Gegen-Bounce (+78 bp, t 3,28)** | Vorwärtstest gescheitert; im 25-Regel-Test **−10,76 bp** |
| **Marktphasen-Filter** | verfehlt Bonferroni deutlich, nie vorwärts getestet |
| **SOL-Value-Area-Ausbruch** | 4 von 14 Märkten — bei Zufall erwartet 3,5 (p = 0,479) |
| **alle 9 früheren Filter** | out-of-sample gescheitert |
| **Pass-Raten (78,1 %, 63,8 % usw.)** | stammen aus derselben Historie, auf der die Regeln gebaut wurden |
| **HLP-Vault +37,3 % p.a.** | Dreijahresmittel; aktueller Lauf **+0,3 %**. Als Erwartungswert unbrauchbar |

## ⚠️ Mit Einschränkung zu behalten

| Befund | was daran hält, was nicht |
|---|---|
| **Volatilitätsprämie** (BTC t 4,12 / S&P t 4,67) | **hält**: zwei Anlageklassen, Kosten enthalten, übersteht Bonferroni. **Hält nicht**: kein Holdout, keine Out-of-Sample-Prüfung. Rettet sich nur dadurch, dass sie eine **vorbestehende, publizierte Hypothese** ist und kein gesuchtes Muster |
| **Orderflow-IC −0,041** | statistisch unbestreitbar, **wirtschaftlich wertlos** (0,29 bp gegen 16 bp) |
| **Markov-Gedächtnis** | dito — p ≈ 0, Bruttovorteil unter 1 bp |
| **Maker verliert −0,575 bp** | 7,8 Mio Trades, 20/20 Zellen negativ. Misst den **Durchschnitts**-Maker, keine Warteschlange |
| **Taker-Anteil 38 % gegen 66 %** | p = 0,057, einer von fünf Vergleichen, n = 58. **Nicht signifikant**, aber der einzige Kandidat |
| **Rauschdecken-Rechnungen** | reine Simulation, keine Datenabhängigkeit — belastbar |

## ✅ Uneingeschränkt belastbar

Nur die **negativen** Befunde und die Simulationen:

- 24 von 25 Lehrbuchregeln verlieren über 1,1 Mio Trades
- Look-ahead: 93 % → 7 % Pass-Rate
- Überlappung: p = 10⁻²⁴⁰ → p = 0,27
- Bestes von N: 54,7 % → 31,9 % out-of-sample
- Rauschdecke: 1.000 Varianten → Sharpe 1,8 ohne Edge
- Trader-Rauschdecke: 858 von 100.000 mit fünf Gewinnjahren ohne Können
- „Zweimal profitabel" auf Hyperliquid: 26,1 % gegen 26,3 % bei Zufall

---

# 5. Der finale Test

> **Kann ein privater Krypto-Trader mit öffentlich bekannten Regeln einen
> statistisch signifikanten Edge gegenüber einem fairen Zufallsprozess
> erzielen?**

Aufbau vorab festgelegt und committet
([`finaltest_spec.md`](finaltest_spec.md)): **25 kanonische Regeln mit
Lehrbuchparametern, keine Optimierung**, 14 Märkte, 1 h, 48 h Halten, 16 bp
Kosten, **White's Reality Check** mit 2.000 Runden.

## Das beobachtete Bild

**24 von 25 Regeln verlieren**, über 1.121.000 Trades:

| Regel | Trades | bp je Trade |
|---|---|---|
| **Keltner-Ausbruch** | 71.082 | **+6,08** |
| Goldenes Kreuz 50/200 | 4.158 | −3,12 |
| ATR-Ausbruch | 27.533 | −3,88 |
| **S/R-Ausbruch (Projekt)** | 16.656 | **−9,84** |
| **Gegen-Bounce (Projekt)** | 14.712 | **−10,76** |
| MACD 12/26/9 | 51.280 | −13,14 |
| Stochastik 14/3/3 | 36.393 | −28,42 |
| **RSI 14 (30/70)** | 18.746 | **−32,40** |

## Der Reality Check

Nullmodell: **zirkuläre Verschiebung** der ganzen Signalreihe — erhält Anzahl,
Long/Short-Quote und Clusterstruktur exakt, zerstört nur die Ausrichtung zum
Kurs.

*(Ein erstes Null mit unabhängigen Zufallszeitpunkten war zu eng für die
einzige Zustandsregel; korrigiert, das Ergebnis änderte sich kaum.)*

| | |
|---|---|
| beobachtetes Maximum | **+6,08 bp** (Keltner) |
| Zufalls-Maximum, Median | −7,06 bp |
| Zufalls-Maximum, 95. Perzentil | +2,29 bp |
| **familienweiser p-Wert** | **0,0170** |

Nach dem vorab festgelegten Kriterium: **p < 0,05 → Ja.**

Nullkontrolle bestanden: Null-Streuung 7,09 bp gegen echten Standardfehler
6,52 bp — Verhältnis 0,92×, das Null ist eher zu breit als zu eng.

## 🛑 Und dann die nachgelagerte Diagnostik

| Zeitraum | Trades | Effekt | t |
|---|---|---|---|
| gesamt | 71.082 | +6,08 bp | 0,93 |
| **Suche 2021-24** | 48.770 | **+16,92 bp** | **2,01** |
| **Holdout 2025-26** | 22.312 | **−17,61 bp** | **−1,88** |

**Das Vorzeichen kippt, und der Holdout ist signifikant negativ.**

Dazu:

| | |
|---|---|
| positiv in | **5 von 14 Märkten** |
| getragen von | DOGE (+96,5 bp) und SOL (+71,3 bp) |
| Parameterempfindlichkeit | 18 Nachbarkombinationen: **−6,65 bis +17,85 bp**, 8 davon negativ |

Der Effekt ist weder über die Zeit noch über die Märkte noch über die
Parameter stabil.

---

# Das Urteil

Die Spezifikation verlangt, dass ich das vorregistrierte Ergebnis stehen
lasse. Also steht es:

> **Familienweiser p-Wert = 0,0170. Über den Gesamtzeitraum 2021–2026 hat die
> beste von 25 öffentlich bekannten Regeln einen fairen Zufallsprozess
> geschlagen.**

Und ebenso steht, was danach kommt:

> **Dieselbe Regel liefert +16,92 bp in der ersten Hälfte und −17,61 bp in der
> zweiten. Sie funktioniert in 5 von 14 Märkten. Sie überlebt keine
> Parameteränderung.**

**Damit lautet die Antwort auf deine Frage:**

> **Nein. Nach Kosten, Out-of-Sample und sauberer Statistik bleibt kein
> reproduzierbarer Edge.**

Der Unterschied zwischen „statistisch signifikant über einen Zeitraum" und
„reproduzierbar" ist genau das, was dieser Test sichtbar macht — und es ist
das letzte der zehn Kriterien deiner Liste: **Regime Changes.** Ein
familienweiser p-Wert über einen festen Zeitraum fängt sie nicht. Nur die
Teilung tut es.

---

## Was das Projekt tatsächlich hervorgebracht hat

Nicht eine Strategie, sondern eine **Fehlerliste** — jeder Punkt an eigenen
Befunden vorgeführt:

| Falle | wo sie zugeschlagen hat |
|---|---|
| Look-ahead | Footprint-z-Scores (IC 0,22 → −0,002), Rainbow (48 → 1,1 Pp) |
| Überlappung zu naiv | p = 10⁻²⁴⁰ → 0,27 |
| Überlappung zu streng | eigener Faktor 5,48; erkannte 200 bp Edge in 0 % der Fälle |
| Bestes von N | SOL, Keltner, der ganze 324er-Gitterlauf |
| Kosten doppelt gezählt | 16 bp → faktisch 32 bp |
| Zeitraummittel als Gegenwart | HLP +37,3 % gegen aktuell +0,3 % |
| Holdout mehrfach benutzt | über zwanzigmal |
| Nullmodell zu eng | erste Fassung des finalen Tests |

**Acht Fallen, alle im eigenen Material.** Das ist das belastbare Ergebnis von
1.067 Tests — und es ist mehr wert als der Indikator, den keiner davon
gefunden hat.

---

*Skripte: `research/audit_methodik.py`, `research/finaltest.py`,
`research/finaltest2.py` (korrigiertes Null), `research/null_pruefung.py`
(Nullkontrolle), `research/keltner_diag.py` (nachgelagerte Diagnostik).
Spezifikation: [`finaltest_spec.md`](finaltest_spec.md), committet vor der
Rechnung.*
