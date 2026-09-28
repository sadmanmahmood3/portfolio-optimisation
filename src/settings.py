# Stocks to include in the portfolio
TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "JPM", "AMD", "TSM", "NFLX"]

# How far back to pull price history
START_DATE = "2020-01-01"

# Portfolio rules for the optimiser (used in Phase 4)
MIN_WEIGHT = 0.05  # each stock gets at least 5%
MAX_WEIGHT = 0.30  # no stock gets more than 30%