# The Retail Trading Reality Check

Systematische Untersuchung der Frage:

> **Ist der durchschnittliche Privatanleger in der Lage, aus öffentlich
> verfügbaren Informationen einen nach Kosten reproduzierbaren Vorteil zu
> erzeugen — und gibt es Anlageklassen, in denen das eher gelingt als in
> anderen?**

Krypto ist Anlageklasse #1 und methodische Grundlage
([`../PAPER.md`](../PAPER.md)). Dieses Verzeichnis erweitert die Untersuchung
auf Aktien, Devisen, Rohstoffe und Zinsen.

---

## 🛑 Zuerst: was von hier aus NICHT geht

Bevor irgendetwas gerechnet wird, die Grenzen der Datenlage. Ich habe
geprüft, nicht vermutet.

| Gewünscht | Status | Grund |
|---|---|---|
| **Point-in-time-Universen** (S&P-500-Mitgliedschaft nach Datum) | ❌ **nicht beschaffbar** | erfordert CRSP/Compustat oder gleichwertig — kostenpflichtig, nicht öffentlich |
| **Einzelaktien** | ❌ | Stooq liefert eine JavaScript-Sperre, Yahoo antwortet mit 429 |
| **ETFs** (SPY, QQQ, IWM einzeln) | ❌ | dieselben Quellen |
| **Futures** (Kontrakte, Rollrenditen) | ❌ | keine erreichbare freie Quelle |
| **Fundamentaldaten** (Value, Quality) | ❌ | dito |

**Damit ist der von dir zu Recht als wichtigste Erweiterung benannte Punkt —
Survivorship Bias über Point-in-time-Universen — von hier aus nicht lösbar.**

Das ist keine Nachlässigkeit, sondern eine harte Grenze. Was es bedeutet:

- Die Untersuchung kann **keine Aussage über Einzelaktienstrategien** treffen.
- Sie kann Aussagen über **Indizes, Devisen, Rohstoffe und Zinsen** treffen —
  dort existiert das Problem in dieser Form nicht, weil ein Index oder ein
  Währungspaar nicht „aus dem Universum fällt".
- Der Survivorship-Bias verschiebt sich damit von der Wertpapierebene auf die
  **Marktebene**: Auch Währungen können verschwinden (DEM, FRF), und die
  Auswahl der Indizes ist nicht neutral. Das wird dokumentiert, nicht gelöst.

Wer den vollständigen Test will, braucht einen bezahlten Datenzugang. Was
dafür nötig wäre, steht in [`specs/datenbedarf.md`](specs/datenbedarf.md).

---

## Was geht: 36 Instrumente, fünf Anlageklassen

| Klasse | Instrumente | Frequenz | Historie |
|---|---|---|---|
| **Krypto** | 14 (BTC, ETH, SOL, BNB, XRP, ADA, ATOM, AVAX, BCH, DOGE, DOT, LINK, LTC, TRX) | 1 h | 2021–2026 |
| **Aktienindizes** | 3 (S&P 500, Nasdaq Composite, Nikkei 225) | täglich | **ab 1949** |
| **Devisen** | 13 (EUR, GBP, AUD, JPY, CAD, CHF, MXN, KRW, INR, BRL, SEK, NOK, CNY) | täglich | **ab 1971** |
| **Rohstoffe** | 3 (WTI, Brent, Erdgas) | täglich | ab 1986 |
| **Zinsen** | 3 (2J, 10J, 30J Treasury) | täglich | **ab 1962** |

Die Tiefe ist der eigentliche Gewinn: **55 Jahre Devisen und 64 Jahre Zinsen**
gegenüber 5,4 Jahren Krypto. Damit lässt sich Regimestabilität prüfen, die im
Krypto-Paper nicht prüfbar war.

---

## Die vier Ebenen

| Ebene | Inhalt | Stand |
|---|---|---|
| **A — Technisch** | 25 kanonische Regeln (RSI, MACD, Bollinger, Keltner, Donchian, …) | ✅ liegt vor |
| **B — Faktoren** | Zeitreihen-Momentum, Trendfolge, Querschnitts-Momentum, Low-Vol, Carry | ⚠️ teilweise (Value/Quality nicht möglich) |
| **C — Intuition** | 10 Heuristiken menschlicher Chartwahrnehmung | ✅ liegt vor |
| **D — Zufall** | zirkulär verschobene Signale, alles andere identisch | ✅ liegt vor |

---

## Die Zielmatrix

| Anlageklasse | A Technisch | B Faktoren | C Intuition | D Zufall | Edge? |
|---|---|---|---|---|---|
| Krypto | −15,18 bp | ? | −2,70 bp | −15,30 bp | ❌ |
| Aktienindizes | ? | ? | ? | ? | ? |
| Devisen | ? | ? | ? | ? | ? |
| Rohstoffe | ? | ? | ? | ? | ? |
| Zinsen | ? | ? | ? | ? | ? |

---

## Methodische Standards (unverändert aus dem Krypto-Paper)

1. **Vorregistrierung** — Regeln, Parameter und Urteilskriterium werden vor
   der Rechnung committet
2. **Kanonische Parameter** — keine Optimierung, keine Suche
3. **Kosten** — je Anlageklasse realistisch, siehe Spezifikation
4. **Zirkuläres Nullmodell** — erhält Anzahl, Richtung und Clusterstruktur
5. **Reality Check nach White** — Mehrfachtests im Instrument, nicht danach
6. **Einzigartigkeitskorrektur** bei überlappenden Haltedauern
7. **Zeitliche Teilung** — jede Anlageklasse in Hälften, Vorzeichenstabilität
8. **Eichung an eingebautem Vorteil** — vor der ersten Anwendung

Und der Fehlerkatalog aus dem Krypto-Paper (neun dokumentierte Fallen) gilt
als Prüfliste für jeden neuen Test.

---

## Verzeichnis

```
rtrc/
  data/        heruntergeladene Reihen (22 FRED + Verweis auf Krypto)
  specs/       Vorregistrierungen -- committet VOR den Ergebnissen
  research/    Skripte
  docs/        Ergebnisse
```

## Stand

| | |
|---|---|
| Daten beschafft | ✅ 22 FRED-Reihen + 14 Krypto |
| Datenbedarf dokumentiert | ✅ |
| Vorregistrierung | ⏳ in Arbeit |
| Ebene A auf allen Klassen | ⏳ |
| Ebene B | ⏳ |
| Ebene C/D | ⏳ |
