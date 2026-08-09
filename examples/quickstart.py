"""Minimalbeispiel: Backtest auf synthetischen Daten, Bericht in die Konsole.

Ausfuehren aus dem Projekt-Root:
    python examples/quickstart.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prop_backtester import backtest, BacktestConfig  # noqa: E402
from prop_backtester import data  # noqa: E402
from prop_backtester.report import format_report  # noqa: E402


def main() -> None:
    # 1) Daten holen (hier synthetisch; alternativ data.load_csv / data.fetch_kraken_ohlc)
    df = data.generate_synthetic(bars=8000, interval_minutes=60, seed=7)

    # 2) Konfiguration -- Kontogroesse = dein Kraken-Prop-Konto
    cfg = BacktestConfig()
    cfg.initial_balance = 50_000
    cfg.risk.risk_per_trade_pct = 0.005  # 0.5% Risiko/Trade -> schont den Drawdown

    # 3) Backtest + Bericht
    result, metrics, challenges = backtest(df, cfg)
    print(format_report(result, metrics, challenges))


if __name__ == "__main__":
    main()
