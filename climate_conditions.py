from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import requests

from utils import get_fs_data, read_file, scatterplot, trendline, stackedbar

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
        sort="Year",
        orders=None,
        x_title="Year",
        y_title="Amount of CO2 (MT CO2e)",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=True,
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
        xaxis=dict(title="Year", showgrid=False),
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


def calcAQI(Cp, Ih, Il, BPh, BPl):
    a = Ih - Il
    b = BPh - BPl
    c = Cp - BPl
    val = round((a / b) * c + Il)
    return val


def get_data_purple_air():
    df = read_file("data/daily_averaged_values.csv")
    df["AQI"] = np.where(
        df["daily_mean_25pm"] > 350.5,
        calcAQI(df["daily_mean_25pm"], 500, 401, 500.4, 350.5),
        np.where(
            df["daily_mean_25pm"] > 250.5,
            calcAQI(df["daily_mean_25pm"], 400, 301, 350.4, 250.5),
            np.where(
                df["daily_mean_25pm"] > 150.5,
                calcAQI(df["daily_mean_25pm"], 300, 201, 250.4, 150.5),
                np.where(
                    df["daily_mean_25pm"] > 55.5,
                    calcAQI(df["daily_mean_25pm"], 200, 151, 150.4, 55.5),
                    np.where(
                        df["daily_mean_25pm"] > 35.5,
                        calcAQI(df["daily_mean_25pm"], 150, 101, 55.4, 35.5),
                        np.where(
                            df["daily_mean_25pm"] > 12.1,
                            calcAQI(df["daily_mean_25pm"], 100, 51, 35.4, 12.1),
                            np.where(
                                df["daily_mean_25pm"] >= 0,
                                calcAQI(df["daily_mean_25pm"], 50, 0, 12, 0),
                                9999999,
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
    df["moving_avg"] = df["AQI"].rolling(window=7).mean()
    # df["time_stamp"] = pd.to_datetime(df["time_stamp"])
    # df.set_index('time_stamp', inplace=True)
    # weekly_avg = df.resample('W').mean().reset_index()
    return df


def plot_purple_air(df):
    trendline(
        df,
        path_html="html/1.2(a)_Purple_Air.html",
        div_id="1.2.a_Purple_Air",
        x="time_stamp",
        y="moving_avg",
        color=None,
        color_sequence=["#023f64", "#7ebfb5", "#a48352", "#fc9a61", "#A48794", "#b83f5d"],
        sort="time_stamp",
        orders=None,
        x_title="Time",
        y_title="AQI (rolling average)",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=False,
    )


def get_data_lake_level(days):
    site_number = 10337000

    # Calculate the start and end dates based on the selected time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={site_number}&parameterCd=00065&startDT={start_date_str}&endDT={end_date_str}"

    response = requests.get(url)
    data = response.json()

    time_series_data = data["value"]["timeSeries"][0]["values"][0]["value"]

    df = pd.DataFrame(time_series_data)
    df["dateTime"] = pd.to_datetime(df["dateTime"], utc=True)
    df["value"] = pd.to_numeric(df["value"])
    df["value"] = df["value"] + 6220
    weekly = df.groupby(pd.Grouper(key="dateTime", freq="W"))["value"].mean().reset_index()
    return weekly


def plot_lake_level(df):
    trendline(
        df,
        path_html="html/1.3(a)_Lake_Level.html",
        div_id="1.3.a_Lake_Level",
        x="dateTime",
        y="value",
        color=None,
        color_sequence=["#023f64"],
        sort="dateTime",
        orders=None,
        x_title="Time",
        y_title="Water Level (ft)",
        hovertemplate="%{y:,.0f}",
        format=",.0f",
        markers=False,
    )


def get_data_lake_temp():
    lakeTempURL = "https://tepfsail50.execute-api.us-west-2.amazonaws.com/v1/report/ns-station-range?rptdate=20240130&rptend=20240202&id=4"
    response = requests.get(lakeTempURL)
    df = pd.DataFrame(response.json())
    df["LS_Temp_Avg"] = df["LS_Temp_Avg"].astype(float)
    return df


def plot_lake_temp(df):
    trendline(
        df,
        path_html="html/1.3(b)_Lake_Temp.html",
        div_id="1.3.b_Lake_Temp",
        x="TmStamp",
        y="LS_Temp_Avg",
        color=None,
        color_sequence=["#023f64"],
        sort="TmStamp",
        orders=None,
        x_title="Time",
        y_title="Average Lake Surface Temperature ",
        format=".1f",
        hovertemplate="%{y:.2f}",
        markers=False,
    )

def get_data_precip():
    # snowlab precip data
    url = "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/145"
    data = get_fs_data(url)

    # cast to float
    data['Pct_of_Precip_as_Snow'] = data['Pct_of_Precip_as_Snow'].astype(float)
    data['Pct_of_Precip_as_Rain'] = data['Pct_of_Precip_as_Rain'].astype(float)

    # new fields for total snow and rain from pct fields
    data['Daily_Precip_Rain_mm'] = data.Full_Day_Total_Precip_mm * (data.Pct_of_Precip_as_Rain/100)
    data['Daily_Precip_Snow_mm'] = data.Full_Day_Total_Precip_mm * (data.Pct_of_Precip_as_Snow/100)

    # group by year and sum the daily precip fields
    dfYearly = data.groupby('Year').agg({'Daily_Precip_Rain_mm': 'sum', 'Daily_Precip_Snow_mm': 'sum'}).reset_index()
    dfYearly['Total_Precip_mm'] = dfYearly['Daily_Precip_Rain_mm'] + dfYearly['Daily_Precip_Snow_mm']

    # create percent fields
    dfYearly['Pct_of_Precip_as_Rain'] = (dfYearly['Daily_Precip_Rain_mm'] / dfYearly['Total_Precip_mm']) * 100
    dfYearly['Pct_of_Precip_as_Snow'] = (dfYearly['Daily_Precip_Snow_mm'] / dfYearly['Total_Precip_mm']) * 100

    # drop all years before 1987 (no data)
    df = dfYearly[dfYearly['Year'] >= 1987]
    return df

def plot_precip(df):
    stackedbar(
        df,
        path_html="html/1.3(d)_Precip.html",
        div_id="1.3.d_Precip",
        x="Year",
        y=["Pct_of_Precip_as_Rain", "Pct_of_Precip_as_Snow"],
        facet=None,
        color=None,
        color_sequence=["#BFD7ED", "#60A3D9"],
        orders=None,
        x_title="Year",
        y_title="% of Precipitation",
        hovertemplate="%{y:,.0f}",
        hovermode="x unified",
        orientation=None,
        format=",.0f"
    )
