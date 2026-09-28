import numpy as np
import pandas as pd
from scipy.optimize import minimize


def optimise_portfolio(
    expected_returns: pd.Series,
    historical_returns: pd.DataFrame,
    min_weight: float,
    max_weight: float,
    lookback_days: int = 252,  # about 1 trading year
) -> pd.Series:
    """
    Find portfolio weights that maximise return per unit of risk (Sharpe ratio).
    expected_returns: predicted return per stock (from the Prophet models)
    historical_returns: past daily returns, used to measure risk
    """
    tickers = list(expected_returns.index)
    n = len(tickers)

    if n * min_weight > 1 or n * max_weight < 1:
        raise ValueError("min/max weights make it impossible for the portfolio to add up to 100%.")

    mu = expected_returns.values
    # Covariance = how much the stocks move together, based on the last year
    cov = historical_returns[tickers].tail(lookback_days).cov().values

    def negative_sharpe(weights: np.ndarray) -> float:
        portfolio_return = weights @ mu
        portfolio_risk = np.sqrt(weights @ cov @ weights)
        return -portfolio_return / portfolio_risk  # negative, because scipy minimises

    result = minimize(
        negative_sharpe,
        x0=np.full(n, 1 / n),                        # start from equal weights
        method="SLSQP",
        bounds=[(min_weight, max_weight)] * n,       # each stock between min and max
        constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}],  # weights add to 100%
    )

    if not result.success:
        raise RuntimeError(f"Optimisation failed: {result.message}")

    return pd.Series(result.x, index=tickers, name="weight")