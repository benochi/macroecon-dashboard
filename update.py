from ingest.fetch_fred import run as update_fred
from ingest.fetch_yfinance import run as update_yf

if __name__ == "__main__":
    update_fred()
    update_yf()
