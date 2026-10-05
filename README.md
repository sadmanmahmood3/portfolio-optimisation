# Portfolio Optimisation with Prophet

A production-style machine learning pipeline that forecasts stock prices with Facebook's Prophet model, then uses Markowitz portfolio optimisation to decide how to split money across 10 stocks. It runs automatically every weekday and publishes results to a live dashboard.

🔗 Live dashboard: https://spadex-portfolio-forecast.streamlit.app

> ⚠️ A learning project, not investment advice.

## How it works

1. **Extract**: download the daily closing prices with `yfinance`
2. **Process**: clean gaps in the objects and reshape the data for Prophet
3. **Forecast**: train one Prophet model per stock and predict the next trading day's return
4. **Optimise**: find the weights with the best return per unit of risk (Sharpe ratio) using SciPy's SLSQP solver, with each stock kept between 5% and 30%
5. **Store**: save forecasts and weights to Supabase (PostgreSQL)
6. **Display**: a Streamlit dashboard reads the latest results from Supabase

## Automation

| Workflow | When | What it does |
|---|---|---|
| **Tests** | Every push | Runs pytest suite |
| **Daily forecast** | Weekdays, 09:00 UTC | Runs the full pipeline and saves new results |

## Tech stack

Python 3.12 · Poetry · Prophet · SciPy · pandas · yfinance · Supabase · Streamlit · Plotly · pytest · GitHub Actions · Streamlit Community Cloud

## Project structure

```
src/
├── settings.py        # tickers, date range, weight limits
├── extractor.py       # downloads price data
├── processor.py       # cleans and reshapes data
├── model.py           # Prophet forecasting
├── optimiser.py       # Markowitz optimisation
├── database.py        # Supabase read/write
├── main.py            # runs the full pipeline
└── streamlit_app.py   # dashboard
tests/
└── test_pipeline.py   # unit tests
.github/workflows/
├── tests.yml
└── daily.yml
```

## Run it locally (Windows)

```powershell
poetry install
```

Create a `.env` file with your Supabase details:

```
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-secret-key
```

Then:

```powershell
python -m src.main                    # run the pipeline
pytest -v                             # run the tests
streamlit run src/streamlit_app.py    # open the dashboard
```

## Credits
Egor Howell
