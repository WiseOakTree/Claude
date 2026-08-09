# Raus aus Krypto — was sich ändert und was nicht

> „Wir müssen nicht Krypto traden, wir können alles nehmen."

Richtig, und es war die produktivste Frage dieses Projekts. Geprüft mit
**24 Zeitreihen aus FRED**, teils seit 1971: Aktienindizes, Rohöl, Erdgas,
13 Währungspaare, US-Zinsen, VIX.

Zwei Ergebnisse: eines negativ, eines der beste Fund seit der
Volatilitätsprämie.

---

## 1. Was sich sofort ändert: die Korrelation

| | mittlere Paarkorrelation |
|---|---|
| Krypto (BTC/ETH/SOL/XRP) | **+0,68** |
| 20 Märkte quer über Anlageklassen | **+0,001** |

Das ist kein kleiner Unterschied, das ist ein struktureller. In Krypto hast du
faktisch **eine** Position mit vier Namen — deshalb brachte Diversifikation über
12 Coins nichts ([`ergebnisse.txt`](ergebnisse.txt)).

Gemessener Effekt auf die Trendfolge:

| | Sharpe |
|---|---|
| Mittelwert der **Einzel**märkte | 0,14 |
| **Portfolio** aus denselben Märkten | **0,49** |
| **Diversifikationsgewinn** | **Faktor 3,5** |

Das ist real und groß. Nur nützt es nichts, wenn das Signal selbst nichts hergibt.

---

## 2. Das negative Ergebnis: Trendfolge ist seit 2008 tot

Zeitreihen-Momentum ist der einzige Strategietyp mit belastbarer akademischer
Evidenz über Anlageklassen hinweg. Look-ahead-frei getestet, invers
vol-gewichtet, 2 bp Kosten:

| Horizont (Tage) | gesamt | 1990–2007 | 2008–2016 | **2017–2026** |
|---|---|---|---|---|
| 21 | 0,36 | 0,73 | −0,05 | 0,14 |
| 63 | 0,43 | 0,64 | 0,43 | 0,08 |
| 252 | 0,49 | **0,92** | 0,10 | 0,14 |
| 504 | 0,44 | 0,75 | 0,16 | 0,13 |
| 63/126/252 kombiniert | 0,44 | 0,80 | 0,39 | **−0,17** |

Nach Sektoren (2017–2026): Aktien **−0,13**, Rohstoffe **−0,19**, FX **−0,29**,
Anleihen **−0,23**.

**Jeder Horizont, jeder Sektor, das letzte Jahrzehnt: null oder negativ.**
Und der Gegentest bestätigt, dass es nicht am Vorzeichen liegt — gegen den
Trend gibt exakt −0,44.

*Einschränkung: Mein Universum ist FX-lastig (13 von 21) und hat weder Metalle
noch Agrar noch Aktienindex-Futures anderer Länder. Ein echtes
Managed-Futures-Programm nutzt 100+ Märkte. Das hier ist ein fairer Test dessen,
woran ich herankomme — kein endgültiges Urteil über die Branche. Der berichtete
Verlauf der CTA-Indizes seit 2009 sieht allerdings ähnlich aus.*

---

## 3. Der Fund: die Volatilitätsprämie gibt es in Aktien auch — mit besseren Daten

In Krypto war die VRP der einzige Edge, der alle Kontrollen bestand. **Dieselbe
Prämie, gemessen am S&P 500 gegen den VIX:**

| | implizit | realisiert danach | **VRP** | Anteil positiv | **t** | p |
|---|---|---|---|---|---|---|
| **S&P 500 / VIX, 2016–2026** | 17,0 % | 12,4 % | **+4,65 pp** | **83,4 %** | **4,67** | **<0,00001** |
| BTC / DVOL, 2021–2026 | 56,4 % | 48,5 % | +10,47 pp | 72,3 % | 4,12 | 0,0001 |

**Das ist die stärkste Bestätigung in diesem ganzen Projekt.** Zwei völlig
unabhängige Märkte, derselbe Mechanismus, beide signifikant nach
Überlappungskorrektur. Kein Muster, das ich in Krypto gefunden habe, hat je
eine zweite Anlageklasse überstanden — dieses schon.

*(Ein erster Test gegen den **Nasdaq** ergab t = −1,19. Das war ein Fehler von
mir: Der VIX misst die implizite Vol des **S&P 500**. Der Nasdaq schwankt
stärker, damit sieht die Prämie künstlich negativ aus. Falsche Paarung, kein
Gegenbeleg.)*

### Geerntet: monatlicher delta-gehedgter Short-Straddle auf den S&P 500

| | |
|---|---|
| Rendite p.a. | **+8,6 %** |
| Volatilität | **5,5 %** |
| **Sharpe** | **1,52** |
| größter Drawdown | **−13,7 %** (16. März 2020) |
| schlechtester Tag | −5,58 % |
| **Tage unter −3 %** | **0,16 %** |

| Zeitraum | Sharpe | p.a. |
|---|---|---|
| 2010er | 1,68 | +7,6 % |
| **2020er** | **1,48** | **+9,2 %** |

**Der Zeitraum enthält Volmageddon (Februar 2018), den COVID-Crash (März 2020)
und den Bärenmarkt 2022** — und der größte Drawdown war 13,7 %. Genau der Tag,
an dem das Produkt XIV auf null ging, kostete diese Strategie 13,7 %. Der
Unterschied ist der **tägliche Delta-Hedge**: XIV war gehebelt und ungehedgt.

---

## 4. Warum das für dein Problem wichtiger ist als alles bisher

Deine Sperre war das **3-%-Tageslimit** ([`ziel.md`](ziel.md)). Der Grund: Um
20–30 % zu verdienen, brauchtest du in Krypto so viel Volatilität, dass ein
−3 %-Tag zwangsläufig kommt.

**Der S&P-Straddle dreht das um.** Er läuft bei **5,5 % Jahresvolatilität** —
nur 0,16 % der Tage liegen unter −3 %. Damit kannst du **hebeln, statt groß zu
handeln**:

| Regelwerk | bester Hebel | überlebt | Ø Rendite | Jahre ≥20 % |
|---|---|---|---|---|
| **Kraken-Typ (3 % Tag / 6 % DD)** | 1× | 74,8 % | +5,3 % | **6,8 %** |
| 5 % Tag / 10 % DD | 2× | 60,3 % | +8,6 % | 23,6 % |
| **kein Tageslimit / 10 % DD** | **3×** | **78,2 %** | **+22,3 %** | **42,5 %** |
| | 4× | 71,4 % | +29,9 % | **52,6 %** |
| **eigenes Kapital** | 3× | 100 % | +27,3 % | 49,0 % |

**Bei „kein Tageslimit / 10 % Drawdown" und 3× Hebel: +22,3 % im Jahr,
78 % Überlebensrate, 42,5 % der Jahre über 20 %.** Das ist dein Ziel — zum
ersten Mal getroffen, nicht angenähert.

Und die Sperre bleibt dieselbe: **Mit 3 % Tageslimit bricht auch das ein**
(6,8 % der Jahre ≥20 %). Das Tageslimit ist der Engpass, nicht der Markt.

---

## 5. Der Direktvergleich aller Kandidaten

| | Sharpe | Vol | max. DD | Datenbasis | Kosten/RT |
|---|---|---|---|---|---|
| BTC-Straddle (VRP) | **1,85** | 13,6 % | −13,7 % | 5,4 Jahre | ~5 bp |
| **S&P-500-Straddle (VRP)** | **1,52** | **5,5 %** | **−13,7 %** | 10 Jahre | **~2 bp** |
| S/R-Ausbruch BTC | 1,07 | 25,0 % | −30,4 % | 5,4 Jahre | 16 bp |
| Trendfolge 20 Märkte | 0,44 | 15,1 % | −50,5 % | 36 Jahre | ~2 bp |
| — davon 2017–2026 | **−0,17** | 15,1 % | −38,2 % | 9 Jahre | ~2 bp |
| BTC einfach halten | 0,34 | 55,6 % | −76,6 % | 5,4 Jahre | einmalig |

Der BTC-Straddle hat den höheren Sharpe. **Der S&P-Straddle ist trotzdem der
bessere Kandidat**, aus drei Gründen:

1. **Die Daten sind ehrlicher.** 10 Jahre mit drei Krisen gegen 5,4
   vergleichsweise ruhige Jahre. Der Krypto-Datensatz enthält kein Ereignis vom
   Typ März 2020 — der S&P-Datensatz enthält März 2020.
2. **Die Kosten sind ein Achtel.** ~2 bp statt 16 bp.
3. **Die niedrige Volatilität ist ein Vorteil, kein Nachteil.** Du erreichst
   dein Ziel über Hebel statt über Positionsgröße — und Hebel auf eine ruhige
   Strategie reißt das Tageslimit seltener als eine wilde Strategie ohne Hebel.

---

## 6. Was ich dazu ausdrücklich sagen muss

**1. Der S&P-Test umfasst nur 2016–2026.** FRED liefert die S&P-Reihe nicht
länger. Die Fachliteratur findet dieselbe Prämie seit 1990, aber **das habe ich
nicht selbst nachgerechnet** — es ist kein Ergebnis dieses Projekts.

**2. Short Straddle bleibt Short Gamma, auch mit besseren Zahlen.** Bei 4×
Hebel wäre der März 2020 ein Drawdown von rund 55 % gewesen. Die Tabelle zeigt
71,4 % Überlebensrate bei 4× — aber der Datensatz enthält **einen** COVID-Crash.
Ein zweiter, etwas schlimmerer, steht in keiner dieser Zahlen.

**3. Höchstens 2×, bis du es ein Jahr live gehandelt hast.** Bei 2× steht
+15,0 % Ø Rendite und 86,0 % Überlebensrate. Das ist unter deinem Ziel — und
es ist die Zahl, die einen schlechten Tag überlebt. Die 4×-Zeile ist genau die
Sorte Zahl, die dich 2024 in die Achterbahn gesetzt hat.

**4. Der Straddle verlangt tägliche Arbeit.** Delta-hedgen, rollen, Margin
überwachen. Ohne Automatisierung ist das ein Teilzeitjob.

---

## Zusammenfassung

| Frage | Antwort |
|---|---|
| Bringt der Wechsel raus aus Krypto etwas? | **Ja** — Korrelation +0,68 → +0,001, Kosten 16 → 2 bp |
| Über ein besseres Signal? | **Nein.** Trendfolge ist seit 2008 bei null |
| Worüber dann? | **Über bessere Daten und niedrigere Volatilität** beim *selben* Edge |
| Was ist der Kandidat? | **S&P-500-Short-Straddle**, Sharpe 1,52, DD −13,7 % |
| Erreicht er 20–30 %? | **Ja, bei 3× Hebel — aber nur ohne 3-%-Tageslimit** |
| Was bleibt der Engpass? | **Das Tageslimit. Immer noch.** |

---

*Skripte: `research/multi_dl.py` (24 FRED-Reihen), `research/multi_trend.py`
und `research/multi_trend2.py` (Trendfolge, Horizonte, Sektoren),
`research/vrp_aktien.py` (VRP in Aktien), `research/vrp_stress.py`
(Stresstest und gefundetes Konto).*
