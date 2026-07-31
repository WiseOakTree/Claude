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
        gen = data.generate_synthetic if args.simple_demo else data.generate_realistic
        return gen(bars=args.demo_bars, interval_minutes=args.interval)
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
    src.add_argument("--demo", action="store_true",
                     help="Realistische Demo-Daten nutzen (GARCH, Fat Tails, Jumps)")
    src.add_argument("--simple-demo", action="store_true",
                     help="Demo als einfachen Random Walk erzeugen (statt realistisch)")
    src.add_argument("--demo-bars", type=int, default=8000, help="Anzahl Demo-Bars")
    src.add_argument("--interval", type=int, default=60, help="Bar-Intervall in Minuten")
    src.add_argument("--since", type=int, default=None, help="Kraken: Unix-Startzeit")

    sw = p.add_argument_group("Parameter-Sweep")
    sw.add_argument("--sweep", action="store_true",
                    help="Parameter-Sweep ueber Szenarien (Robustheit statt Einzellauf)")
    sw.add_argument("--preset", default="1step_classic",
                    help="Preset, fuer das optimiert wird (siehe --list-presets); "
                         "App-Namen wie 'starter' werden aufgeloest")
    sw.add_argument("--scenarios", type=int, default=12,
                    help="Anzahl synthetischer Szenarien (ohne echte Daten)")
    sw.add_argument("--sweep-bars", type=int, default=6000,
                    help="Bars pro synthetischem Szenario")
    sw.add_argument("--wf-window", type=int, default=None,
                    help="Walk-Forward-Fenstergroesse (Bars) bei echten Daten")
    sw.add_argument("--wf-step", type=int, default=None,
                    help="Walk-Forward-Schrittweite (Bars); Default = Fenstergroesse")
    sw.add_argument("--sweep-csv", metavar="FILE", help="Sweep-Tabelle als CSV speichern")
    sw.add_argument("--heatmap", metavar="PNG",
                    help="Heatmap (Pass-Rate / Rendite / Drawdown) als PNG speichern")

    dl = p.add_argument_group("Kraken-Download (tiefe Historie via Trades-Endpoint)")
    dl.add_argument("--download-kraken", metavar="PAIR",
                    help="Trades von Kraken laden und zu OHLC aggregieren, z.B. XBTUSD")
    dl.add_argument("--from", dest="from_date", default=0,
                    help="Startzeit (ISO-Datum oder Unix-Sekunden)")
    dl.add_argument("--to", dest="to_date", default=None,
                    help="Endzeit (ISO-Datum oder Unix-Sekunden)")
    dl.add_argument("--out", help="Ziel-CSV fuer die heruntergeladenen OHLC-Daten")
    dl.add_argument("--max-trades", type=int, default=None,
                    help="Maximale Anzahl Trades (begrenzt den Download)")
    dl.add_argument("--sleep", type=float, default=1.6,
                    help="Pause zwischen API-Calls in Sekunden (Rate-Limit)")

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


def _run_download(args) -> int:
    from . import kraken

    out = args.out or f"{args.download_kraken.lower()}_{args.interval}m.csv"
    print(f"Lade Kraken-Trades fuer {args.download_kraken} (Intervall {args.interval}min)...")
    print("Hinweis: der Trades-Endpoint paginiert -- tiefe Historien dauern (Rate-Limit).")
    df = kraken.download_ohlc(
        args.download_kraken, interval_minutes=args.interval,
        since=args.from_date, until=args.to_date,
        max_trades=args.max_trades, sleep_s=args.sleep,
    )
    df.to_csv(out)
    print(f"\nFertig: {len(df)} OHLC-Bars von {df.index[0]} bis {df.index[-1]}")
    print(f"Gespeichert: {out}")
    print(f"\nNaechster Schritt:\n  python -m prop_backtester --csv {out} --balance 50000"
          f"\n  python -m prop_backtester --sweep --csv {out} --wf-window 3000 --wf-step 1500")
    return 0


def _run_sweep(args, cfg: BacktestConfig) -> int:
    from .sweep import (DEFAULT_GRID, run_sweep, synthetic_scenarios,
                        walkforward_scenarios)
    from .report import format_sweep

    if args.csv or args.kraken:
        # Walk-Forward auf echten Daten -- der realistischste Robustheitstest
        df = _load_data(args)
        window = args.wf_window or max(len(df) // 6, cfg.renko.atr_period + 50)
        scenarios = walkforward_scenarios(df, window_bars=window, step_bars=args.wf_step)
        print(f"Walk-Forward: {len(scenarios)} Fenster à {window} Bars aus {len(df)} Bars.\n")
    else:
        scenarios = synthetic_scenarios(n=args.scenarios, bars=args.sweep_bars,
                                        interval_minutes=args.interval)
        print(f"Synthetisch: {len(scenarios)} realistische Szenarien à {args.sweep_bars} Bars.\n")

    sweep = run_sweep(scenarios, DEFAULT_GRID, preset_key=args.preset, base_cfg=cfg)
    print(format_sweep(sweep))

    if args.sweep_csv:
        sweep.table.to_csv(args.sweep_csv, index=False)
        print(f"\nSweep-Tabelle gespeichert: {args.sweep_csv}")
    if args.heatmap:
        from .viz import save_heatmap
        ok = save_heatmap(sweep, args.heatmap)
        print(("\nHeatmap gespeichert: " + args.heatmap) if ok
              else "\nHinweis: matplotlib nicht verfuegbar, Heatmap uebersprungen.")
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_presets:
        print("Verfuegbare Kraken-Prop-Presets:\n")
        for key, r in PRESETS.items():
            print(f"  {key:16s} {r.name}")
            print(f"  {'':16s} {r.note}")
        from .prop import ALIASES
        if ALIASES:
            print("\n  Alias (Name in der Kraken-App):")
            for a, target in ALIASES.items():
                print(f"    {a:14s} -> {target}")
        return 0

    if args.download_kraken:
        return _run_download(args)

    cfg = load_config(args.config) if args.config else BacktestConfig()
    cfg = _apply_overrides(cfg, args)

    if args.sweep:
        return _run_sweep(args, cfg)

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
