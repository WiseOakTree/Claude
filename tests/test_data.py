import numpy as np

from prop_backtester import data


def test_csv_roundtrip(tmp_path):
    # Schreiben/Lesen mit ISO-Zeitstempel-Index muss verlustfrei funktionieren.
    df = data.generate_synthetic(bars=300, seed=8)
    path = tmp_path / "hist.csv"
    df.to_csv(path)
    loaded = data.load_csv(str(path))
    assert len(loaded) == len(df)
    assert list(loaded.columns) == ["open", "high", "low", "close", "volume"]
    assert loaded.index.tz is not None
    assert np.allclose(loaded["close"].values, df["close"].values)


def test_generate_realistic_valid_ohlc():
    df = data.generate_realistic(bars=2000, seed=3)
    assert len(df) == 2000
    assert (df["high"] >= df["low"]).all()
    assert (df["high"] >= df["close"]).all()
    assert (df["low"] <= df["close"]).all()
    assert (df["close"] > 0).all()
    assert df.index.tz is not None


def test_realistic_has_fatter_tails_than_gbm():
    # Student-t + Jumps -> hoehere Kurtosis der Log-Returns als reiner GBM.
    r_real = np.diff(np.log(data.generate_realistic(bars=6000, seed=5)["close"].values))
    r_gbm = np.diff(np.log(data.generate_synthetic(bars=6000, seed=5)["close"].values))

    def excess_kurtosis(x):
        x = (x - x.mean()) / x.std()
        return (x ** 4).mean() - 3.0

    assert excess_kurtosis(r_real) > excess_kurtosis(r_gbm)


def test_realistic_t_dof_guard():
    try:
        data.generate_realistic(bars=100, t_dof=2.0)
        assert False
    except ValueError:
        pass
