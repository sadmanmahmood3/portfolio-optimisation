import argparse

from src.extractor import fetch_prices
from src.model import forecast_all
from src.optimiser import optimise_portfolio
from src.processor import clean_prices, daily_returns
from src.settings import MARKETS, MAX_WEIGHT, MIN_WEIGHT


def run_optimisation(
    market: str = "US",
    tickers: list[str] | None = None,
    start_date: str | None = None,
    min_weight: float = MIN_WEIGHT,
    max_weight: float = MAX_WEIGHT,
) -> dict:
    """Full pipeline for one market: download data -> forecast each stock -> optimise."""
    config = MARKETS[market]
    tickers = tickers or config["tickers"]
    start_date = start_date or config["start_date"]

    prices = clean_prices(fetch_prices(tickers, start_date, market=market))
    forecasts = forecast_all(prices, tickers, trading_days=config["trading_days"])

    weights = optimise_portfolio(
        forecasts["predicted_return"],
        daily_returns(prices),
        min_weight,
        max_weight,
    )

    return {
        "market": market,
        "as_of": prices.index[-1],
        "weights": weights,
        "predicted_returns": forecasts["predicted_return"],
        "forecasts": forecasts,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the portfolio pipeline.")
    parser.add_argument("--market", choices=list(MARKETS), default="US")
    parser.add_argument("--no-save", action="store_true", help="don't save results to Supabase")
    args = parser.parse_args()

    result = run_optimisation(market=args.market)

    print(f"\n{MARKETS[args.market]['name']} portfolio as of {result['as_of'].date()}:")
    weights_pct = (result["weights"] * 100).round(1).sort_values(ascending=False)
    for ticker, pct in weights_pct.items():
        print(f"  {ticker:<11} {pct:>5}%")
    print(f"  Total: {weights_pct.sum():.1f}%")

    if args.no_save:
        print("\n(Not saved: --no-save was used.)")
    else:
        from src.database import save_results
        saved = save_results(result)
        print(f"\nSaved {saved} rows to Supabase.")