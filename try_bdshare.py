from datetime import date

from bdshare import get_historical_data

TICKERS = ["GP", "SQURPHARMA", "BATBC", "BRACBANK", "RENATA",
           "WALTONHIL", "OLYMPIC", "MARICO", "ROBI", "BXPHARMA"]

end = date.today().isoformat()
failed = []

for ticker in TICKERS:
    try:
        df = get_historical_data("2024-01-01", end, ticker)
        print(f"{ticker:<11} OK  {len(df):>4} rows, up to {df.index.max()}")
    except Exception as e:
        print(f"{ticker:<11} FAILED: {e}")
        failed.append(ticker)

if failed:
    raise SystemExit(f"Failed tickers: {failed}")