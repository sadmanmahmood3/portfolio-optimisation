import numpy as np
import pandas as pd
import pytest

from src.model import ProphetModel
from src.optimiser import optimise_portfolio
from src.processor import clean_prices, daily_returns, to_prophet_format


def make_fake_prices(days: int = 300) -> pd.DataFrame:
    """Random-walk prices for 3 fake stocks."""
    rng = np.random.default_rng(seed=42)
    dates = pd.bdate_range("2024-01-01", periods=days)
    changes = rng.normal(0.0005, 0.01, size=(days, 3))
    prices = 100 * np.cumprod(1 + changes, axis=0)
    return pd.DataFrame(prices, index=dates, columns=["AAA", "BBB", "CCC"])


# ---------- processor ----------

def test_clean_prices_fills_gaps():
    prices = make_fake_prices()
    prices.iloc[10, 0] = np.nan  # create a gap
    cleaned = clean_prices(prices)
    assert not cleaned.isna().any().any()


def test_to_prophet_format_has_correct_columns():
    df = to_prophet_format(make_fake_prices(), "AAA")
    assert list(df.columns) == ["ds", "y"]


def test_daily_returns_has_one_less_row():
    prices = make_fake_prices()
    assert len(daily_returns(prices)) == len(prices) - 1


# ---------- optimiser ----------

def test_weights_add_up_to_one_and_respect_limits():
    prices = make_fake_prices()
    expected = pd.Series([0.002, -0.001, 0.001], index=["AAA", "BBB", "CCC"])

    weights = optimise_portfolio(expected, daily_returns(prices), min_weight=0.1, max_weight=0.6)

    assert weights.sum() == pytest.approx(1.0)
    assert (weights >= 0.1 - 1e-6).all()
    assert (weights <= 0.6 + 1e-6).all()


def test_impossible_limits_raise_error():
    prices = make_fake_prices()
    expected = pd.Series([0.001, 0.001, 0.001], index=["AAA", "BBB", "CCC"])

    with pytest.raises(ValueError):
        # 3 stocks x 50% minimum = 150%, which is impossible
        optimise_portfolio(expected, daily_returns(prices), min_weight=0.5, max_weight=0.9)


# ---------- model ----------

def test_model_predicts_a_small_return():
    df = to_prophet_format(make_fake_prices(), "AAA")
    predicted = ProphetModel().fit(df).predict_next_return()
    assert isinstance(predicted, float)
    assert abs(predicted) < 0.1  # a daily move over 10% would be unrealistic


def test_predict_before_fit_raises_error():
    with pytest.raises(RuntimeError):
        ProphetModel().predict_next_return()