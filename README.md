# Krypto Prop Backtester — Renko-Reversal für die Kraken-Prop-Challenge

> ## 🛑 WICHTIG: Ergebnisse zurueckgezogen
>
> Der Backtest enthielt einen **Look-ahead-Bias** (Signal-Entscheidung per
> Kerzenschluss, Fill zum frueheren Brick-Level). Look-ahead-frei gemessen hat
> die Strategie **keinen Edge**: 7 % Pass-Rate bei Fill zum Schlusskurs, 0 % mit
> ruhenden Stop-Orders (55,5 % Fehlausloesungen durch Dochte).
> **Nicht live handeln.** Details und Zahlen: [`docs/realism.md`](docs/realism.md).
>
> Die Engine ist inzwischen **strukturell gegen Look-ahead abgesichert**
> (`ExecutionConfig`, Fill wird von der Engine aus den Bar-Daten abgeleitet).
> Eine anschliessende saubere Suche ueber **120 Kombinationen** aus 5
> Strategiefamilien und 3 Timeframes fand **keine** tragfaehige Strategie
> (beste Pass-Rate 20 %, Median-Rendite ueber alle Kombis: 0,00 %) —
> siehe [`docs/strategy_search.md`](docs/strategy_search.md).
>
> Auch **alternative Daten** wurden geprueft ([`docs/altdata_test.md`](docs/altdata_test.md)):
> Orderbuch scheitert rechnerisch an der Kostenschwelle (Signal 1-5 bp vs.
> 16 bp Kosten); der Coinbase-Premium als ETF-Fluss-Stellvertreter zeigt zwar
> ein messbares Signal (IC +0,10 auf 5 Tage), ist aber out-of-sample instabil
> und liegt um **Faktor 13** unter dem noetigen Verhaeltnis Rendite/Drawdown.

---

## 🛑 Korrektur der Regelauslegung (betrifft alle Pass-Raten unten)

Die Auswertung war zu streng: Sie verlangte, dass das Gewinnziel am **Ende**
des 90-Tage-Fensters erreicht ist. Tatsaechlich ist eine Challenge bestanden,
**sobald** das Ziel beruehrt wird. Zusaetzlich misst Kraken den Drawdown
**statisch** vom Startguthaben, nicht vom laufenden Hoch.

| Strategie | bisher berichtet | korrekt |
|---|---|---|
| BTC einfach halten | 0,0 % | **24,9 %** |
| Vol-Targeting 15 % | 16,3 % | **24,8 %** |
| S/R-Ausbruch | 17,0 % | **33,9 %** |

Die *Rangfolge* der Ansaetze bleibt, die absoluten Zahlen in den aelteren
Dokumenten sind zu pessimistisch. Details: [`prop_rules.md`](docs/prop_rules.md).

**Zweite Korrektur:** Die 90-Tage-Fenster waren ebenfalls eine Modellannahme —
**Kraken Prop hat keine begrenzte Laufzeit.** Ohne Frist ist die richtige Frage
ein Erstpassage-Problem, und ueber **95 % aller Fehlschlaege kommen vom
3-%-Tagesverlustlimit, nicht vom Drawdown**. Daraus folgt: kleiner handeln,
laenger brauchen. Bestes belastbares Ergebnis: **~40-50 %** mit halber
Positionsgroesse. Details: [`no_time_limit.md`](docs/no_time_limit.md).

---

## Die Untersuchung im Ueberblick

Zehn Ansaetze, jeder mit echten Daten und Out-of-Sample-Kontrolle geprueft.

| # | Ansatz | Ergebnis | Dokument |
|---|---|---|---|
| 1 | Renko-Reversal (Ausgangspunkt) | Look-ahead-Bias; korrigiert **7 %** Pass | [`realism.md`](docs/realism.md) |
| 2 | 120 TA-Kombinationen, 3 Timeframes | Median-Rendite **0,00 %** | [`strategy_search.md`](docs/strategy_search.md) |
| 3 | Orderbuch, ETF-Fluesse, Liquidationen, Tech-Kopplung | Faktor **13** zu schwach | [`altdata_test.md`](docs/altdata_test.md) |
| 4 | Vol-Targeting & Smart DCA | **20–25 %** Pass — bestes Ergebnis | [`volatility_targeting.md`](docs/volatility_targeting.md) |
| 5 | Volatilitaets-Risikopraemie (Optionen) | **echter Edge, Sharpe 1,33** — bei Kraken nicht handelbar | [`volatility_premium.md`](docs/volatility_premium.md) |
| 6 | Orderflow & Orderbuchtiefe (9,2 Mio. Snapshots) | real, aber **0,31×** der Kostenschwelle | [`orderflow_test.md`](docs/orderflow_test.md) |
| 7 | On-Chain: MVRV, Puell, Hash Ribbons, NVT | MVRV wirkt **umgekehrt**; Pass **0,1–0,5 %** | [`onchain_test.md`](docs/onchain_test.md) |
| 8 | Kombination aller Signale | Signale unkorreliert (ρ = 0,11), Kombi trotzdem **schlechter** | [`ensemble_test.md`](docs/ensemble_test.md) |
| 9 | Welcher Edge waere noetig? | Sharpe **2,91** fuer 50 % Erfolgsquote | [`required_edge.md`](docs/required_edge.md) |
| 10 | Obergrenze fuer Machine Learning | Vol-Prognose: **kein** Nutzen moeglich; Richtung: 60 % Treffer noetig fuer Gleichstand | [`ml_ceiling.md`](docs/ml_ceiling.md) |
| 11 | Order Blocks (Smart Money) | Reaktion **nicht** OB-spezifisch — Zufallskerze gleich gut | [`altdata_test.md`](docs/altdata_test.md) |
| 12 | **S/R-Ausbruch nach Beruehrungszahl** | **erster Chartmuster-Befund, der standhaelt** — alle vier Kontrollen bestanden | [`sr_breakout.md`](docs/sr_breakout.md) |
| 13 | Welches Regelwerk passt? | Tagesverlust-Limit ist der groesste Hebel, Drawdown-Limit **wirkungslos** | [`prop_rules.md`](docs/prop_rules.md) |
| 14 | **Ohne Zeitlimit gerechnet** | **95 % der Fehlschlaege kommen vom Tageslimit** — halbe Groesse gibt ~40-50 % | [`no_time_limit.md`](docs/no_time_limit.md) |
| 15 | **S/R-Bounce, Parametersuche, Liquiditaet** | Bounce **widerlegt** (Holdout p=0,002); Ausbruch **out-of-sample bestaetigt** (+66,8 bp) | [`sr_bounce.md`](docs/sr_bounce.md) |
| 16 | **XGBoost als Signalfilter** | in-sample +1,1 SD ueber Zufall, out-of-sample **zerfaellt** (-21 bis +39 bp) | [`xgboost_filter.md`](docs/xgboost_filter.md) |
| 17 | Timeframe-Vergleich (1h/2h/4h/8h) | **1h bleibt** — 4h/8h brechen im Holdout ein oder sind auf ETH am schlechtesten | [`sr_bounce.md`](docs/sr_bounce.md) |
| 18 | **Heikin Ashi + zwei frische Assets** | HA bringt nichts; **Abrechnungsfalle** kippt auf allen 4 Assets das Vorzeichen. **S/R-Ausbruch traegt nur auf BTC/ETH, nicht auf SOL/XRP** | [`heikin_ashi.md`](docs/heikin_ashi.md) |
| 19 | Tageszeit / Sessions | Bewegung liegt in der **US-Session** (+14 %), nicht in Asien (-7 %); US einzige Session mit 4/4 positivem Effekt, als Filter aber nur suggestiv | [`sessions.md`](docs/sessions.md) |
| 20 | **Cross-Sectional Relative Strength (14 Coins)** | echtes Brutto-Alpha (+82 % p.a.), von Reibung gefressen; Holdout **-20,3 %**; Rendite/DD 0,67 statt 1,67 | [`cross_sectional.md`](docs/cross_sectional.md) |
| 21 | **Open-Interest-Squeeze** | Vorgeschlagene Kombination feuert **0-mal in 3,2 Jahren**; OI allein auf BTC +111 bp, aber **0 von 24 Zellen** im Holdout | [`oi_squeeze.md`](docs/oi_squeeze.md) |
| 22 | **Wochenend-Saisonalitaet als Filter** | Praemisse **bestaetigt** (Volumen 0,60-0,69x); im Suchzeitraum +6,9 pp ueber Zufallsfilter (Perzentil 77 %), im **Holdout Muenzwurf** (Perzentil 53 %) — **achter** gescheiterter Filter | [`weekend.md`](docs/weekend.md) |
| 23 | **Die Spielregeln aendern statt die Strategie** | **Mehrfachantritt ist der groesste Hebel ueberhaupt**: 50,9 % → 63,0 % (2 Versuche) → 78,7 % (3) fuer ~132 $ Gesamteinsatz. Aber Fehlschlaege clustern: P(2. besteht \| 1. fiel) = 35,9 % statt 60,1 % | [`spielregeln.md`](docs/spielregeln.md) |
| 24 | **Reiner Zufall und die Regelwerk-Formel** | **P(bestehen) = DD/(DD+Ziel)** — Kraken 37,5 %, gemessen 36,7 % **ohne jedes Koennen**. Zufall *gehandelt*: 13,9 %. BTC halten 0,25x: Suchzeitraum 60,6 %, Holdout **9,5 %** (reine Richtungswette). Gesamtertrag des Projekts: **~12 pp ueber einem korrekt dimensionierten Muenzwurf** | [`zufall.md`](docs/zufall.md) |
| 25 | **So einfach wie moeglich** | **Selektivitaet toetet**: >=10 Beruehrungen statt >=6 → **0,0 %** (1 % Zeit im Markt = 3 % Vol). Mit Hebel repariert: 25 pp UNTER Zufall. **Eine Position statt gestapelt: gleiche Pass-Rate mit einem Viertel der Trades** | [`einfach.md`](docs/einfach.md) |
| 26 | **Die vier Grundfragen** | Rauf/runter: **50,4 %** (Holdout 50,0 %). Uhrzeit: nach Bonferroni **keine** Stunde signifikant, groesster Unterschied 5 bp gegen 16 bp Kosten. Risiko: bei 0,35x war der schlechteste Tag **-5,16 %** — es gibt keine sichere Groesse. Grund fuer Verluste: **sieben Merkmale geprueft, keines signifikant** | [`grundfragen.md`](docs/grundfragen.md) |
| 27 | **Was die Bots finden — und was es kostet** | Bester messbarer Bot-Edge: Orderbuch-Imbalance **+0,87 bp je Trade** ueber 110.786 Trades. Break-even bei 0,87 bp Kosten — du zahlst **16 bp (18x zu viel)**. Aber: brutto p.a. **19,1 % gegen deine 18,3 %** — der Bot verdient NICHT mehr, er hat nur Sharpe 0,85 statt 0,36 | [`bots.md`](docs/bots.md) |
| 28 | **Eigenes Kapital statt Challenge** | 🛑 **Kostenkorrektur: der Backtest verrechnete 32 bp statt 16 bp je Roundtrip** (BTC 0,35x: 48,4 % → **53,8 %**). Ohne Tageslimit zaehlt Sharpe: **Short-Straddle (VRP) +26,3 % p.a. bei Sharpe 1,47 und nur -9,9 % Drawdown** schlaegt S/R (1,07 / -30,4 %) und BTC-Halten (0,34 / -76,6 %) | [`eigenkapital.md`](docs/eigenkapital.md) |
| 29 | **Ziel: 20-30 % p.a. auf 100k** | **Auf einem 3-%-Tageslimit-Konto mathematisch unmoeglich** (Ø +1,4 %). Ohne Tageslimit: Ø +13,6 bis +19,9 %, 42 % der Jahre ueber 20 %. Und: 2k→100k→0 ist der NORMALFALL eines gehebelten Muenzwurfs — **96 % derer, die mit 20x die 100k erreichen, verlieren alles** | [`ziel.md`](docs/ziel.md) |
| 30 | **Andere Maerkte statt Krypto (24 FRED-Reihen, teils seit 1971)** | Korrelation **+0,001 statt +0,68**, Diversifikationsgewinn Faktor 3,5. **Trendfolge seit 2008 tot** (Sharpe 0,80 → 0,39 → **-0,17**). Aber: **VRP existiert in Aktien ebenfalls** — S&P/VIX t=**4,67**, Straddle Sharpe **1,52**, DD **-13,7 %** inkl. COVID. Bei 3x Hebel ohne Tageslimit: **+22,3 % p.a., 42,5 % der Jahre ueber 20 %** | [`andere_maerkte.md`](docs/andere_maerkte.md) |
| 31 | **Vier Prop-Anbieter durchgerechnet** | Entscheidend ist **trailing gegen statisch**, nicht EOD gegen intraday: bei 3 % DD ueberlebt statisch **54,5 %**, EOD-trailing **0,0 %**. Drei der vier sind Futures-only und koennen die Strategie gar nicht traden. **Iron Condor (erlaubt) schlaegt den nackten Straddle**: Sharpe 2,55 statt 1,52, bei 3 % statischem DD **+29 % p.a. und 58,6 % der Jahre ueber 20 %** | [`anbieter.md`](docs/anbieter.md) |
| 32 | **Vanquish mit den echten Regeln** | 🛑 **Mein Hebel-Sweep war strukturell falsch**: bindend ist der Maximalverlust gegen den 6.000-$-Puffer, nicht das Nominal. Neu: **enge Fluegel schlagen weite** (Kappe 0,8 % bei 4x: +21,0 % bei **98,5 %** Ueberleben; Kappe 2,0 %: +22,9 % bei **77,2 %**). Robust ist **3x: +15,9 % p.a., 100 % Ueberleben**. Evaluierung 90,9 %, Konsistenzregel unkritisch (bester Tag = 10 % des Jahresgewinns) | [`vanquish.md`](docs/vanquish.md) |
| 33 | **Echtes Iron-Condor-Modell statt Naeherung** | 🛑 **Praemienanteil 4-11 %, nicht 40 %** — aber der Skew ist nicht der Grund (nur 0,6 pp), sondern die Fluegelbreite. **Delta-Drag gemessen**: enge Strangles ohne Hedge haben Sharpe **-0,18**. Frueher Stop bei 35 % des Maximalverlusts verdoppelt den Sharpe auf **2,38**. Endstand: **6x Nominal = +14,8 % p.a. bei 99,1 % Ueberleben** | [`condor.md`](docs/condor.md) |
| 34 | **Validierung an echter SPX-Kette (32.168 Optionen, kostenlos)** | Modell **bestaetigt**: Straddle 3,09 % gerechnet gegen 3,06 % real. Condor-Anteil Modell 4,1/8,0/10,6 % gegen real 4,3/8,8/12,5 % — leicht **konservativ**. **4-Leg-Slippage nur 0,027 % je Roundtrip** = 14 % des Kredits. Endstand **+14,4 % p.a. bei 100 % Ueberleben**; vier Methodenwege landen alle bei 13-16 % | [`validierung.md`](docs/validierung.md) |
| 35 | **Mehrere Konten statt mehr Hebel** | **Strikt besser**: 3 Konten je 4x hat dasselbe Nominal wie 1 Konto mit 12x — Stopverlust aber **67 % statt 201 %** des Puffers, Ueberleben **100 % statt 79,4 %**, Ertrag **43.214 $ statt 39.322 $**. Aber: Konten sind **perfekt korreliert** — echte Streuung kommt vom **Versetzen der Verfallszyklen** (Vol -31 %, Sharpe 2,07→2,69). Endstand **~49.000 $/Jahr bei 98,1 %** | [`parallel.md`](docs/parallel.md) |
| 36 | **Zwei Regelfragen, eine davon entscheidend** | 🛑 **Widerspruch: statisch gegen trailing.** Bei 6x Nominal: statisch **86,1 % ueberlebt / +29,5 %**, trailing **15,9 % / -1,0 %**. 🛑 **Korrektur:** Konsistenzregel misst „Best **Trade**", nicht Tag — **38,3 % der Jahre ueber 30 %**, meine Entwarnung war falsch. **Loesung: Wochenzyklen** (+4,90 % p.a., Sharpe 2,59, nur 9,1 % gerissen) | [`regelfragen.md`](docs/regelfragen.md) |
| 37 | 🛑 **Die echten Vanquish-Regeln (PDF)** | **„No spreads, no selling to open"** auf SPX/XSP/VIX, **Intraday Trailing** Drawdown, **keine Overnight-Positionen**. Damit ist nur die **Verliererseite** der einzigen gemessenen Praemie erlaubt. Zeilen 31-36 sind hinfaellig — ich habe fuenf Dokumente auf unverifizierte Regelangaben gebaut | [`vanquish_regeln.md`](docs/vanquish_regeln.md) |
| 38 | **Mehrere Kraken-Challenges parallel** | **Gleichzeitig bringt exakt NULL**: 1 Challenge 70,9 %, 3 gleichzeitige ebenfalls **70,9 %** — drei Lottoscheine mit denselben Zahlen. **Mit 90 Tagen Versatz: ~100 %**, dass mindestens eines durchkommt, ~110 $ je gefundetem Konto | [`kraken_parallel.md`](docs/kraken_parallel.md) |
| 39 | **„Ich bin im Minus" — heisst das was?** | Rund **jeder zweite Trade** steht zwischenzeitlich im Minus. Die scheinbare Vorhersagekraft (r=+0,454) ist **groesstenteils Arithmetik** (mechanisch +0,354); der Vorwaerts-Anteil ist +0,145 bei **p=0,346**. Signal **umdrehen** kostet 166 bp je Trade | [`im_minus.md`](docs/im_minus.md) |
| 40 | **„Marktphasen und Price Action sind das Wichtigste"** | **Mit Orakel: 348 bp Spanne** (Seitwaerts -80,5 bp, Trend +268,1 bp) — groesster Einzeleffekt des Projekts. **Aber Phasen persistieren nicht**: Korrelation Vergangenheit↔Zukunft -0,077 bis +0,026. Der Versuch als Filter ist der **neunte**, der durchfaellt (Bonferroni p=1,00, keine Monotonie) | [`marktphasen.md`](docs/marktphasen.md) |
| 41 | **„Wie machen das Firmen?"** | **Prop-Firmen haben keinen Handels-Edge** — kritische Bestehensquote **4-9 %**; die Regeln sind das Produkt. **Handelsfirmen** verdienen nicht mehr als du (+19,1 % gegen +18,3 % p.a.), aber mit **Sharpe 0,85 statt 0,36**. Bei gleichem 10-%-Drawdown: Sharpe 0,36 → **1,5 %** p.a., Sharpe 3,0 → **35,2 %**. Fuer Sharpe 3 braucht man **~70 unkorrelierte Edges** — bei 5 % Trefferquote rund **1.400 getestete Ansaetze** | [`firmen.md`](docs/firmen.md) |
| 42 | **Der ehrliche Weg** | **Einkommen = Kapital x Rendite**: 3.000 €/Monat bei 20 % p.a. verlangen **180.000 €**. Eine um 35 % hoehere Rendite spart **genauso viel Zeit wie eine um 35 % hoehere Sparrate** — nur ist die Sparrate sicher. Prop-Konten sind **kein Gehalt**, sondern ein Sparbeschleuniger (2.400-7.200 $/Jahr). Und: auch Profi-Trader leben von einem **Gehalt**, nicht von eigenen Renditen | [`der_weg.md`](docs/der_weg.md) |
| 43 | **„Alle TradingView-Strategien haben Sharpe unter 0,3"** | **Rauschdecke gemessen**: 1.000 wertlose Varianten ueber 5 Jahre → bester zeigt Sharpe **1,8 ohne jeden Edge**. Und **Sharpe 0,3 braucht 43 Jahre**, um von null unterscheidbar zu sein — auch mein eigener S/R-Fund (0,36). Praezisierung: Chartmuster 0,00-0,36 (Aussage stimmt), **Risikopraemien 1,5-1,9** (Aussage zu stark) | [`tradingview.md`](docs/tradingview.md) |
| 44 | **4h MACD + Stochastik + Bollinger** (Nutzerentscheidung, direkt gemessen) | **Das Lehrbuch-Setup existiert nicht**: Band-Beruehrung + Stoch<20 + MACD-Histogramm steigend = **0 Vorkommen in 3,8 Jahren** (die dritte Bedingung widerspricht den ersten beiden). Einzeln alle drei negativ (-14 bis -76 bp) **auch bei null Kosten**. Trendlesart: t=0,20 in der Suche, **-0,10 im Holdout** (ETH +69 → **-93 bp**). Gitter aus 324 Varianten: beste 8 **+61 bp → -360 bp**. Pass-Rate **57,8 % → 9,3 %** (Zufall waere 37,5 %). Was wirklich wirkt: **Groesse und Haltedauer** — jedes Signal handeln = **0,0 %**, 28,9 % Gebuehren p.a. | [`macd_stoch_boll.md`](docs/macd_stoch_boll.md) |
| 45 | **Dieselben drei als reine Informationsquelle** (nicht als Signal) | **Richtung: leer** — Transinformation **0,002 von 1,0 Bit**, teils unter der Kontrolle; das einzige monotone Muster (Stochastik) **kippt das Vorzeichen in allen drei Maerkten** (t zwischen -0,58 und +0,35). **Risiko: haelt** — Bollinger-Breite sagt die kommende 5-Tage-Vol an, Faktor **1,85/2,15/1,89** in der Suche und **1,55/1,33/1,59 im Holdout**, sechs von sechs gleiche Richtung. Aber: **die reine realisierte Vol ist der bessere Schaetzer** (R² 0,315 gegen 0,228), Zuwachs der Breite nur +0,009. Drei Indikatoren = **zwei Groessen** (MACD↔Momentum +0,88, %B↔Stoch +0,85, Breite↔Vol +0,75) | [`indikatoren_als_info.md`](docs/indikatoren_als_info.md) |
| 46 | **Gibt es Besseres als die Bollinger-Baender fuer Risiko?** | **Ja — die Baender liegen auf Platz 9 von 14.** Rangkorrelation mit dem Kraken-Tageslimit (Tag <= -3 %), BTC-Holdout: **DVOL 0,210**, **Abwaerts-Semivol 0,166**, EWMA 0,155, ATR 0,143, **Bollinger 0,078**. Aber: **Niveau ist nicht prognostizierbar** (fast alle Out-of-Sample-R² negativ, Bollinger -0,134) — nur der Rang. Und der Zahltag-Test dreht es um: **jede Vol-Steuerung senkt die Pass-Rate um 9-15 Pp** bei gleichem Ø Einsatz, obwohl der Drawdown faellt. Grund: das Regelwerk hat ein **Ziel**, und Vol ist der einzige Weg dorthin | [`risiko_indikatoren.md`](docs/risiko_indikatoren.md) |
| — | Traden als Beruf | 3.000 EUR/Monat verlangen ~338.000 EUR; Prop-Konto lebt erwartet 102 Tage | [`trading_as_job.md`](docs/trading_as_job.md) |

### Die zwei Ergebnisse, die bleiben

**1. Ein echter Edge wurde gefunden** — die Volatilitaets-Risikopraemie:
implizite Vol uebersteigt die danach realisierte bei BTC um 10,5 pp (Median),
in 72 % der Faelle, t = 4,12 nach Ueberlappungskorrektur ueber 5,4 Jahre.
Delta-gehedgter Short-Straddle: **Sharpe 1,33**, +149 % ueber 64 Monate.
Er ist im Kraken-Prop-Konto **nicht erreichbar** (Kraken bietet 294 Futures
und 0 Optionen) und wuerde die Challenge auch dann nicht bestehen
(Rendite/Drawdown 0,69 statt der noetigen 1,67).

**2. Positionsgroesse schlaegt Edge.** Ohne jeden Edge, aber mit 15 %
Zielvolatilitaet: **8,2 %** Pass-Rate. Mit echtem Edge (Sharpe 1,33), aber
30 % Volatilitaet: **1,5 %**. Die optimale Zielvolatilitaet liegt ueber alle
Sharpe-Niveaus bei **15–16 % annualisiert** — eine Vorgabe, die keinerlei
Prognose voraussetzt.

Ein **realistischer** Backtester, um eine manuell handelbare **Renko-Reversal-Strategie**
gegen die Regeln der **Kraken-Prop-Challenge** zu testen — mit dem Ziel, die
Challenge **nachhaltig** (nicht per Glück) zu bestehen.

Die Engine bewertet die Strategie nicht nur nach Rendite, sondern prüft, ob die
Equity-Kurve **jede** Kraken-Regel einhält: Profit-Target, Max Daily Loss und
Max Total Drawdown — inklusive **unrealisiertem** PnL, so wie Kraken es rechnet.

---

## Die Idee in einem Satz

> Renko-Bricks glätten das Rauschen. Bei **2 Gegen-Bricks** dreht die Position
> (Stop-and-Reverse). Der Backtester zeigt dir, ob dieses simple Regelwerk die
> engen Drawdown-Limits von Kraken übersteht — und mit welcher Positionsgröße.

---

## Kraken-Prop-Regeln (eingebaute Presets)

Stand 2026. **Für alle Tiers gilt: 3 % Max Daily Loss** (Reset 00:30 UTC),
**realized + unrealized** PnL zählen, keine Consistency-Rule, keine
Mindest-Handelstage.

| Preset          | Profit-Target      | Max Drawdown   | Typ      |
|-----------------|--------------------|----------------|----------|
| `1step_turbo`   | 9 %                | 3 %            | statisch |
| `1step_pro`     | 12 %               | 3 %            | statisch |
| `1step_classic` | 10 %               | 6 %            | statisch |
| `2step_classic` | 10 % + 5 %         | 8 %            | trailing |

- **statisch**: Drawdown-Grenze = Startkapital − X % (fix, ab Kontostart).
- **trailing**: Grenze folgt dem **Equity-Hoch** nach oben.

> ⚠️ **Prop-Firmen ändern Regeln.** Diese Werte sind ein dokumentierter
> Ausgangspunkt. Gleiche sie **vor dem Kauf** mit der aktuellen Kraken-Seite ab.
> Kraken Prop ist der Consumer-Rebrand von *Breakout*; die alte
> Vertragssprache nennt teils abweichende Zahlen. Quellen unten.

---

## Installation

```bash
python -m pip install -r requirements.txt
# oder als Paket (inkl. CLI-Befehl "prop-backtester"):
python -m pip install -e .
```

Nur NumPy/Pandas werden zwingend gebraucht. `matplotlib` ist optional (nur für Plots).

---

## Schnellstart

```bash
# Mit synthetischen Demo-Daten (kein Netzwerk nötig)
PYTHONPATH=src python -m prop_backtester --demo --balance 50000 --risk 0.005

# Mit eigener CSV (Spalten: time,open,high,low,close,volume)
PYTHONPATH=src python -m prop_backtester --csv meine_daten.csv --config configs/example.yaml

# Live von Kraken laden (öffentliche API, XBTUSD, 1h-Kerzen) + Plot speichern
PYTHONPATH=src python -m prop_backtester --kraken XBTUSD --interval 60 --plot equity.png

# Alle Presets anzeigen
PYTHONPATH=src python -m prop_backtester --list-presets

# PARAMETER-SWEEP: robusteste Einstellung ueber viele Marktphasen finden
PYTHONPATH=src python -m prop_backtester --sweep --preset 1step_classic --scenarios 12

# Sweep als Walk-Forward auf echten Daten (rollierende Fenster)
PYTHONPATH=src python -m prop_backtester --sweep --csv daten.csv --wf-window 3000 --wf-step 1500

# Sweep + Heatmap (Pass-Rate / Rendite / Drawdown) als PNG
PYTHONPATH=src python -m prop_backtester --sweep --scenarios 12 --heatmap heatmap.png
```

Oder als Python-API:

```python
from prop_backtester import backtest, BacktestConfig, data

df = data.generate_synthetic(bars=8000)      # oder data.load_csv(...) / data.fetch_kraken_ohlc(...)
cfg = BacktestConfig()
cfg.initial_balance = 50_000
cfg.risk.risk_per_trade_pct = 0.005          # 0.5 % Risiko pro Trade

result, metrics, challenges = backtest(df, cfg)
print(metrics["return_pct"], metrics["max_drawdown_pct"])
for key, ch in challenges.items():
    print(key, "PASS" if ch.passed else "FAIL")
```

Siehe auch `examples/quickstart.py`.

---

## Echte Kraken-Historie laden

Krakens OHLC-API liefert nur ~720 aktuelle Kerzen. Für **tiefe Historie** nutzt
der eingebaute Downloader den **Trades-Endpoint** und aggregiert die Trades zu
OHLC-Bars:

```bash
# BTC/USD, 1h-Bars, Zeitraum wählbar; schreibt eine CSV
PYTHONPATH=src python -m prop_backtester --download-kraken XBTUSD \
    --interval 60 --from 2024-01-01 --to 2024-06-01 --out xbtusd_1h.csv

# dann Backtest / robuster Walk-Forward-Sweep auf echten Daten:
PYTHONPATH=src python -m prop_backtester --csv xbtusd_1h.csv --balance 50000
PYTHONPATH=src python -m prop_backtester --sweep --csv xbtusd_1h.csv --wf-window 3000 --wf-step 1500
```

Programmatisch:

```python
from prop_backtester import kraken
df = kraken.download_ohlc("XBTUSD", interval_minutes=60,
                          since="2024-01-01", until="2024-06-01")
df.to_csv("xbtusd_1h.csv")
```

Details: paginiert automatisch über den `last`-Cursor, respektiert das
Rate-Limit (`--sleep`, Default 1.6 s) mit exponentiellem Backoff, und lässt sich
per `--max-trades` begrenzen. Tiefe Historien dauern entsprechend.

> 🌐 **Netzwerk:** Der Download braucht ausgehenden Zugriff auf `api.kraken.com`.
> In manchen Umgebungen (z.B. eingeschränkte Egress-Policy) ist das blockiert —
> dann den Download **lokal** ausführen und die CSV übertragen. Siehe die Doku zu
> [Umgebungen & Netzwerk](https://code.claude.com/docs/en/claude-code-on-the-web).

---

## Live-Signale nach Telegram

Der Bot zieht die aktuellen Kraken-Kerzen, erkennt neue 2-Brick-Reversals und
schickt dir bei einem Signal eine Telegram-Nachricht — du schaust nur noch aufs
Handy. Nutzt **nur geschlossene Kerzen** (kein Repainting) und merkt sich, was
schon gesendet wurde (kein Doppel-Ping).

**1. Telegram-Bot anlegen:** In Telegram `@BotFather` → `/newbot` → Token kopieren.
Deinem neuen Bot einmal etwas schreiben, dann Chat-ID holen:
`https://api.telegram.org/bot<TOKEN>/getUpdates` → `chat.id`.

**2. Config anlegen:** `configs/signals.example.yaml` → `configs/signals.yaml` kopieren.
Token/Chat-ID am besten als Umgebungsvariablen setzen (nicht in die Datei):

```bash
export TELEGRAM_TOKEN=123456:ABC...
export TELEGRAM_CHAT_ID=987654321
python -m prop_backtester.signals --config configs/signals.yaml --once   # Testlauf
python -m prop_backtester.signals --config configs/signals.yaml --loop   # dauerhaft
```

**3. Dauerbetrieb (damit du nur noch Telegram brauchst):** auf einem immer laufenden
Gerät (Raspberry Pi, kleiner VPS) `--loop` starten, oder stündlich per Cron:

```cron
5 * * * * cd /pfad/zum/projekt && TELEGRAM_TOKEN=... TELEGRAM_CHAT_ID=... \
  python -m prop_backtester.signals --config configs/signals.yaml --once >> signals.log 2>&1
```

Die Nachricht enthält Richtung, Einstiegs-/Triggerkurs, Stop (2 Bricks) und die
zur Risiko-Einstellung passende Positionsgröße. Voreingestellt ist die
4-Jahres-validierte Config (0.75× ATR, 0.3 % Risiko).

**24/7 auf einem Server (systemd):** Schritt-für-Schritt in
[`docs/deploy_signals.md`](docs/deploy_signals.md) — Auto-Neustart nach Reboot,
Token sicher getrennt.

### Zwei Modi — und warum `levels` der richtige ist

| Modus | Was kommt aufs Handy | Im Test |
|---|---|---|
| **`levels`** (Default) | Die **kommenden Trigger-Level** mit SL/TP/Size — du legst dort **vorab** Stop-Orders hin | **94 % Pass-Rate** |
| `signals` | Meldung erst **nachdem** das Reversal ausgelöst hat | 7 % Pass-Rate |

Der Edge hängt daran, dass **auf dem Brick-Level** gefüllt wird. Die Levels
stehen im Voraus fest (`Anker ± Brickgröße`), deshalb funktionieren ruhende
Orders — Reagieren nach Kerzenschluss dagegen nicht (siehe
[`docs/realism.md`](docs/realism.md)). Validiert: die vorhergesagten Level
weichen im Median nur **0,017 %** vom echten Auslösepreis ab.

```bash
python -m prop_backtester.signals --config configs/signals.yaml --loop            # levels (Default)
python -m prop_backtester.signals --config configs/signals.yaml --loop --mode signals
```

Der Bot meldet sich nur, wenn sich die Level ändern (kein Spam). Zieh die Orders
stündlich nach — die Level wandern mit der ATR und dem Trend.

📋 **Beim Handeln zur Hand:** [`docs/spickzettel.md`](docs/spickzettel.md) —
eine Seite „Situation → Aktion" fürs Handy (inkl. Setup-Check, Positionsgrößen-
Formel und den drei „Nie").

> ⚠️ Signale sind Entscheidungshilfen, keine automatischen Orders — du platzierst
> sie selbst. Kein Finanzrat. Vorher [`docs/realism.md`](docs/realism.md) lesen.

---

## Wie es funktioniert

### 1. Renko-Bricks (ATR-basiert)
Die Brick-Größe ist **dynamisch** = `ATR(14) × Multiplikator` (Wilder-ATR). In
volatilen Phasen werden Bricks größer, in ruhigen kleiner — realistischer für
Krypto als eine feste Größe. Ein neuer Brick entsteht, sobald sich der Preis um
eine Brick-Größe vom letzten Brick-Schluss entfernt. Fixe Bricks (% oder $) sind
per Config ebenfalls möglich.

### 2. Strategie: 2-Brick-Reversal (Stop-and-Reverse)
Sobald **2 gleichgerichtete Bricks** vorliegen, ist die Zielposition long (+1)
bzw. short (−1). Die Position bleibt bestehen, bis das Gegensignal (2
Gegen-Bricks) kommt — dann wird gedreht. Das entspricht dem klassischen
2-Brick-Reversal: Nach einem Up-Brick auf Kurs C müssen für 2 Down-Bricks
2 × Brick fallen. Der Fill erfolgt am Gitter-Level des auslösenden Bricks (ein
Kurs, der intrabar real erreicht wurde → **kein Lookahead**).

Per Config: `allow_short: false` macht daraus eine Long-only-Strategie (geht bei
Verkaufssignalen flach, statt zu shorten).

### 3. Realistische Ausführung
- **Positionsgröße** aus Risiko: `Risiko% × Kontostand ÷ (stop_bricks × Brick)`.
  Der Stop entspricht dem Reversal-Abstand (2 Bricks). Gehebelt bis `max_leverage`.
- **Gebühren** pro Seite + **Slippage** pro Fill (adversariell).
- **Mark-to-Market** je Bar inkl. unrealisiertem PnL, plus **konservative
  Intrabar-Extrema** (High/Low), damit Drawdown-Breaches nicht „durchrutschen".

### 4. Prop-Regel-Prüfung
Der Evaluator läuft Bar für Bar über die Equity-Kurve:
- **Daily-Reset 00:30 UTC** setzt die Tages-Verlustgrenze neu.
- **Breach** (Daily Loss *oder* Drawdown) wird **vor** dem Target geprüft
  (pessimistisch). Beim Trailing-Drawdown wird das Equity-Hoch in der
  ungünstigsten Reihenfolge angehoben.
- **Mehrstufig (2-Step):** Phase 2 wird auf einem **frischen** Konto gleicher
  Größe bewertet — genau wie in echt.

---

## Parameter-Sweep — die robusteste Einstellung finden

Ein Einzellauf sagt wenig: Vielleicht hattest du Glück mit dem Zeitfenster. Der
**Sweep** testet jede Parameter-Kombination gegen **viele Szenarien** und misst,
wie *zuverlässig* sie besteht.

```
 atr_multiplier  atr_period  risk_per_trade_pct   pass%   medRet%   medDD%   worstDD%
         0.75          14          0.005          91.7    18.19     5.94     9.21
         0.75          20          0.005          83.3    20.80     7.87    10.91
            1          14         0.0075          50.0    11.14     9.79    12.52
 BESTE ROBUSTE EINSTELLUNG: atr_multiplier=0.75, atr_period=14, risk_per_trade_pct=0.005
   -> Pass-Rate 91.7%, Median-Rendite 18.19%, Worst-Drawdown 9.21%
```

- **`pass_rate`**: Anteil der Szenarien, in denen die Challenge bestanden wurde
  — die eigentliche Kennzahl für *nachhaltiges* Bestehen.
- Ranking: höchste Pass-Rate → kleinster Worst-Case-Drawdown → höchste Rendite.
- **Zwei Szenario-Quellen:**
  - *Synthetisch* (`--scenarios N`): viele realistische Zufallsmärkte mit
    gestreuter Drift/Vola (Bull, Bär, Range).
  - *Walk-Forward* (`--csv/--kraken` + `--wf-window/--wf-step`): rollierende
    Fenster echter Historie — der realistischste Test. Jedes Fenster ist ein
    eigener Challenge-Versuch.

Programmatisch:

```python
from prop_backtester.sweep import run_sweep, synthetic_scenarios, DEFAULT_GRID
from prop_backtester.viz import save_heatmap

scenarios = synthetic_scenarios(n=20, bars=6000)
sweep = run_sweep(scenarios, DEFAULT_GRID, preset_key="1step_classic")
print(sweep.best)          # robusteste Parameter
print(sweep.table.head())  # komplettes Ranking
save_heatmap(sweep, "heatmap.png")   # 3-Panel-Heatmap
```

### Heatmap

`save_heatmap` (bzw. `--heatmap`) rendert drei Panels über das Parametergitter
(ATR-Multiplikator × Risiko): **Pass-Rate** (sequenziell), **Median-Rendite**
(divergierend um 0) und **Worst-Drawdown** (divergierend um das Drawdown-Limit
des Presets). Blau = gut, Rot = schlecht; jede Zelle ist zusätzlich beschriftet,
sodass die Farbe nie die einzige Information ist. Auf echten Kraken-Daten zeigt
sie klar: **kleine Bricks (0.5–0.75× ATR) unten-links gewinnen**, große Bricks
(≥1.25×) bestehen nicht, und mehr Risiko/Trade erkauft Rendite gegen
Drawdown-Nähe zum Limit.

---

## Wie realistisch ist das?

Bewusst auf Realismus ausgelegt — die Punkte, die Backtests sonst schönrechnen:

- **Kosten:** Gebühr + halber Spread + fixe Slippage + **vola-abhängige
  Slippage** (teurer in wilden Phasen) + **Funding-Kosten** auf offene
  Positionen (Perp-Drag). Alles in `configs/example.yaml` einstellbar.
- **Equity-Bewertung wie bei Kraken:** realized **und** unrealized PnL fließen in
  Daily-Loss und Drawdown ein; Daily-Reset 00:30 UTC.
- **Konservative Intrabar-Prüfung:** Breaches werden gegen High/Low geprüft und
  *vor* dem Target ausgewertet (pessimistisch) — kein „durchrutschen".
- **Realistische Testmärkte:** der Demo-/Szenario-Generator nutzt
  **Volatilitäts-Cluster (GARCH), Fat Tails (Student-t) und Jumps** statt eines
  reinen Random Walks — so werden enge Drawdowns wirklich gestresst.
- **Kein Lookahead:** Fills am Renko-Gitter-Level, das intrabar real erreicht wurde.

**Grenzen (ehrlich):** Bar-granular (kein Tick-Orderbuch), Renko-Fills sind eine
Näherung der Ausführung, Funding als konstanter Drag statt echter Funding-Kurve,
und synthetische Daten bleiben synthetisch. Für die belastbarste Aussage:
**echte Kraken-Historie im Walk-Forward-Sweep** verwenden.

---

## Nachhaltig bestehen — worauf es ankommt

Der Backtester macht die zentrale Wahrheit sichtbar: **Bei Krypto ist nicht das
Target das Problem, sondern der Drawdown.** 3–8 % Drawdown sind bei BTC/ETH
schnell erreicht. Praktische Hebel:

1. **Risiko pro Trade klein halten** (`risk_per_trade_pct` 0.3–0.7 %). Das ist
   der stärkste Regler gegen einen frühen Drawdown-Bust.
2. **Preset zur eigenen Vola wählen:** Enge 3 %-Drawdown-Tiers (Turbo/Pro)
   verzeihen fast nichts. `1step_classic` (6 %) ist oft der nachhaltigste
   Startpunkt.
3. **Brick-Größe kalibrieren** (`atr_multiplier`): größere Bricks = weniger
   Whipsaw, aber späteres Reagieren. Über mehrere Werte backtesten.
4. **Über viele Marktphasen testen** (Bull, Bär, Range) — nicht nur das eine
   schöne Jahr. Mit `--kraken` echte Historie ziehen oder mehrere Seeds/CSV nutzen.

---

## Konfiguration

Alle Parameter stehen in `configs/example.yaml` (Renko, Strategie, Kosten,
Risiko). CLI-Flags (`--balance`, `--risk`, `--atr-period`, `--atr-mult`)
überschreiben einzelne Werte.

---

## Tests

```bash
python -m pytest -q
```

---

## Projektstruktur

```
src/prop_backtester/
  config.py     # Konfigurations-Objekte (+ YAML-Loader)
  data.py       # CSV / Kraken-API / synthetische Daten
  renko.py      # ATR-basierter Renko-Aufbau
  strategy.py   # 2-Brick-Reversal-Signale
  engine.py     # Ausführung, Kosten (Gebühr/Spread/Slippage/Funding), Equity-Kurve
  prop.py       # Kraken-Presets + Regel-Evaluator
  sweep.py      # Parameter-Sweep + Robustheit (Multi-Szenario / Walk-Forward)
  kraken.py     # Downloader: tiefe Historie via Trades-Endpoint -> OHLC
  viz.py        # Heatmaps der Sweep-Ergebnisse (Pass-Rate / Rendite / Drawdown)
  signals.py    # Live-Signal-Bot (Renko-Reversal -> Telegram)
  telegram.py   # Telegram-Versand
  report.py     # Kennzahlen, Textbericht, Plot
  cli.py        # Kommandozeile
configs/example.yaml
examples/quickstart.py
tests/
```

---

## Haftungsausschluss

Dieses Projekt dient der **Recherche und Bildung**. Es ist keine Anlageberatung.
Backtests bilden die Zukunft nicht ab; reale Ausführung, Slippage, Gebühren und
Regeländerungen können abweichen. Kraken kann funded Capital nach eigenem
Ermessen als simuliert („B-Book") behandeln. Handle nur mit Kapital, dessen
Verlust du verkraften kannst.

---

## Quellen (Kraken-Prop-Regeln)

- [Kraken Prop — Übersicht](https://www.kraken.com/prop)
- [Support: What is Kraken Prop?](https://support.kraken.com/articles/what-is-kraken-prop)
- [Support: How Kraken Prop Evaluations Work](https://support.kraken.com/articles/how-kraken-prop-evaluations-work)
- [Support: Kraken Prop FAQ](https://support.kraken.com/articles/kraken-prop-faq)
