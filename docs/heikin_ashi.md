# Heikin Ashi — getestet, und eine Warnung

Vorschlag: Heikin-Ashi-Kerzen ausprobieren.

**Ergebnis: HA bringt nichts. Wichtiger ist, was der Test nebenbei zeigt — eine
Abrechnungsfalle, die auf jedem geprüften Asset aus einer verlierenden
Strategie eine scheinbar profitable macht.**

## Die Falle

```
HA_close = (open + high + low + close) / 4
```

Das ist **kein handelbarer Preis**. Man kann nicht zum HA-Schluss kaufen — es
ist ein Mittelwert der echten Kerze. Wer Signale auf HA berechnet und den
Gewinn dann ebenfalls mit HA-Preisen misst, rechnet sich reich.

Getestet wurde deshalb sauber: **Signal auf HA, Fill zum echten Schlusskurs.**
Zum Vergleich daneben dieselben Trades mit HA-Preisen abgerechnet.

| Asset | HA-Trendfolge, **echt** | mit **HA-Preisen** | Verzerrung |
|---|---|---|---|
| BTC | −7,8 bp | **+14,5 bp** | +22,3 bp |
| ETH | −6,4 bp | **+19,9 bp** | +26,3 bp |
| SOL | +3,3 bp | **+43,4 bp** | +40,1 bp |
| XRP | −2,4 bp | **+23,0 bp** | +25,4 bp |

**Auf allen vier Assets kippt das Vorzeichen.** Die Verzerrung beträgt 22 bis
40 Basispunkte — mehr als die gesamte Kostenschwelle von 16 bp. Das ist
dieselbe Klasse von Fehler wie der Look-ahead-Bias in
[`realism.md`](realism.md): Er entsteht nicht aus Absicht, sondern daraus, dass
die Größe, auf der man rechnet, nicht die Größe ist, die man handelt.

## Die drei Anwendungen

Alle sauber abgerechnet, BTC-Suchzeitraum:

| Variante | Ereignisse | Effekt 24 h | Pass 0,5× |
|---|---|---|---|
| **Referenz: Level auf echten Kerzen** | 474 | **+37,9 bp** | **49,3 %** |
| Level auf HA-Kerzen gebaut | 418 | +36,4 bp | 45,3 % |
| echte Level + HA-Richtungsfilter | 360 | +30,7 bp | 44,6 % |
| klassische HA-Trendfolge (Farbwechsel) | 8.861 | **−7,8 bp** | **0,0 %** |

HA glättet, aber es fügt keine Information hinzu — es ist eine Transformation
derselben OHLC-Daten mit Verzögerung. Level auf HA-Kerzen sind minimal
schlechter, der Richtungsfilter entfernt mehr gute als schlechte Signale, und
die klassische Farbwechsel-Strategie verliert (wie jede andere Trendfolge in
dieser Untersuchung).

## Der eigentlich wichtige Befund dieses Laufs

Für den Test wurden zwei **nie verwendete** Assets geladen (SOL, XRP), weil der
BTC-Holdout nach vier Nutzungen verbraucht ist. Die Referenzzeile darin ist
folgenreicher als alles zu Heikin Ashi:

| Asset | Effekt 24 h | p | Pass 0,5× |
|---|---|---|---|
| BTC | +37,9 bp | 0,053 | 49,3 % |
| ETH | +33,5 bp | 0,081 | 26,7 % |
| **SOL** | **+18,8 bp** | 0,382 | 20,0 % |
| **XRP** | **−11,3 bp** | 0,556 | 22,5 % |

**Der S/R-Ausbruch trägt nur auf BTC und ETH** — genau den beiden Assets, auf
denen er entwickelt und zuerst geprüft wurde. Auf SOL halbiert sich der Effekt
und verliert jede Signifikanz; auf XRP ist er nicht vorhanden (nicht
signifikant negativ — schlicht weg).

Das schwächt den bisher stärksten Chartmuster-Fund dieser Untersuchung
erheblich. Vier Assets, zwei davon tragen. Ein Effekt, der nur auf den
Entwicklungsdaten funktioniert, ist genau das, wovor die ganze Methodik
schützen soll.

Beachtenswert ist auch, dass XRP mit **22,5 % Pass-Rate** dasteht, obwohl der
Effekt je Ereignis **negativ** ist. Die Pass-Rate lebt in erheblichem Maß vom
Marktdrift, nicht vom Signal — eine Erinnerung daran, dass sie als alleiniger
Maßstab täuscht.

## Praktische Folge

An der Handelsregel ändert sich nichts, aber die Erwartung muss nach unten:
Die BTC-Zahlen (+37,9 bp, ~49 % Pass-Rate) sind der **obere Rand**, nicht der
Erwartungswert. Über vier Assets gemittelt bleibt deutlich weniger.
