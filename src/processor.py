import pandas as pd


def clean_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Sort by date, remove timezone info, and fill small gaps in the data."""
    prices = prices.sort_index()

    # Prophet can't handle dates with timezones
    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)

    # If a stock is missing a day's price, use the previous day's price
    prices = prices.ffill()

    # Drop any rows still missing data (e.g. before a stock started trading)
    prices = prices.dropna()

    return prices


def to_prophet_format(prices: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Turn one stock's price column into Prophet's required format: columns 'ds' and 'y'."""
    df = prices[[ticker]].reset_index()
    df.columns = ["ds", "y"]
    return df


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Percentage change from one day to the next, for every stock."""
    return prices.pct_change().dropna()


if __name__ == "__main__":
    # Quick manual test
    from src.extractor import fetch_prices
    from src.settings import TICKERS, START_DATE

    prices = clean_prices(fetch_prices(TICKERS, START_DATE))

    print("Prophet format for AAPL:")
    print(to_prophet_format(prices, "AAPL").tail(3))

    print("\nDaily returns (last 3 days):")
    print(daily_returns(prices).tail(3).round(4))