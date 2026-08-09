# Volatilitäts-Targeting und Smart DCA — das beste gefundene Ergebnis

Nach sechs erfolglosen Ideen war dies der erste Ansatz, der die **richtige
Größe** angreift: nicht die Rendite, sondern den **Drawdown**.

## Die Idee

Position **invers zur Volatilität** skalieren — klein in wilden Phasen, groß in
ruhigen. Das erzeugt keine Rendite, senkt aber gezielt den Drawdown. Da die
Challenge an einem 6-%-Drawdown-Limit scheitert und nicht am Renditeziel, setzt
das genau am Engpass an.

## Ergebnis (BTC, 4 Jahre, 138 Fenster à 90 Tage, 16 bp Kosten)

| Ansatz | 90T-Rendite | 90T-Drawdown | Pass-Rate |
|---|---|---|---|
| BTC einfach halten | +6,8 % | 18,5 % | **1 %** |
| Smart DCA (Faktor 3) | +8,4 % | 13,7 % | 11 % |
| **Vol-Target 20 % / 30T** | +2,5 % | 8,7 % | **21 %** |
| Vol-Target 15 % + Trendfilter | +0,4 % | 4,1 % | 25 % |

Vol-Targeting halbiert den Drawdown (18,5 % → 8,7 %), während die Rendite
weniger stark fällt. Das vervielfacht die Pass-Rate gegenüber Buy-and-Hold.

## Der Out-of-Sample-Test trennt Fund von Überanpassung

Nach ~80 getesteten Kombinationen ist Überanpassung die Hauptgefahr. Test:
Parameter auf der ersten Hälfte gewählt, auf der zweiten geprüft.

| Variante | 1. Hälfte | 2. Hälfte | Urteil |
|---|---|---|---|
| Vol 15 % + Trend 50T (der „beste") | 41 % | 14 % | **bricht ein** |
| Vol 15 % / 30T | 36 % | 14 % | **bricht ein** |
| **Vol-Target 20 % / 30T** | 20 % | **25 %** | **hält** |
| BTC halten | 2 % | 0 % | — |

Bezeichnend: Was hält, ist die Variante, die **nicht** auf das Optimum getunt
wurde. Die getunten Varianten brechen sämtlich ein.

## Was die 20–25 % wirklich sind

| | BTC-Rendite im Fenster |
|---|---|
| **Bestandene** Fenster | **+52,4 %** (Median) |
| Gescheiterte Fenster | −3,1 % (Median) |

**Man besteht, wenn BTC von selbst rund 50 % läuft.** Vol-Targeting erzeugt
keine Rendite — es sorgt nur dafür, dass der Drawdown einen nicht vorher
hinauswirft.

> **Das ist Risikokontrolle, kein Edge.** Die Rendite kommt vom Markt, nicht von
> der Strategie. Wer so handelt, macht eine **Beta-Wette auf BTC** mit
> kontrolliertem Risiko — kein systematisches Verfahren.

## Ehrliche Einordnung

**Was es ist:** Der beste gefundene Ansatz. Pass-Rate ~20–25 % statt 1 %, und
er hält out-of-sample. Bei 85 $ je Challenge entspricht das erwarteten ~340 $
bis zum Bestehen.

**Was es nicht ist:** Eine Strategie mit Edge. Der Erfolg hängt davon ab, ob BTC
in den nächsten 90 Tagen läuft — das ist Marktrichtung, nicht Können. In einem
Bärenmarkt fällt die Pass-Rate gegen null, weil das Renditeziel unerreichbar
wird (nicht weil man bustet).

**Smart DCA** landet mit 11 % dazwischen und behält mehr Rendite (+8,4 % Median),
bezahlt das aber mit höherem Drawdown (13,7 %). Für das Ziel „nicht busten" ist
Vol-Targeting die bessere Wahl.

## Praktisch

Wer die Challenge damit angeht, sollte wissen:

1. Es ist eine **gerichtete Wette auf BTC** mit gutem Risikomanagement
2. Erfolgswahrscheinlichkeit je Versuch: **~20–25 %**, abhängig vom Marktregime
3. In Seitwärts- und Bärenphasen ist das Ziel schlicht nicht erreichbar —
   dann besser gar nicht handeln, statt Gebühren zu zahlen
4. Konkret: Positionsgröße = `Zielvola 20 % / realisierte 30-Tage-Vola`,
   Obergrenze 2×, täglich nachjustieren
