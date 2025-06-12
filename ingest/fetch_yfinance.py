import yfinance as yf
import pandas as pd
from config import YFINANCE_TICKERS, DB_PATH
from sqlalchemy import create_engine
import os

def fetch_yfinance_data(ticker, period="max"):
    try:
        data = yf.Ticker(ticker).history(period=period)
        df = data.reset_index()[["Date", "Close"]].rename(columns={"Date": "date", "Close": "value"})
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame(columns=["date", "value"])

def save_to_csv(df, name):
    path = f"data/{name}.csv"
    os.makedirs("data", exist_ok=True)

    try:
        if os.path.exists(path):
            existing = pd.read_csv(path)
            combined = pd.concat([existing, df]).drop_duplicates(subset="date").sort_values("date")
        else:
            combined = df
        combined.to_csv(path, index=False)
        return combined
    except Exception as e:
        print(f"Error saving CSV for {name}: {e}")
        return df

def save_to_sqlite(df, name):
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}")
        df.to_sql(name, engine, if_exists="replace", index=False)
    except Exception as e:
        print(f"Error saving to SQLite for {name}: {e}")

def run():
    for name, ticker in YFINANCE_TICKERS.items():
        print(f"Fetching {name} from Yahoo Finance...")
        df = fetch_yfinance_data(ticker)
        if df.empty:
            print(f"No data returned for {name}.")
            continue

        updated_df = save_to_csv(df, name)
        save_to_sqlite(updated_df, name)
        print(f"Finished updating {name}.")

if __name__ == "__main__":
    run()