# Kombination aller Signale — getestet

Vorschlag: Vielleicht braucht es die **Kombination** vieler Analysen statt
einer einzelnen Strategie.

Der Gedanke hat eine präzise Theorie hinter sich — das *Fundamental Law of
Active Management*: Bei **unkorrelierten** Signalen wächst die Information
Ratio mit der Wurzel ihrer Anzahl. Vier Signale mit IC 0,05 ergäben kombiniert
0,10.

**Ergebnis: Die Prämisse stimmt — die Signale sind fast unkorreliert. Die
Kombination macht das Ergebnis trotzdem schlechter.**

## Aufbau

Architektur wie in der Praxis üblich: **Richtung** aus dem Signal-Ensemble,
**Größe** aus Vol-Targeting.

| Signal | Quelle | gemessener Einzel-IC |
|---|---|---|
| MVRV z-Score | On-Chain (CoinMetrics) | +0,090 |
| Orderbuch-Imbalance ±5 % | Binance bookDepth | +0,036 |
| Orderflow (OFI) | Taker-Buy-Volumen | −0,025 |
| Trendfolge (50T) | Preis | +0,154 |

Gemeinsamer Zeitraum: **2023-05 bis 2026-06, 1.058 Tage.** Begrenzt durch die
Orderbuchdaten. Das sind nur **12 unabhängige 90-Tage-Fenster** — alle
Ergebnisse hier sind entsprechend unscharf.

## 1. Die Signale sind tatsächlich unkorreliert

| | mvrv | book | flow | trend |
|---|---|---|---|---|
| **mvrv** | +1,00 | +0,05 | +0,08 | +0,33 |
| **book** | +0,05 | +1,00 | +0,16 | −0,03 |
| **flow** | +0,08 | +0,16 | +1,00 | −0,03 |
| **trend** | +0,33 | −0,03 | −0,03 | +1,00 |

Mittlere paarweise Korrelation: **+0,113**. Das ist genau die Konstellation,
für die die Theorie einen Gewinn verspricht — theoretischer
Diversifikationsfaktor **1,73×** (bei perfekter Unabhängigkeit wären es 2,0×).

Anders als bei den 12 Coins (Korrelation 0,68), wo Diversifikation an der
Kopplung scheiterte, ist die Voraussetzung hier **erfüllt**.

## 2. Der IC steigt — aber nicht über das beste Einzelsignal

| Signal | IC (20 Tage) | p korrigiert |
|---|---|---|
| mvrv | +0,090 | 0,524 |
| book | +0,036 | 0,800 |
| flow | −0,025 | 0,858 |
| **trend** | **+0,154** | 0,276 |
| **KOMBI** | **+0,118** | 0,404 |

Die Kombination schlägt drei von vier Einzelsignalen — und **verliert gegen
das beste**. Der Grund ist arithmetisch: Ein gleichgewichteter Mittelwert
verwässert ein starkes Signal mit drei schwachen. Der √k-Gewinn gilt für
Signale **gleicher** Stärke; bei ungleichen Signalen zieht der Durchschnitt
nach unten.

Keiner der Werte ist signifikant (p = 0,28 bis 0,86, n_eff = 53).

## 3. Gegen die Challenge: die Kombination schadet

| Variante | Rendite | Drawdown | Pass-Rate |
|---|---|---|---|
| BTC einfach halten | +6,3 % | 16,0 % | 0,0 % |
| **nur Vol-Targeting (ohne Richtungssignal)** | +2,8 % | 7,3 % | **22,1 %** |
| mvrv × Vol-Target | −0,4 % | 6,3 % | 18,6 % |
| trend × Vol-Target | +2,4 % | 7,0 % | 13,3 % |
| book × Vol-Target | −3,6 % | 7,7 % | 0,0 % |
| flow × Vol-Target | −7,1 % | 10,4 % | 0,0 % |
| **KOMBI × Vol-Target** | +0,2 % | 6,0 % | **1,7 %** |

**Jede** Richtungsüberlagerung verschlechtert das reine Vol-Targeting. Die
Kombination aller vier ist mit 1,7 % fast das schlechteste Ergebnis der
Tabelle.

### Warum das so sein muss

Die 22 % Pass-Rate des Vol-Targetings kommen nicht aus Prognose, sondern
daraus, **im Markt zu bleiben, wenn BTC läuft** (siehe
[`volatility_targeting.md`](volatility_targeting.md): bestandene Fenster hatten
BTC-Median +52 %). Jeder Filter, der einen zeitweise aus dem Markt nimmt, senkt
die Wahrscheinlichkeit, die +10 % zu erreichen — und genau das tut ein
Richtungssignal mit IC 0,1.

Ein IC von 0,1 heißt: In etwa 55 von 100 Fällen liegt das Signal richtig. Für
einen Fonds, der tausende Wetten eingeht, ist das Geld. Für **ein**
90-Tage-Fenster mit hartem Drawdown-Limit ist es fast wertlos — die 45 %
Fehlsignale kosten Marktzeit, die man braucht.

## Fazit

Die Idee war methodisch richtig, und die Voraussetzung war sogar erfüllt: Die
Signale sind fast unkorreliert (ρ = 0,11), anders als die 12 Coins (ρ = 0,68).

Sie scheitert an zwei Stellen:

1. **Der Durchschnitt verwässert.** Gleichgewichtete Mittelung von vier
   ungleich starken Signalen liefert weniger als das beste allein
   (+0,118 gegen +0,154).
2. **Die Challenge belohnt keinen IC.** Sie belohnt das Verhältnis
   Rendite/Drawdown in einem einzelnen 90-Tage-Fenster. Ein besserer IC
   verbessert dieses Verhältnis nicht — er verbessert die *durchschnittliche*
   Trefferquote über viele Wetten, und dafür ist kein Platz.

**Das reine Vol-Targeting bleibt mit 22 % das Beste.** Es ist kein Signal,
sondern die Abwesenheit eines Signals plus Risikokontrolle — und genau deshalb
funktioniert es besser als alles, was ich obendrauf gelegt habe.

*Einschränkung: 1.058 Tage sind 12 unabhängige 90-Tage-Fenster. Die Rangfolge
ist deutlich, die einzelnen Prozentwerte sind es nicht.*
