import pandas as pd

from src.extractor import fetch_prices
from src.model import forecast_all
from src.optimiser import optimise_portfolio
from src.processor import clean_prices, daily_returns
from src.settings import MAX_WEIGHT, MIN_WEIGHT, START_DATE, TICKERS


def run_optimisation(
    tickers: list[str] = TICKERS,
    start_date: str = START_DATE,
    min_weight: float = MIN_WEIGHT,
    max_weight: float = MAX_WEIGHT,
) -> dict:
    """Full pipeline: download data -> forecast each stock -> optimise the portfolio."""
    prices = clean_prices(fetch_prices(tickers, start_date))
    forecasts = forecast_all(prices, tickers)

    weights = optimise_portfolio(
        forecasts["predicted_return"],
        daily_returns(prices),
        min_weight,
        max_weight,
    )

    return {
        "as_of": prices.index[-1],
        "weights": weights,
        "predicted_returns": forecasts["predicted_return"],
        "forecasts": forecasts,
    }


if __name__ == "__main__":
    result = run_optimisation()

    print(f"\nPortfolio as of {result['as_of'].date()}:")
    weights_pct = (result["weights"] * 100).round(1).sort_values(ascending=False)
    for ticker, pct in weights_pct.items():
        print(f"  {ticker:<5} {pct:>5}%")
    print(f"  Total: {weights_pct.sum():.1f}%")