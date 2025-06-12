import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from config import DB_PATH, FRED_SERIES
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
from charts import make_indicator_chart

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

    st.subheader(f"{selected_series} vs. S&P 500")
    first_scale_type = st.radio(
        "Scale Type (Single Indicator)", ["Raw", "Log", "Z-Score"], key="single_chart_scale"
    )

    first_df = merged.copy()
    if first_scale_type == "Log":
        for col in ["value_macro", "value_sp500"]:
            first_df[col] = first_df[col].apply(lambda x: x if x > 0 else None)
    elif first_scale_type == "Z-Score":
        for col in ["value_macro", "value_sp500"]:
            mean = first_df[col].mean()
            std = first_df[col].std()
            first_df[col] = (first_df[col] - mean) / std

    line_chart = alt.Chart(first_df.dropna()).mark_line().encode(
        x="date:T",
        y=alt.Y("value_macro:Q", title=selected_series),
        color=alt.value("#1f77b4")
    ) + alt.Chart(first_df.dropna()).mark_line().encode(
        x="date:T",
        y=alt.Y("value_sp500:Q", title="S&P 500"),
        color=alt.value("#ff7f0e")
    )

    st.altair_chart(line_chart, use_container_width=True)

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

    chart = make_indicator_chart(long_df, scale_type)
    st.altair_chart(chart, use_container_width=True)

    # --- Correlation Heatmap ---
    st.subheader("Correlation Heatmap (Pearson)")

    corr = full.drop(columns=["date"]).corr(method="pearson")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        corr[["sp500"]].T,
        annot=True,
        cmap="cividis",  # colorblind-friendly
        cbar_kws={"label": "Correlation"},
        annot_kws={"size": 10, "weight": "bold"},
        linewidths=0.5,
        linecolor="black",
        ax=ax
    )
    ax.set_title("Correlation of S&P 500 with Other Indicators", fontsize=14)
    st.pyplot(fig)

else:
    st.warning("No data available for selected indicator or S&P 500.")