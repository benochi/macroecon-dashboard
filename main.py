import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from config import DB_PATH, FRED_SERIES
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Macroeconomic Dashboard", layout="wide")

@st.cache_data
def load_data(table_name):
    engine = create_engine(f"sqlite:///{DB_PATH}")
    try:
        df = pd.read_sql_table(table_name, engine)
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Failed to load {table_name}: {e}")
        return pd.DataFrame()

@st.cache_data
def load_all_macro_data():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    dfs = []
    for name in FRED_SERIES.keys():
        df = pd.read_sql_table(name, engine)
        df["date"] = pd.to_datetime(df["date"])
        df.rename(columns={"value": name}, inplace=True)
        dfs.append(df[["date", name]])
    macro_all = dfs[0]
    for df in dfs[1:]:
        macro_all = pd.merge(macro_all, df, on="date", how="outer")
    return macro_all
    
#* UI
st.title("Macroeconomic indicators vs. S&P 500")

selected_series = st.selectbox("Select an economic indicator", list(FRED_SERIES.keys()))

macro_df = load_data(selected_series)
sp500_df = load_data("sp500")

# Plots
if not macro_df.empty and not sp500_df.empty:
    merged = pd.merge(macro_df, sp500_df, on="date", how="inner", suffixes=("_macro", "_sp500"))

    st.line_chart(
        data=merged.set_index("date")[["value_macro", "value_sp500"]],
        use_container_width=True
    )

    # --- Multi-Line Chart: All Indicators vs. S&P 500 ---
    st.subheader("Full Comparison: S&P 500 and Macroeconomic Indicators")

    macro_all = load_all_macro_data()
    sp500_df["date"] = pd.to_datetime(sp500_df["date"])
    full = pd.merge(macro_all, sp500_df[["date", "value"]].rename(columns={"value": "sp500"}), on="date", how="inner")

    # Sidebar multi-select for filtering
    with st.sidebar:
        st.header("Indicator Filters")
        selected_indicators = st.multiselect(
            "Select indicators to plot",
            options=list(FRED_SERIES.keys()),
            default=list(FRED_SERIES.keys())  # all selected by default
        )

    # Only keep selected columns
    columns_to_plot = selected_indicators + ["sp500"]
    plot_df = full[["date"] + columns_to_plot].dropna()

    # --- Scale toggle ---
    scale_type = st.radio("Scale Type", ["Raw", "Log", "Z-Score"])

    working_df = plot_df.copy()

    if scale_type == "Log":
        # Replace zeros/negatives with NaN (log scale requires > 0)
        for col in columns_to_plot:
            working_df[col] = working_df[col].apply(lambda x: x if x > 0 else None)
            working_df[col] = working_df[col].apply(lambda x: None if pd.isna(x) else float(x))
    elif scale_type == "Z-Score":
        for col in columns_to_plot:
            col_mean = working_df[col].mean()
            col_std = working_df[col].std()
            working_df[col] = (working_df[col] - col_mean) / col_std

    # Melt for Altair plotting
    long_df = pd.melt(working_df, id_vars="date", var_name="indicator", value_name="value")
    long_df.dropna(inplace=True)

    y_scale = alt.Scale(type="log") if scale_type == "Log" else alt.Scale(type="linear")

    chart = alt.Chart(long_df).mark_line().encode(
        x="date:T",
        y=alt.Y("value:Q", scale=y_scale),
        color="indicator:N",
        tooltip=["date:T", "indicator:N", "value:Q"]
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # --- Correlation Heatmap ---
    st.subheader("Correlation Heatmap (Pearson)")

    corr = full.drop(columns=["date"]).corr(method="pearson")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr[["sp500"]].T, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

else:
    st.warning("No data available for selected indicator or S&P 500.")