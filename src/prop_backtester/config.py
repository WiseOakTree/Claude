"""Konfigurations-Objekte fuer den Krypto-Prop-Backtester.

Alle Parameter der Strategie, der Renko-Bricks, der Handelskosten und des
Risikomanagements werden hier zentral definiert. Die Werte lassen sich per
YAML-Datei ueberschreiben (siehe ``load_config``).

Bewusst nur mit der Python-Standardbibliothek + PyYAML gehalten, damit die
Konfiguration leicht lesbar und versionierbar bleibt.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class RenkoConfig:
    """Parameter fuer den Aufbau der Renko-Bricks (ATR-basiert)."""

    mode: str = "atr"          # "atr" (dynamisch) oder "fixed"
    atr_period: int = 14        # ATR-Laenge fuer die Brick-Groesse
    atr_multiplier: float = 1.0  # Brick-Groesse = ATR * multiplier
    fixed_brick: Optional[float] = None  # nur bei mode == "fixed": absolute Brick-Groesse
    fixed_brick_pct: Optional[float] = None  # alternativ bei "fixed": Prozent vom Preis

    def validate(self) -> None:
        if self.mode not in ("atr", "fixed"):
            raise ValueError(f"RenkoConfig.mode ungueltig: {self.mode!r}")
        if self.mode == "atr" and self.atr_period < 2:
            raise ValueError("atr_period muss >= 2 sein")
        if self.mode == "fixed" and not (self.fixed_brick or self.fixed_brick_pct):
            raise ValueError("mode=fixed benoetigt fixed_brick oder fixed_brick_pct")


@dataclass
class StrategyConfig:
    """Renko-Reversal-Strategie: Einstieg bei N Gegen-Bricks."""

    reversal_bricks: int = 2   # so viele gleichgerichtete Bricks loesen ein Signal aus
    allow_short: bool = True   # Short-Positionen erlaubt (Stop-and-Reverse)
    allow_long: bool = True

    def validate(self) -> None:
        if self.reversal_bricks < 1:
            raise ValueError("reversal_bricks muss >= 1 sein")
        if not (self.allow_long or self.allow_short):
            raise ValueError("Mindestens eine Handelsrichtung muss erlaubt sein")


@dataclass
class CostConfig:
    """Realistische Handelskosten, als Anteil (0.001 = 0.1%).

    Deckt die vier realen Kostenquellen ab:
      * ``fee_pct``            -- Boersen-/Taker-Gebuehr pro Seite
      * ``half_spread_pct``    -- halber Bid/Ask-Spread pro Fill
      * ``slippage_pct``       -- fixe Slippage pro Fill
      * ``slippage_vol_mult``  -- zusaetzliche Slippage ~ Volatilitaet
                                  (mult * Brick/Preis) -- teurer in wilden Phasen
      * ``funding_rate_daily_pct`` -- Finanzierungskosten pro Tag auf den
                                  Nominalwert offener Positionen (Perp-Funding-Drag)
    """

    fee_pct: float = 0.0005            # Taker-Gebuehr pro Seite
    slippage_pct: float = 0.0002       # fixe Slippage pro Fill
    half_spread_pct: float = 0.0002    # halber Spread pro Fill
    slippage_vol_mult: float = 0.05    # vola-abhaengige Slippage (* Brick/Preis)
    funding_rate_daily_pct: float = 0.0003  # ~0.01%/8h Funding-Drag auf Nominalwert

    def validate(self) -> None:
        for name in ("fee_pct", "slippage_pct", "half_spread_pct",
                     "slippage_vol_mult", "funding_rate_daily_pct"):
            if getattr(self, name) < 0:
                raise ValueError(f"Kosten duerfen nicht negativ sein: {name}")


@dataclass
class RiskConfig:
    """Positionsgroesse & Hebel."""

    risk_per_trade_pct: float = 0.005  # Risiko pro Trade als Anteil des Kontostands (0.5%)
    stop_bricks: float = 2.0            # Stop-Distanz = stop_bricks * Brick-Groesse
    max_leverage: float = 5.0           # Obergrenze fuer Nominalwert / Kontostand
    min_notional: float = 10.0          # kleinstmoegliche Position (Boersen-Minimum)
    # TP-Ziele fuer die Signal-Nachricht als R-Vielfache (R = Stop-Distanz).
    # Nur informativ fuer manuelles Teil-Mitnehmen -- der Backtest nutzt sie NICHT
    # (dort ist der Ausstieg immer das Gegensignal / Reversal).
    tp_r_multiples: list = field(default_factory=lambda: [2.0, 4.0])

    def validate(self) -> None:
        if not (0 < self.risk_per_trade_pct < 1):
            raise ValueError("risk_per_trade_pct muss zwischen 0 und 1 liegen")
        if self.stop_bricks <= 0:
            raise ValueError("stop_bricks muss > 0 sein")
        if self.max_leverage <= 0:
            raise ValueError("max_leverage muss > 0 sein")
        if any(m <= 0 for m in self.tp_r_multiples):
            raise ValueError("tp_r_multiples muessen > 0 sein")


@dataclass
class BacktestConfig:
    """Gesamtkonfiguration eines Backtest-Laufs."""

    initial_balance: float = 50_000.0
    renko: RenkoConfig = field(default_factory=RenkoConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    costs: CostConfig = field(default_factory=CostConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)

    def validate(self) -> "BacktestConfig":
        if self.initial_balance <= 0:
            raise ValueError("initial_balance muss > 0 sein")
        self.renko.validate()
        self.strategy.validate()
        self.costs.validate()
        self.risk.validate()
        return self

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _sub(cls, data: Dict[str, Any], key: str):
    """Baut ein Sub-Config-Objekt aus dem YAML-Teilbaum (mit Defaults)."""
    section = data.get(key) or {}
    if not isinstance(section, dict):
        raise ValueError(f"Konfig-Abschnitt {key!r} muss eine Map sein")
    return cls(**section)


def config_from_dict(data: Dict[str, Any]) -> BacktestConfig:
    data = data or {}
    cfg = BacktestConfig(
        initial_balance=float(data.get("initial_balance", 50_000.0)),
        renko=_sub(RenkoConfig, data, "renko"),
        strategy=_sub(StrategyConfig, data, "strategy"),
        costs=_sub(CostConfig, data, "costs"),
        risk=_sub(RiskConfig, data, "risk"),
    )
    return cfg.validate()


def load_config(path: str) -> BacktestConfig:
    """Laedt eine YAML-Konfiguration und validiert sie."""
    import yaml  # lokal importiert, damit das Paket ohne YAML nutzbar bleibt

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return config_from_dict(data)
