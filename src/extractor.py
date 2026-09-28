import pandas as pd
import yfinance as yf


def fetch_prices(tickers: list[str], start_date: str, end_date: str | None = None) -> pd.DataFrame:
    """Download daily closing prices. Returns one column per ticker, one row per date."""
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,  # adjusts for stock splits and dividends
        progress=False,
    )

    if data.empty:
        raise ValueError("No data returned. Check the tickers or your internet connection.")

    prices = data["Close"]

    # If only one ticker was requested, make sure we still return a table
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    return prices


if __name__ == "__main__":
    # Quick manual test: run this file directly to see some data
    from src.settings import TICKERS, START_DATE

    prices = fetch_prices(TICKERS, START_DATE)
    print(prices.tail())
    print(f"\nShape: {prices.shape[0]} days x {prices.shape[1]} stocks")