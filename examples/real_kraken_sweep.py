"""Robustheits-Sweep auf ECHTEN Kraken-Daten ueber mehrere Coins.

Holt fuer eine Liste von Paaren die aktuellen OHLC-Daten von Kraken (je bis zu
~720 Kerzen) und laesst den Parameter-Sweep ueber alle Paare als eigenstaendige
Szenarien laufen. So bekommst du Robustheit auf realen Daten, ohne monatelange
Trade-Historie herunterladen zu muessen -- jeder Coin ist ein realer Markt.

Voraussetzung: ausgehender Zugriff auf api.kraken.com (Netzwerk-Policy "Full"
oder "Custom" mit api.kraken.com).

Ausfuehren aus dem Projekt-Root:
    python examples/real_kraken_sweep.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prop_backtester import data, run_sweep, DEFAULT_GRID  # noqa: E402
from prop_backtester.report import format_sweep  # noqa: E402

PAIRS = ["XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD", "ADAUSD", "DOGEUSD",
         "LTCUSD", "LINKUSD"]
INTERVAL_MINUTES = 60
PRESET = "1step_classic"


def main() -> None:
    scenarios = []
    for pair in PAIRS:
        try:
            df = data.fetch_kraken_ohlc(pair, interval_minutes=INTERVAL_MINUTES)
            scenarios.append(df)
            print(f"  {pair}: {len(df)} Bars geladen "
                  f"({df.index[0].date()} -> {df.index[-1].date()})")
            time.sleep(0.3)  # sanft zum Rate-Limit
        except Exception as exc:  # noqa: BLE001
            print(f"  {pair}: uebersprungen ({str(exc)[:70]})")

    if not scenarios:
        raise SystemExit("Keine Daten geladen -- Netzwerk/Kraken-Zugriff pruefen.")

    print(f"\n{len(scenarios)} echte Coin-Szenarien -> Sweep laeuft...\n")
    sweep = run_sweep(scenarios, DEFAULT_GRID, preset_key=PRESET)
    print(format_sweep(sweep, top=15))


if __name__ == "__main__":
    main()
