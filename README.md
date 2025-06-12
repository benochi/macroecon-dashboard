# 📊 Macroeconomic Dashboard

This project visualizes the relationship between key U.S. macroeconomic indicators and the S&P 500 using interactive charts and heatmaps. It pulls data from the **FRED API** and **Yahoo Finance**, processes it with **Pandas**, and displays it using **Streamlit**, **Altair**, and **Seaborn**.

## 🔍 Features

- Weekly automatic data refresh (FRED + S&P 500 via yfinance)
- Raw, log, and Z-score scaling options
- Correlation heatmap (accessible color scheme)
- Filter indicators with sidebar
- Clean, accessible UI for data storytelling

## 📦 Tech Stack

- Python, Pandas, SQLAlchemy, SQLite
- FRED API + yfinance
- Streamlit
- Altair + Seaborn + Matplotlib

## 🚀 Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/macroecon-dashboard.git
   cd macroecon-dashboard

2. Install dependencies:
  pip install -r requirements.txt

3. Set up .env:
  FRED_API_KEY=your_key_here

4. Fetch the data:
  python fetch_fred.py
  python fetch_stocks.py

5. Launch the app:
  streamlit run main.py

