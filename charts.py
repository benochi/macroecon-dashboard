import altair as alt

ACCESSIBLE_COLORS = [
    "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00",
    "#CC79A7", "#999999", "#000000", "#882255", "#44AA99", "#117733",
    "#332288", "#AA4499", "#DDCC77", "#88CCEE", "#117733", "#999933",
    "#661100", "#6699CC", "#888888", "#CC6677", "#DDDDDD", "#44AA99",
    "#882255", "#AA4499", "#332288", "#117733", "#999999", "#CC79A7"
]

def make_indicator_chart(df, scale_type="Raw"):
    y_scale = alt.Scale(type="log") if scale_type == "Log" else alt.Scale(type="linear")

    chart = alt.Chart(df).mark_line().encode(
        x="date:T",
        y=alt.Y("value:Q", scale=y_scale),
        color=alt.Color("indicator:N", scale=alt.Scale(range=ACCESSIBLE_COLORS)),
        tooltip=["date:T", "indicator:N", "value:Q"]
    ).interactive()

    return chart
