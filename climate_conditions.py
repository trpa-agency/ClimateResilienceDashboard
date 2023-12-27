import plotly.express as px

from utils import get_fs_data, trendline

# from pathlib import Path
# from arcgis import GIS
# import statsmodel


def get_data_1_1_a():
    return get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/124"
    )


def plot_1_1_a(df):
    trendline(
        df,
        path_html="html/1.1(a)_GHG.html",
        x="Year",
        y="MT_CO2",
        color="Category",
        color_sequence=["#023f64", "#7ebfb5", "#a48352", "#fc9a61", "#A48794", "#b83f5d"],
        x_title="Year",
        y_title="Amount of CO2",
    )


def get_data_1_3_c():
    return get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/125"
    )


# A pretty specific graph
def plot_1_3_c(df):
    config = {"displayModeBar": False}
    fig = px.scatter(
        df, x="year", y="annual_average", trendline="ols", color_discrete_sequence=["black"]
    )
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        yaxis=dict(title="Secchi Depth"), xaxis=dict(title="Year"), template="plotly_white"
    )
    fig.add_trace(
        px.line(df, x="year", y="F5_year_average", color_discrete_sequence=["#208385"]).data[0]
    )
    fig.write_html(config=config, file="html/1.3(c)_Secchi_Depth.html")
