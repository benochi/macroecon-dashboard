import requests
import pandas as pd
from config import FRED_API_KEY, FRED_SERIES, DB_PATH
from sqlalchemy import create_engine
import os
from datetime import timedelta

def fetch_fred_series(series_id, start_date=None):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
    }
    if start_date:
        params["observation_start"] = start_date

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("observations", [])
        if not data:
            return pd.DataFrame(columns=["date", "value"])

        df = pd.DataFrame(data)[["date", "value"]]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df.dropna(inplace=True)
        return df

    except requests.exceptions.RequestException as e:
        print(f"Request error for series {series_id}: {e}")
        return pd.DataFrame(columns=["date", "value"])
    except ValueError as e:
        print(f"Parsing error for series {series_id}: {e}")
        return pd.DataFrame(columns=["date", "value"])

def get_latest_date_from_csv(name):
    path = f"data/{name}.csv"
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        if df.empty:
            return None
        return pd.to_datetime(df["date"]).max().date()
    except Exception as e:
        print(f"Error reading existing CSV for {name}: {e}")
        return None

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
    for name, series_id in FRED_SERIES.items():
        print(f"Checking updates for {name}...")

        try:
            latest_date = get_latest_date_from_csv(name)
            start_date = (latest_date + timedelta(days=1)).isoformat() if latest_date else None

            df = fetch_fred_series(series_id, start_date=start_date)
            if df.empty:
                print(f"{name} already up-to-date.")
                continue

            updated_df = save_to_csv(df, name)
            save_to_sqlite(updated_df, name)
            print(f"Updated {name} with {len(df)} new rows.")

        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    run()
