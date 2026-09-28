import logging

import pandas as pd
from prophet import Prophet

from src.processor import to_prophet_format

# Hide Prophet's noisy log messages (set after import, or they get switched back on)
logging.getLogger("prophet.plot").disabled = True
logging.getLogger("cmdstanpy").disabled = True


class ProphetModel:
    """Wraps Prophet to forecast one stock's next-day movement."""

    def __init__(self):
        self.model = Prophet(
            daily_seasonality=False,   # we only have one price per day
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_range=0.95,    # let the trend adapt to recent data
        )
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "ProphetModel":
        """Train on a table with columns 'ds' (date) and 'y' (price)."""
        self.model.fit(df)
        self.is_fitted = True
        return self

    def predict_next_return(self) -> float:
        """
        Predicted % change for the next business day.
        Compares the model's forecast for tomorrow with its own estimate for today,
        so any gap between the trend line and the real price doesn't distort the result.
        """
        if not self.is_fitted:
            raise RuntimeError("Call fit() before predicting.")

        future = self.model.make_future_dataframe(periods=1, freq="B")  # "B" = business day
        forecast = self.model.predict(future)

        today_estimate = forecast["yhat"].iloc[-2]
        tomorrow_estimate = forecast["yhat"].iloc[-1]
        return float((tomorrow_estimate - today_estimate) / today_estimate)


def forecast_all(prices: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """Train a model per stock and return last price, predicted price and expected return."""
    results = []

    for ticker in tickers:
        print(f"Training model for {ticker}...")
        df = to_prophet_format(prices, ticker)

        model = ProphetModel().fit(df)
        predicted_return = model.predict_next_return()
        last_price = float(df["y"].iloc[-1])

        results.append({
            "ticker": ticker,
            "last_price": last_price,
            "predicted_price": last_price * (1 + predicted_return),
            "predicted_return": predicted_return,
        })

    return pd.DataFrame(results).set_index("ticker")


if __name__ == "__main__":
    # Quick manual test
    from src.extractor import fetch_prices
    from src.processor import clean_prices
    from src.settings import TICKERS, START_DATE

    prices = clean_prices(fetch_prices(TICKERS, START_DATE))
    forecasts = forecast_all(prices, TICKERS)

    print("\nForecasts:")
    print(forecasts.round(4))