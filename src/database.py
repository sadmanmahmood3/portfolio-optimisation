import os

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()  # reads SUPABASE_URL and SUPABASE_KEY from the .env file

TABLE = "portfolio_forecasts"


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set (check your .env file).")
    return create_client(url, key)


def save_results(result: dict, client: Client | None = None) -> int:
    """Save one run's forecasts and weights. Re-running the same market and date overwrites it."""
    client = client or get_client()
    forecasts = result["forecasts"]
    weights = result["weights"]
    as_of = result["as_of"].date().isoformat()

    rows = [
        {
            "market": result["market"],
            "as_of": as_of,
            "ticker": ticker,
            "last_price": float(forecasts.loc[ticker, "last_price"]),
            "predicted_price": float(forecasts.loc[ticker, "predicted_price"]),
            "predicted_return": float(forecasts.loc[ticker, "predicted_return"]),
            "weight": float(weights[ticker]),
        }
        for ticker in forecasts.index
    ]

    client.table(TABLE).upsert(rows, on_conflict="market,as_of,ticker").execute()
    return len(rows)


def load_results(
    market: str | None = None, as_of: str | None = None, client: Client | None = None
) -> pd.DataFrame:
    """Load saved forecasts, optionally for one market and/or one date."""
    client = client or get_client()
    query = client.table(TABLE).select("*")
    if market:
        query = query.eq("market", market)
    if as_of:
        query = query.eq("as_of", as_of)
    rows = query.order("as_of", desc=True).execute().data
    return pd.DataFrame(rows)