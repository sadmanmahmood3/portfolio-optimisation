import time
from datetime import date

import pandas as pd
import yfinance as yf


def fetch_prices(
    tickers: list[str],
    start_date: str,
    end_date: str | None = None,
    market: str = "US",
) -> pd.DataFrame:
    """Download daily closing prices. Returns one column per ticker, one row per date."""
    if market == "US":
        return _fetch_us(tickers, start_date, end_date)
    if market == "BD":
        return _fetch_bd(tickers, start_date, end_date)
    raise ValueError(f"Unknown market: {market}")


def _fetch_us(tickers: list[str], start_date: str, end_date: str | None) -> pd.DataFrame:
    """US prices from Yahoo Finance."""
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,  # adjusts for stock splits and dividends
        progress=False,
    )

    if data is None or data.empty:
        raise ValueError("No data returned. Check the tickers or your internet connection.")

    prices = data["Close"]

    # If only one ticker was requested, make sure we still return a table
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    return prices


def _fetch_bd(
    tickers: list[str], start_date: str, end_date: str | None, retries: int = 3
) -> pd.DataFrame:
    """Bangladesh prices from the Dhaka Stock Exchange (via bdshare)."""
    from bdshare import get_historical_data

    end_date = end_date or date.today().isoformat()
    columns = {}

    for ticker in tickers:
        # The DSE website sometimes drops connections, so retry a few times
        df=None
        for attempt in range(1, retries + 1):
            try:
                df = get_historical_data(start_date, end_date, ticker)
                break
            except Exception as e:
                if attempt == retries:
                    raise RuntimeError(f"Could not download {ticker} from DSE: {e}") from e
                time.sleep(2 * attempt)

        if df is None or df.empty:
            raise ValueError(f"No DSE data returned for {ticker}.")

        close = pd.to_numeric(df["close"], errors="coerce")
        close.index = pd.to_datetime(close.index)
        close = close.where(close > 0)  # a price of 0 means "no trade", treat as missing
        close = close[~close.index.duplicated(keep="last")]
        columns[ticker] = close

    prices = pd.DataFrame(columns).sort_index()  # DSE returns newest first, so sort
    prices.index.name = "Date"
    return prices


if __name__ == "__main__":
    # Quick manual test: python -m src.extractor BD   (or US)
    import sys

    from src.settings import MARKETS

    market = sys.argv[1] if len(sys.argv) > 1 else "US"
    config = MARKETS[market]

    prices = fetch_prices(config["tickers"], config["start_date"], market=market)
    print(prices.tail())
    print(f"\nShape: {prices.shape[0]} days x {prices.shape[1]} stocks")