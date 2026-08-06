# Mehrere Kraken-Challenges — aber nicht gleichzeitig

Bei Kraken kostet ein Versuch **85 $**. Mehrere gleichzeitig sind erlaubt.
Damit ist die Frage aus [`parallel.md`](parallel.md) hier tatsächlich
umsetzbar — nur mit einem entscheidenden Unterschied im Ergebnis.

Alle Zahlen: BTC 1h, ≥6 Berührungen, eine Position, 48 h, 0,35×, korrigierte
Kosten (16 bp je Roundtrip), identische Startfenster für alle Bauformen.

---

## Das Kernergebnis: gleichzeitig bringt nichts, versetzt bringt alles

| Versatz der Startzeitpunkte | **≥1 gefunded** | Ø Konten (von 3) | $ je gefundetem Konto |
|---|---|---|---|
| **0 / 0 / 0 (gleichzeitig)** | **70,9 %** | 2,13 | 120 $ |
| 0 / 30 / 60 Tage | 79,3 % | 2,17 | 117 $ |
| **0 / 60 / 120 Tage** | **92,7 %** | 2,31 | 111 $ |
| **0 / 90 / 180 Tage** | **~100 %** | 2,38 | **107 $** |
| 0 / 120 / 240 Tage | ~100 % | 2,33 | 109 $ |

**Zum Vergleich: eine einzelne Challenge schafft 70,9 %.**

Drei Challenges, die du **am selben Tag** startest, schaffen ebenfalls
**70,9 %**. Nicht 71,1 %, nicht 72 % — exakt dieselbe Zahl.

> **Drei gleichzeitige identische Challenges sind drei Lottoscheine mit
> denselben Zahlen.** Sie bestehen oder scheitern zusammen. Du zahlst 255 $
> statt 85 $ und kaufst dir null zusätzliche Sicherheit.

Mit **90 Tagen Versatz** dagegen: von 70,9 % auf praktisch 100 %, dass
mindestens eines durchkommt.

---

## Warum der Versatz wirkt und die Kontenzahl nicht

Das ist derselbe Mechanismus wie bei den Verfallszyklen in
[`parallel.md`](parallel.md), nur auf einer anderen Zeitskala.

Der Grund, warum die S/R-Strategie scheitert, ist fast immer ein
**Marktregime** — eine zerhackte Phase, in der Ausbrüche systematisch
zurückfallen. Ein solches Regime dauert Wochen bis Monate. Drei Versuche, die
am selben Tag starten, erleben **dasselbe** Regime. Drei Versuche mit 90 Tagen
Abstand erleben **drei verschiedene**.

Genau das misst die Tabelle: Der Versatz kauft dir Unabhängigkeit, die
zusätzliche Konten allein nicht liefern können.

---

## Wie viele lohnen sich?

Versatz 60 Tage, BTC 0,35×:

| Anzahl | Einsatz | ≥1 gefunded | Ø Konten | $ je Konto |
|---|---|---|---|---|
| 1 | 85 $ | 70,9 % | 0,71 | 120 $ |
| 2 | 170 $ | 79,7 % | 1,46 | 116 $ |
| **3** | **255 $** | **92,7 %** | **2,31** | **111 $** |
| 4 | 340 $ | ~100 % | 3,18 | 107 $ |
| 5 | 425 $ | ~100 % | 4,00 | 106 $ |

Ab drei bis vier Konten flacht der Zugewinn bei „mindestens eines" ab — die
Kosten je Konto sinken danach nur noch marginal. **Drei ist der Punkt, an dem
der Sprung passiert.**

---

## Andere Bauformen, die ich geprüft habe

| Bauform | ≥1 gefunded | Ø Konten | je Konto |
|---|---|---|---|
| 3× identisch, gleichzeitig | 70,9 % | 2,13 | 70,9 % |
| 3× BTC, **verschiedene Größen** (0,25/0,35/0,5) | 74,3 % | 1,98 | 65,9 % |
| 3× **verschiedene Assets** (BTC/ETH/SOL) | 87,2 % | 1,62 | **54,2 %** |
| **3× BTC, versetzt** | **92,7–100 %** | **2,31–2,38** | **76,9–79,2 %** |

**Verschiedene Assets streuen zwar** (87,2 % statt 70,9 %), **kosten aber
Qualität**: ETH und SOL tragen die Strategie deutlich schlechter, die Quote je
Konto fällt auf 54,2 %. Du kaufst Diversifikation mit einem schwächeren Edge.

**Verschiedene Größen bringen fast nichts** — die Regime-Korrelation bleibt.

**Der Versatz ist die einzige Bauform, die streut, ohne Qualität zu kosten.**

---

## Was das praktisch heißt

```
NICHT:  drei Challenges heute kaufen und alle heute starten.
SONDERN: eine starten. Nach 60-90 Tagen die zweite. Nach weiteren
         60-90 Tagen die dritte -- unabhaengig davon, wie die
         erste laeuft.

Einsatz  255 $ ueber ein halbes Jahr verteilt
Ergebnis ~93-100 % Wahrscheinlichkeit, mindestens ein Konto zu bekommen
         Ø 2,3 von 3 Konten
         ~110 $ je gefundetem Konto
```

Und der Punkt, der leicht untergeht: **Du musst nicht warten, bis eine
Challenge scheitert.** Läuft die erste noch, startest du die zweite trotzdem.
Genau das unterscheidet diese Bauform von den sequentiellen Mehrfachversuchen
in [`spielregeln.md`](spielregeln.md) — dort wartete man auf das Ergebnis und
brauchte im Median 107–133 Tage je Anlauf.

---

## Die Einschränkungen

**1. Die 100 % sind zu glatt.** Über 5,4 Jahre und 90-Tage-Versatz bleiben
effektiv nur eine Handvoll unabhängiger Beobachtungen. Lies die Zeile als
„sehr hoch, vermutlich 90–98 %", nicht als Garantie.

**2. Die Quote je Konto (70,9 % → 79,2 %) ist teilweise ein
Zensierungseffekt.** Später startende Konten haben weniger Restdaten und
fallen häufiger aus der Auswertung. Die belastbare Zahl ist **≥1 gefunded**,
nicht die Quote je Konto.

**3. Die 70,9 % für ein einzelnes Konto sind höher als die 53,8 % aus
[`einfach.md`](einfach.md)** — weil hier ein 365-Tage-Deckel gilt und
unaufgelöste Versuche herausfallen statt als Fehlschlag zu zählen. Für den
Vergleich *zwischen* den Bauformen ist das egal, für die absolute Höhe nicht.
**Rechne mit dem konservativeren Wert.**

**4. Kraken muss mitspielen.** Kläre, ob mehrere gleichzeitige Challenges auf
denselben Namen erlaubt sind und ob identischer Handel über Konten hinweg
beanstandet wird. Bei 90 Tagen Versatz und derselben öffentlichen Regel ist
das unkritischer als simultanes Spiegeln — aber gefragt werden sollte es.

**5. Auf dem gefundeten Konto ändert sich nichts.** Mehr Challenges heißt mehr
Einstiegs­chancen, nicht mehr Ertrag je Konto. Was danach kommt, steht in
[`trading_as_job.md`](trading_as_job.md).

---

*Skripte: `research/kraken_parallel.py` (vier Bauformen),
`research/kraken_parallel2.py` (Kontrolle identischer Startfenster,
optimaler Abstand, Kontenzahl).*
