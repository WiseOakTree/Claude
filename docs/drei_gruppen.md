# Indikator gegen Bauchgefühl gegen Zufall

Aufbau vorab festgelegt und committet
([`dreigruppen_spec.md`](dreigruppen_spec.md)). Gemeinsamer Maßstab:
**Basispunkte je Trade nach Kosten**, 14 Märkte, 1 h, 48 h Halten, 16 bp je
Roundtrip.

**Ergebnis: 1 ≈ 2 ≈ 3. Kruskal-Wallis p = 0,5971.**

---

## Die vier Gruppen

| Gruppe | n | Median | 25 % | 75 % |
|---|---|---|---|---|
| **1 Indikator-Trader** (Regeln) | 24 | **−15,18** | −18,88 | −10,53 |
| **2a Bauchgefühl** (Heuristiken) | 10 | **−2,70** | −28,35 | +15,55 |
| **3 Zufall** | 60 | **−15,30** | −19,46 | −8,23 |
| *2b Bauchgefühl (echte Menschen)* | *15.776* | *+5,36* | *−18,40* | *+105,73* |

## Der vorab festgelegte Test

| | |
|---|---|
| Kruskal-Wallis über 1, 2a, 3 | **H = 1,031, p = 0,5971** |
| **Urteil** | **1 = 2 = 3, nicht unterscheidbar** |

Paarweise, Holm-korrigiert:

| Vergleich | p roh | p Holm | Urteil |
|---|---|---|---|
| Indikator gegen Bauchgefühl | 0,3744 | 0,7488 | **nicht unterscheidbar** |
| Indikator gegen Zufall | 0,7476 | 0,7476 | **nicht unterscheidbar** |
| Bauchgefühl gegen Zufall | 0,3603 | 1,0000 | **nicht unterscheidbar** |

> **Zwischen einer Indikatorregel, einer Bauchentscheidung und einem Münzwurf
> besteht kein messbarer Unterschied im Ergebnis je Trade.**

---

## Die einzelnen Bauchgefühl-Heuristiken

| Heuristik | Trades | bp |
|---|---|---|
| „fühlt sich nach Breakout an" | 6.729 | **+52,27** |
| „läuft heiß" (drei grüne Tage) | 72.639 | +37,28 |
| „ist überverkauft" | 84.698 | +15,95 |
| „war ruhig, jetzt geht's los" | 11.787 | +14,34 |
| „sieht bullish aus" | 328.969 | +0,98 |
| „große Kerze" | 129.712 | −6,37 |
| „runde Zahl" | 15.784 | −25,00 |
| „sieht bearish aus" | 331.098 | −29,47 |
| „fällt ins Messer" | 73.646 | −35,45 |
| „ist überkauft" | 85.621 | **−60,87** |

### 🛑 Und ein Look-ahead in meinem eigenen Code

Der erste Lauf zeigte „läuft heiß" bei **+176,10 bp** und „fällt ins Messer"
bei **+116,15 bp**. Beide benutzen Tageskerzen. Mein Code hat die
Tagesbedingung per `reindex(method="ffill")` auf alle Stunden desselben Tages
verteilt — **damit kannte die Stunde 01:00 bereits den Schluss um 23:00.**

| | mit Look-ahead | korrigiert |
|---|---|---|
| „läuft heiß" | +176,10 | **+37,28** |
| „fällt ins Messer" | +116,15 | **−35,45** (Vorzeichen kippt) |

Das ist die **neunte** Falle dieses Projekts, wieder im eigenen Material.

---

## Gruppe 2b: echte Menschen — und warum sie scheinbar gewinnen

15.776 on-chain verifizierte Hyperliquid-Konten mit über 1 Mio $ Volumen.
Median **+5,36 bp**, unterscheidbar vom Zufall (p < 0,0001).

**Das löst sich beim Hinschauen auf.** Nach Umschlag (Volumen ÷ Kontowert):

| Umschlag | n | Median bp | Anteil > 0 |
|---|---|---|---|
| **unter 5×** (kaum gehandelt) | 692 | **+1.736,14** | 80,6 % |
| 5–25× | 1.928 | +323,83 | 75,0 % |
| 25–100× | 2.088 | +114,55 | 74,7 % |
| 100–1.000× | 4.557 | +13,32 | 61,7 % |
| **über 1.000×** (Vieltrader) | 6.511 | **−6,72** | **36,1 %** |

**Ein perfekt monotoner Verlauf: Je mehr jemand handelt, desto schlechter das
Ergebnis je gehandeltem Dollar.**

Die Konten mit dem besten Wert sind die, die **fast nicht gehandelt** haben —
bei ihnen misst PnL ÷ Volumen den Kursanstieg, nicht die Handelsleistung. Wer
2023 einmal gekauft und gehalten hat, steht mit +1.736 bp in der Statistik.

Bleiben die echten Vieltrader: **Median −1,98 bp**, nur 36,1 % im Plus.

Zum verbleibenden Abstand zum Zufall (−15,30 bp): Hyperliquid nimmt deutlich
niedrigere Gebühren als die 16 bp, die ich der Zufallsgruppe aufgebürdet habe.
**Der Abstand entspricht ungefähr dem Gebührenunterschied**, nicht einem
Können.

---

## Was diese Untersuchung nicht kann

- **Gruppe 2a hat nur 10 Mitglieder.** Der Kruskal-Wallis-Test hat gegen sie
  wenig Trennschärfe. „Nicht unterscheidbar" heißt hier auch: *mit zehn
  Heuristiken ließe sich ein mittelgroßer Unterschied nicht nachweisen.*
- **Bauchgefühl bleibt eine Modellierung.** Zehn Heuristiken sind nicht
  dasselbe wie ein Mensch, der auf einen Chart schaut. Sie sind der Versuch,
  Wahrnehmung statt Rechnung abzubilden — mehr nicht.
- **Gruppe 2b hat Überlebensauswahl.** Geschlossene Nullkonten fehlen; die
  echte Verteilung liegt tiefer.
- **Unterschiedliche Kostenbasis** zwischen 2b und den übrigen Gruppen.

---

## Die Aussage

| Frage | Antwort |
|---|---|
| Schlagen Indikatoren den Zufall? | **nein** (p = 0,7476) |
| Schlägt Bauchgefühl den Zufall? | **nein** (p = 1,0000 nach Holm) |
| Schlagen Indikatoren das Bauchgefühl? | **nein** (p = 0,7488) |
| Schlagen echte Vieltrader den Zufall? | nur um den Gebührenunterschied |
| Was schlägt alles? | **weniger handeln** — der Umschlag-Gradient |

Und die Zahl, die das Ganze zusammenfasst: Von 24 Indikatorregeln liegen
**4 %** über null, von 10 Heuristiken 50 %, von 60 Zufallsvarianten 15 % —
und alle drei Verteilungen überlappen sich so weit, dass kein Test sie
trennt.

> **Der Chart, auf den der Indikator-Trader und der Bauchgefühl-Trader
> schauen, enthält für beide dasselbe: nichts, was ein Münzwurf nicht auch
> hätte.**

---

*Skripte: `research/dreigruppen.py` (Heuristiken, drei Gruppen),
`research/dreigruppen2.py` (Kruskal-Wallis, Holm, echte Menschen).
Spezifikation: [`dreigruppen_spec.md`](dreigruppen_spec.md), committet vor
der Rechnung.*
