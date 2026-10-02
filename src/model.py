import logging

import pandas as pd
from prophet import Prophet

from src.processor import to_prophet_format

# Hide Prophet's noisy log messages (set after import, or they get switched back on)
logging.getLogger("prophet.plot").disabled = True
logging.getLogger("cmdstanpy").disabled = True

US_TRADING_DAYS = "Mon Tue Wed Thu Fri"


class ProphetModel:
    """Wraps Prophet to forecast one stock's next-day movement."""

    def __init__(self):
        self.model: Prophet | None = None
        self.last_date: pd.Timestamp | None = None
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "ProphetModel":
        """Train on a table with columns 'ds' (date) and 'y' (price)."""
        # Yearly patterns need at least 2 full years of data to be learned reliably
        history_days = (df["ds"].max() - df["ds"].min()).days

        self.model = Prophet(
            daily_seasonality=False,                  # we only have one price per day
            weekly_seasonality=True,
            yearly_seasonality=history_days >= 730,   # only if there's enough history
            changepoint_range=0.95,                   # let the trend adapt to recent data
        )
        self.model.fit(df)
        self.last_date = pd.Timestamp(df["ds"].max())
        self.is_fitted = True
        return self

    def predict_next_return(self, trading_days: str = US_TRADING_DAYS) -> float:
        """
        Predicted % change for the next trading day.
        trading_days: which weekdays the market is open, e.g. "Sun Mon Tue Wed Thu" for DSE.
        """
        if not self.is_fitted or self.model is None or self.last_date is None:
            raise RuntimeError("Call fit() before predicting.")

        # Work out the next day the market is open (e.g. Thursday -> Sunday for DSE)
        next_day = self.last_date + pd.offsets.CustomBusinessDay(weekmask=trading_days)

        # Ask the model for its estimate on the last known day and the next trading day
        future = pd.DataFrame({"ds": [self.last_date, next_day]})
        forecast = self.model.predict(future)

        today_estimate = forecast["yhat"].iloc[0]
        tomorrow_estimate = forecast["yhat"].iloc[1]
        return float((tomorrow_estimate - today_estimate) / today_estimate)


def forecast_all(
    prices: pd.DataFrame, tickers: list[str], trading_days: str = US_TRADING_DAYS
) -> pd.DataFrame:
    """Train a model per stock and return last price, predicted price and expected return."""
    results = []

    for ticker in tickers:
        print(f"Training model for {ticker}...")
        df = to_prophet_format(prices, ticker)

        model = ProphetModel().fit(df)
        predicted_return = model.predict_next_return(trading_days)
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