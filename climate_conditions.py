import plotly.express as px

from utils import get_fs_data, trendline

# from pathlib import Path
# from arcgis import GIS
# import statsmodel


def get_data_greenhouse_gas():
    return get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/124"
    )


def plot_greenhouse_gas(df):
    trendline(
        df,
        path_html="html/1.1(a)_Greenhouse_Gas.html",
        div_id="1.1.a_greenhouse_gas",
        x="Year",
        y="MT_CO2",
        color="Category",
        color_sequence=["#023f64", "#7ebfb5", "#a48352", "#fc9a61", "#A48794", "#b83f5d"],
        x_title="Year",
        y_title="Amount of CO2 (MT CO2e)",
    )


def get_data_secchi_depth():
    return get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/125"
    )


# A pretty specific graph
def plot_secchi_depth(df):
    config = {"displayModeBar": False}
    fig = px.scatter(
        df, x="year", y="annual_average", trendline="ols", color_discrete_sequence=["black"]
    )
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        yaxis=dict(title="Secchi Depth (meters)"),
        xaxis=dict(title="Year"),
        template="plotly_white",
        hovermode="x unified",
        dragmode=False,
    )
    fig.update_yaxes(autorange="reversed", autorangeoptions=dict(include=0))
    fig.add_trace(
        px.line(df, x="year", y="F5_year_average", color_discrete_sequence=["#208385"]).data[0]
    )
    fig.data[0].name = "Annual Average"
    fig.data[0].showlegend = True
    fig.data[1].name = "Trendline"
    fig.data[1].showlegend = True
    fig.data[2].name = "5-Year Average"
    fig.data[2].showlegend = True
    fig.update_traces(hovertemplate="%{y:.2f}")
    fig.write_html(
        config=config,
        file="html/1.3(c)_Secchi_Depth.html",
        include_plotlyjs="directory",
        div_id="1.3.c_Secchi_Depth",
    )
