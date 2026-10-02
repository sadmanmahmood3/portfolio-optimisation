# Rules shared by every market (used by the optimiser)
MIN_WEIGHT = 0.05  # each stock gets at least 5%
MAX_WEIGHT = 0.30  # no stock gets more than 30%

MARKETS = {
    "US": {
        "name": "US stocks",
        "tickers": ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "JPM", "AMD", "TSM", "NFLX"],
        "start_date": "2020-01-01",
        "currency": "$",
        "trading_days": "Mon Tue Wed Thu Fri",
    },
    "BD": {
        "name": "Bangladesh (DSE)",
        "tickers": ["GP", "SQURPHARMA", "BATBC", "BRACBANK", "RENATA",
                    "WALTONHIL", "OLYMPIC", "MARICO", "ROBI", "BXPHARMA"],
        "start_date": "2024-01-01",  # DSE only serves about the last 2 years
        "currency": "৳",
        "trading_days": "Sun Mon Tue Wed Thu",
    },
}

# Old names, kept so existing code keeps working until we update it
TICKERS = MARKETS["US"]["tickers"]
START_DATE = MARKETS["US"]["start_date"]