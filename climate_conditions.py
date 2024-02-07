import plotly.express as px

from utils import get_fs_data, scatterplot, trendline

# from pathlib import Path
# from arcgis import GIS
# import statsmodel


def get_data_greenhouse_gas():
    return get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/125"
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
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/126"
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


def get_air_quality():
    data = get_fs_data("https://maps.trpa.org/server/rest/services/LTInfo_Monitoring/MapServer/46")
    df = data[data["Include_in_Trend_Analysis"] == "Yes"]
    return df


def plot_air_quality(df):
    # CO
    co = df[df["Pollutant"] == "CO"]
    scatterplot(
        df=co,
        path_html="html/1.2(a)_Air_Quality_CO.html",
        div_id="1.2.a_Air_Quality_CO",
        x="Year",
        y="Value",
        y2="Threshold_Value",
        color="Site",
        color_sequence=["#FC9A62", "#F9C63E", "#632E5A", "#A48352", "#BCEDB8"],
        y_title="Highest 8-Hour Average Concentration of CO (ppm)",
        x_title="Year",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        legend_number=5,
        legend_otherline="Threshold",
    )
    # O3
    o3 = df[df["Pollutant"] == "O3"]
    scatterplot(
        df=o3,
        path_html="html/1.2(a)_Air_Quality_O3.html",
        div_id="1.2.a_Air_Quality_O3",
        x="Year",
        y="Value",
        y2="Threshold_Value",
        color="Site",
        color_sequence=[
            "#FC9A62",
            "#7EBFB5",
            "#632E5A",
            "#023F64",
            "#A48352",
            "#F9C63E",
            "#B83F5D",
            "#749099",
            "#A48794",
        ],
        y_title="Highest 1-Hour Average Concentration of Ozone (ppm)",
        x_title="Year",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        legend_number=10,
        legend_otherline="Threshold",
    )
    # PM10
    pm10 = df[(df["Pollutant"] == "PM10") & (df["Statistic"] == "HIGH 24 HR")]
    scatterplot(
        df=pm10,
        path_html="html/1.2(a)_Air_Quality_PM10.html",
        div_id="1.2.a_Air_Quality_PM10",
        x="Year",
        y="Value",
        y2="Threshold_Value",
        color="Site",
        color_sequence=["#FC9A62"],
        y_title="Highest 24-Hour Average Concentration of PM10",
        x_title="Year",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        legend_number=2,
        legend_otherline="Threshold",
    )
    # PM2.5
    pm25 = df[df["Pollutant"] == "PM2.5"]
    scatterplot(
        df=pm25,
        path_html="html/1.2(a)_Air_Quality_PM2.5.html",
        div_id="1.2.a_Air_Quality_PM2.5",
        x="Year",
        y="Value",
        y2="Threshold_Value",
        color="Site",
        color_sequence=["#FC9A62"],
        y_title="3 Year 24-Hour Average Concentration of PM2.5",
        x_title="Year",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        legend_number=2,
        legend_otherline="Threshold",
    )
