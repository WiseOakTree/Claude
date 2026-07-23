"""Kommandozeilen-Interface fuer den Krypto-Prop-Backtester.

Beispiele:
    python -m prop_backtester --demo
    python -m prop_backtester --csv daten.csv --config configs/example.yaml
    python -m prop_backtester --kraken XBTUSD --interval 60 --plot equity.png
    python -m prop_backtester --list-presets
"""

from __future__ import annotations

import argparse
import json
import sys

from . import backtest
from .config import BacktestConfig, load_config
from .prop import PRESETS
from .report import format_report, save_plot


def _load_data(args):
    from . import data
    if args.demo:
        return data.generate_synthetic(bars=args.demo_bars, interval_minutes=args.interval)
    if args.csv:
        return data.load_csv(args.csv)
    if args.kraken:
        return data.fetch_kraken_ohlc(args.kraken, interval_minutes=args.interval,
                                      since=args.since)
    raise SystemExit("Bitte Datenquelle angeben: --demo, --csv PFAD oder --kraken PAIR")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="prop_backtester",
        description="Realistischer Krypto-Prop-Backtester (Renko-Reversal, Kraken-Regeln)",
    )
    src = p.add_argument_group("Datenquelle")
    src.add_argument("--csv", help="OHLCV-CSV laden")
    src.add_argument("--kraken", metavar="PAIR", help="Von Kraken laden, z.B. XBTUSD")
    src.add_argument("--demo", action="store_true", help="Synthetische Demo-Daten nutzen")
    src.add_argument("--demo-bars", type=int, default=8000, help="Anzahl Demo-Bars")
    src.add_argument("--interval", type=int, default=60, help="Bar-Intervall in Minuten")
    src.add_argument("--since", type=int, default=None, help="Kraken: Unix-Startzeit")

    cfgg = p.add_argument_group("Konfiguration")
    cfgg.add_argument("--config", help="YAML-Konfigurationsdatei")
    cfgg.add_argument("--balance", type=float, help="Startkapital ueberschreiben")
    cfgg.add_argument("--risk", type=float, help="Risiko pro Trade (Anteil), z.B. 0.005")
    cfgg.add_argument("--atr-period", type=int, help="ATR-Periode fuer Brick-Groesse")
    cfgg.add_argument("--atr-mult", type=float, help="ATR-Multiplikator fuer Brick-Groesse")

    out = p.add_argument_group("Ausgabe")
    out.add_argument("--plot", metavar="PNG", help="Equity/Drawdown-Plot speichern")
    out.add_argument("--json", metavar="FILE", help="Ergebnis als JSON speichern")
    out.add_argument("--list-presets", action="store_true", help="Kraken-Presets zeigen")
    return p


def _apply_overrides(cfg: BacktestConfig, args) -> BacktestConfig:
    if args.balance is not None:
        cfg.initial_balance = args.balance
    if args.risk is not None:
        cfg.risk.risk_per_trade_pct = args.risk
    if args.atr_period is not None:
        cfg.renko.atr_period = args.atr_period
    if args.atr_mult is not None:
        cfg.renko.atr_multiplier = args.atr_mult
    return cfg.validate()


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_presets:
        print("Verfuegbare Kraken-Prop-Presets:\n")
        for key, r in PRESETS.items():
            print(f"  {key:16s} {r.name}")
            print(f"  {'':16s} {r.note}")
        return 0

    cfg = load_config(args.config) if args.config else BacktestConfig()
    cfg = _apply_overrides(cfg, args)

    df = _load_data(args)
    if len(df) < cfg.renko.atr_period + 5:
        raise SystemExit("Zu wenige Datenpunkte fuer die gewaehlte ATR-Periode.")

    result, metrics, challenges = backtest(df, cfg)
    print(format_report(result, metrics, challenges))

    if args.plot:
        ok = save_plot(result, args.plot)
        print(("\nPlot gespeichert: " + args.plot) if ok
              else "\nHinweis: matplotlib nicht verfuegbar, Plot uebersprungen.")

    if args.json:
        payload = {
            "metrics": metrics,
            "config": cfg.to_dict(),
            "challenges": {k: v.to_dict() for k, v in challenges.items()},
        }
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        print(f"JSON gespeichert: {args.json}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
