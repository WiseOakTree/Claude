import pandas as pd

from prop_backtester.viz import heatmap_pivot


def _table():
    return pd.DataFrame({
        "renko.atr_multiplier": [0.5, 0.5, 1.0, 1.0],
        "risk.risk_per_trade_pct": [0.003, 0.005, 0.003, 0.005],
        "pass_rate": [1.0, 0.8, 0.2, 0.1],
        "median_return": [0.16, 0.20, 0.03, 0.04],
        "worst_maxdd": [0.05, 0.07, 0.04, 0.06],
    })


def test_heatmap_pivot_shape_and_orientation():
    p = heatmap_pivot(_table(), "risk.risk_per_trade_pct",
                      "renko.atr_multiplier", "pass_rate")
    assert list(p.columns) == [0.003, 0.005]
    # Zeilen absteigend sortiert -> grosse Brick-Groesse oben
    assert list(p.index) == [1.0, 0.5]
    assert p.loc[0.5, 0.003] == 1.0
    assert p.loc[1.0, 0.005] == 0.1


def test_heatmap_pivot_aggregates_hidden_param():
    # Zusaetzlicher versteckter Parameter -> pivot mittelt darueber
    t = _table()
    t2 = t.copy()
    t2["renko.atr_period"] = [10, 10, 10, 10]
    t["renko.atr_period"] = [20, 20, 20, 20]
    combined = pd.concat([t, t2], ignore_index=True)
    p = heatmap_pivot(combined, "risk.risk_per_trade_pct",
                      "renko.atr_multiplier", "pass_rate", agg="mean")
    # Mittel ueber die zwei Perioden = urspruenglicher Wert (identisch)
    assert p.loc[0.5, 0.003] == 1.0


def test_heatmap_pivot_missing_column_raises():
    try:
        heatmap_pivot(_table(), "risk.risk_per_trade_pct", "renko.atr_multiplier", "nope")
        assert False
    except ValueError:
        pass
