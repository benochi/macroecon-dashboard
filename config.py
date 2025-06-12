import os
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

FRED_SERIES = {
    "fed_funds_rate": "FEDFUNDS",
    "m2_money_supply": "M2SL",
    "cpi": "CPIAUCSL",
    "unemployment_rate": "UNRATE",
    "real_gdp": "GDPC1",
    "personal_savings_rate": "PSAVERT",
    "10y_treasury_rate": "GS10",
    "2y_treasury_rate": "GS2",
    "yield_curve_10y_minus_2y": "T10Y2Y",
    "total_public_debt": "GFDEBTN",
    "inflation_expectations": "T10YIE",
}

YFINANCE_TICKERS = {
    "sp500": "^GSPC"
}

DB_PATH = "data/macros.db"