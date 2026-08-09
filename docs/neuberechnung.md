# Alle Befunde mit korrigierter Statistik

Nachtrag zu [`zu_streng.md`](zu_streng.md). Die Überlappungskorrektur war um
Faktor 5,48 zu streng; hier ist alles neu gerechnet.

**Zusammenfassung: Zwei Befunde werden deutlich stärker, alle Absagen bleiben
Absagen — und ein Effekt, den ich als gescheitert abgelegt hatte, ist der
stärkste Fund des Projekts.**

---

## 1. Der Kernbefund

| S/R-Ausbruch | n | Effekt | t ALT | **t NEU** |
|---|---|---|---|---|
| Suche 2021-24 | 474 | +49,4 bp | 0,36 | **1,52** |
| **Holdout 2025-26** | 301 | **+52,2 bp** | 0,47 | **1,73** |
| **gesamt** | 775 | **+50,5 bp** | 0,54 | **2,16** |

## 2. Die Volatilitätsprämie — Korrektur war dort richtig

| | t |
|---|---|
| naiv, ohne Korrektur | 22,77 |
| **alt (n/30, so berichtet)** | **4,16** |
| **neu (Einzigartigkeit)** | **4,19** |

Hier feuert an *jedem* Tag ein 30-Tage-Fenster — die Überlappung ist wirklich
maximal, beide Rechnungen fallen zusammen. **Der Fehler trat nur auf, wo
Signale dünn gesät waren.** Der VRP-Befund stand nie auf wackligem Grund.

---

## 3. Die zehn Filter — neu bewertet

Ausgangslage ohne Filter: **+49,4 bp (Suche) / +52,2 bp (Holdout)**

| Filter | Suche | t | Holdout | t | |
|---|---|---|---|---|---|
| 1 Mindest-Durchbruch 0,25 ATR | +41,2 | 1,15 | +21,2 | 0,65 | schlechter |
| 2 Rollenlogik nach Kurslage | +3,2 | 0,10 | **−17,4** | −0,58 | **kippt** |
| 3 Cooldown 48 Bars | +60,5 | 1,72 | +32,9 | 0,99 | schlechter |
| 5 Heikin-Ashi im Einklang | +58,9 | 1,77 | +44,8 | 1,45 | schlechter |
| 6 Session 08–20 UTC | +78,2 | 2,05 | +41,6 | 1,26 | schlechter |
| 7/8 Wochentage statt Wochenende | +57,3 | 1,65 | +34,2 | 1,09 | schlechter |
| **9 Marktphase Trend (ER > Median)** | **+84,6** | **2,07** | **+70,8** | **1,94** | **besser** |
| 10 VWAP im Einklang | +71,2 | 2,10 | +53,8 | 1,66 | ±0 |

**Neun von zehn bleiben gescheitert.** Der Marktphasen-Filter ist der einzige,
der in **beiden** Zeiträumen über der Ausgangslage liegt (+84,6 / +70,8 gegen
+49,4 / +52,2).

🛑 **Aber Vorsicht:** Das ist der beste von zehn getesteten Filtern. Bonferroni
verlangt bei zehn Tests t > 2,81 — er erreicht 2,07 und 1,94. Und er halbiert
die Signalzahl (474 → 244). Er bleibt damit **ein Kandidat, kein Befund.**

---

## 4. 🟢 Der Fund, den ich als gescheitert abgelegt hatte

Der **S/R-Bounce** (Kurs läuft in ein Level und schließt auf der haltenden
Seite) war als „fällt durch" abgelegt. Mit korrigierter Statistik:

| S/R-Bounce | n | Effekt | t ALT | **t NEU** |
|---|---|---|---|---|
| Suche | 651 | −72,1 bp | −0,63 | **−2,17** |
| Holdout | 433 | −87,4 bp | −0,90 | **−2,79** |
| **gesamt** | 1.084 | **−78,2 bp** | −0,99 | **−3,28** |

**Er ist nicht wirkungslos — er verliert signifikant.** Damit ist sein
Gegenteil der stärkste Einzeleffekt des Projekts.

### Ist das nur der Ausbruch unter anderem Namen?

| | |
|---|---|
| Ausbruchs-Ereignisse | 768 |
| Bounce-Ereignisse | 1.068 |
| **gemeinsame Bars** | **21 (2,0 %)** |

Nach Entfernen aller Überschneidungen: **+72,0 bp (t 2,18) / +88,9 bp
(t 2,82)** — praktisch unverändert. **Es ist ein eigenständiges Signal.**

### Der ganze Effekt sitzt auf einer Seite

| Zeitraum | long n | bp | t | short n | bp | t |
|---|---|---|---|---|---|---|
| Suche | 289 | −49,1 | −1,02 | 362 | **+111,3** | **3,00** |
| Holdout | 194 | −2,7 | −0,07 | 239 | **+102,5** | **2,65** |

Übersetzt: **Nach einem Bounce an einer Unterstützung geht es weiter runter.**
Nach einem Bounce an einem Widerstand passiert nichts.

Und zwar in einem Markt, der in beiden Zeiträumen **stark gestiegen** ist
(+102 % / +74 %). Der Effekt läuft also **gegen** den Drift, nicht mit ihm.

### Die entscheidende Kontrolle: Level oder nur die Vorbewegung?

Ein Unterstützungs-Bounce heißt: Der Kurs ist gefallen und hat sich knapp
gefangen. Vielleicht ist es einfach Abwärts-Fortsetzung. Kontrolle: Bars mit
**derselben Vorbewegung**, aber **ohne Level in Reichweite** (200 Ziehungen):

| Zeitraum | echt | Kontrolle (Median) | 5–95 % | **p** |
|---|---|---|---|---|
| Suche | **+111,3 bp** | −39,1 bp | −79 … −4 | **0,000** |
| Holdout | **+102,5 bp** | +3,8 bp | −30 … +33 | **0,000** |

Und ohne jede Level-Bedingung — reine Abwärts-Fortsetzung:

| Zeitraum | Vorbewegung < −1 ATR | −1 bis −0,3 ATR |
|---|---|---|
| Suche | −39,9 bp (t −1,70) | −29,8 bp (t −1,43) |
| Holdout | +16,7 bp (t 0,70) | −3,2 bp (t −0,16) |

**Es ist das Level, nicht die Bewegung.** Die Kontrolle hält in beiden
Zeiträumen mit p = 0,000.

### Pass-Rate unter den Kraken-Regeln

| Regel | 0,25× | 0,35× | 0,50× |
|---|---|---|---|
| S/R-Ausbruch | 76,8 % | **78,1 %** | 50,5 % |
| Gegen-Bounce | 63,3 % | 67,4 % | 50,8 % |
| *Zufall* | *37,5 %* | *37,5 %* | *37,5 %* |

---

## 🛑 Warum ich das trotzdem nicht als bewiesen verkaufe

| Punkt | Stand |
|---|---|
| BTC, beide Zeiträume | **stark** (+111 / +102 bp, t 3,00 / 2,65) |
| Kontrolle gegen Vorbewegung | **bestanden**, p = 0,000 zweimal |
| unabhängig vom Ausbruch | **ja**, 2 % Überschneidung |
| läuft gegen den Markttrend | **ja** — kein Drift-Effekt |
| **andere Märkte** | **schwach: 3 von 6 kippen** |
| **Bonferroni (12 Tests, t > 2,87)** | Suche 3,00 ✓, **Holdout 2,65 ✗** |
| **Asymmetrie erklärt?** | **nein** |

Auf fünf weiteren Märkten:

| | Suche | Holdout |
|---|---|---|
| ETH | +49,5 | +50,5 |
| SOL | +20,4 | +63,4 |
| BNB | +24,1 | **−33,2** |
| XRP | −4,2 | +14,9 |
| ADA | −4,9 | +85,1 |

Im Holdout sind fünf von sechs positiv (Median +57,0 bp), aber **drei von
sechs wechseln das Vorzeichen** zwischen den Zeiträumen. Die Median-t liegt
bei 1,01.

Und der unangenehmste Punkt: **Ich habe diese Daten inzwischen sehr oft
angesehen.** Dieser Befund entstand nach einer Methodikkorrektur, aus einem
bereits abgelegten Ergebnis, beim zweiten Hinsehen. Das ist genau die Lage, in
der Scheinbefunde entstehen — auch wenn die Kontrolle sauber ist.

**Dass nur die Short-Seite trägt und niemand erklären kann warum, ist das
stärkste Warnsignal.** Ein Effekt ohne Mechanismus ist ein Muster, keine
Ursache.

---

## Was daraus folgt

1. **Der S/R-Ausbruch ist besser belegt als berichtet** (t 2,16 gesamt) —
   und die Pass-Rate von **78,1 % bei 0,35×** ist die beste gemessene Zahl
   des Projekts.
2. **Der Gegen-Bounce ist ein echter Kandidat**, unabhängig vom Ausbruch, mit
   bestandener Kontrolle — aber nur auf BTC, nur short, ohne Erklärung.
3. **Beide sagen dasselbe:** Level halten nicht. Ausbrüche tragen, Bounces
   verlieren. Das ist das Gegenteil dessen, was jeder Kurs lehrt — und es ist
   ein Mechanismus, nicht zwei.
4. **Alle Indikator-Absagen bleiben.** MACD, Stochastik, Bollinger, VWAP,
   Volume Profile, Footprint, Liquidations-Karte: kein einziges Feld mit
   stabilem Vorzeichen über der Kostenschwelle.

**Der nächste Schritt ist Vorwärtstest, nicht Hochskalieren.** Ein Befund, der
beim wiederholten Hinsehen entsteht, verdient neue Daten — keine größere
Position.

---

*Skripte: `research/alles.py` (S/R und zehn Filter), `research/alles2.py`
(Indikatoren, VWAP, Volatilitätsprämie), `research/bounce.py` (sechs Märkte,
Unabhängigkeit), `research/bounce2.py` (Richtungsverteilung, Drift-Kontrolle,
Pass-Rate), `research/bounce3.py` (Kontrolle gegen die Vorbewegung).*
