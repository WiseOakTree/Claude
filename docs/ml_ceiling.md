# Bringt Machine Learning etwas? — die Obergrenze, ohne ein Modell zu trainieren

Die Frage nach neun gescheiterten Ideen: Wenn selbst gute Strategien die
Challenge nicht bestehen, kann ML dann überhaupt helfen?

**Methode: Orakel-Modelle.** Statt Modelle zu trainieren und über
Überanpassung zu streiten, simuliere ich Modelle, die **schummeln** — die die
Zukunft mit einstellbarer Genauigkeit kennen. Was ein Orakel nicht schafft,
schafft auch das beste ML nicht. Das gibt die Obergrenze als Zahl.

## A) Volatilitätsprognose: **keine Luft nach oben**

Das war meine Erwartung für den einen Bereich, in dem ML zuverlässig gut ist —
und in dem [`required_edge.md`](required_edge.md) gezeigt hat, dass die
Positionsgröße wichtiger ist als der Edge.

| Schätzer für die Positionsgröße | Median | Drawdown | Pass-Rate |
|---|---|---|---|
| trailing 30 Tage (heute genutzt) | +0,2 % | 7,4 % | **20,7 %** |
| DVOL implizit (Marktprognose) | +0,4 % | 6,7 % | 18,2 % |
| **ORAKEL: perfekte Vol-Prognose** | +1,9 % | 6,4 % | **20,7 %** |

**Eine perfekte Volatilitätsprognose liefert exakt dieselbe Pass-Rate wie ein
simpler 30-Tage-Durchschnitt.** Sie verbessert die Rendite (+1,9 % statt
+0,2 %) und senkt den Drawdown leicht — aber die Pass-Rate bewegt sich um
keinen Prozentpunkt.

Der Grund: Volatilität ist stark autokorreliert. Der gestrige Wert ist bereits
ein guter Schätzer für den morgigen; der Rest ist Rauschen, das die
Positionsgröße kaum verschiebt. **Für diesen Anwendungsfall ist ML sinnlos —
nicht weil es zu schwach wäre, sondern weil das Problem gelöst ist.**

## B) Richtungsprognose: **sehr viel Luft — die niemand erreicht**

| Trefferquote (täglich) | Median | Drawdown | Pass-Rate |
|---|---|---|---|
| 50 % (reiner Zufall) | −5,7 % | 11,1 % | 1,4 % |
| 52 % | −3,9 % | 9,9 % | 3,5 % |
| 55 % | −0,7 % | 8,4 % | 8,6 % |
| **60 %** | +5,6 % | 6,2 % | **23,6 %** |
| **70 %** | +17,8 % | 4,2 % | **57,8 %** |
| 80 % | +31,5 % | 3,0 % | 78,7 % |
| 100 % | +63,1 % | 0,1 % | 100,0 % |

Hier ist die Obergrenze riesig. Aber zwei Zahlen setzen sie ins Verhältnis:

1. **Bei 60 % Trefferquote erreicht man 23,6 % — also genau das, was
   Vol-Targeting mit *null* Prognose schon liefert (20,7 %).** Ein Modell muss
   in 6 von 10 Fällen die Tagesrichtung richtig treffen, nur um mit dem
   Nichtstun gleichzuziehen.
2. **Für eine 50-%-Quote braucht es rund 68–70 %.**

## C) Was die gemessenen Signale tatsächlich liefern

Alle in dieser Untersuchung gefundenen Signale lagen bei **IC 0,03 bis 0,15** —
das entspricht einer Trefferquote von etwa **51 bis 58 %**. In der Tabelle
oben: **1,4 bis 8,6 % Pass-Rate.** Schlechter als Vol-Targeting ohne jede
Prognose.

Und keines dieser Signale hielt out-of-sample:

| Signal | in-sample | out-of-sample |
|---|---|---|
| DVOL z-Score | IC +0,276 | **−0,004** |
| Orderbuch, 3 Tage | +110 bp | **−33 bp** |
| Ausbruch + Volumen | 20,8 % Pass | **6,3 %** |
| MVRV | p = 0,037 | fällt bei Bonferroni |

## Warum ML hier eher schadet als hilft

Die Untersuchung enthält den Beweis am eigenen Material: Mein erster
Backtester zeigte **93 % Pass-Rate**. Der gesamte Effekt war ein
Look-ahead-Bug von 0,34 % je Trade
([`realism.md`](realism.md)) — nach der Korrektur blieben 7 %.

Ein lineares Modell mit fünf Parametern hat diesen Fehler produziert. Ein
Gradient-Boosting-Modell mit tausenden Splits findet solche Artefakte
**zuverlässiger**, nicht seltener — es hat mehr Kapazität, Rauschen als Struktur
zu lernen. Die vier Zeilen der Tabelle oben zeigen dasselbe Muster bereits bei
einfachsten Methoden.

Dazu kommt: 1.265 bis 5.100 Tagesbeobachtungen sind für ein Modell mit vielen
Parametern eine sehr kleine Stichprobe. Auf 90-Tage-Sicht sind es
**12 bis 55 unabhängige Fenster**.

## Fazit

Die Vermutung „dann bringt ML auch nichts" trifft zu — aber der genaue Grund
ist wichtiger als die Antwort:

| Anwendungsfall | Obergrenze | Urteil |
|---|---|---|
| **Volatilitätsprognose** | perfekt = heute (20,7 %) | **kein Nutzen möglich** |
| **Richtungsprognose** | 70 % Treffer → 58 % Pass | Nutzen möglich, aber unerreichbar |

Bei der Volatilität ist ML nutzlos, weil das Problem **bereits gelöst** ist.
Bei der Richtung wäre es enorm nützlich — man bräuchte nur **60 % tägliche
Trefferquote, um mit Nichtstun gleichzuziehen**, und 70 % für eine
50-%-Erfolgsquote. Die besten hier gemessenen Signale lagen bei 51–58 %, und
keines war stabil.

**ML ist ein Werkzeug zur Extraktion von Information, kein Ersatz für sie.**
Neun Untersuchungen haben gezeigt, dass die Information in frei zugänglichen
BTC-Daten für dieses Ziel nicht ausreicht — und genau das würde ein Modell
ebenfalls vorfinden, nur mit deutlich höherem Risiko, das Fehlen von Struktur
für Struktur zu halten.
