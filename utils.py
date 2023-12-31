from pathlib import Path

import pandas as pd
import plotly.express as px
from arcgis.features import FeatureLayer


# Reads in csv file
def read_file(path_file):
    p = Path(path_file)
    p.expanduser()
    data = pd.read_csv(p)
    return data


# Gets data from the TRPA server
def get_fs_data(service_url):
    feature_layer = FeatureLayer(service_url)
    query_result = feature_layer.query()
    # Convert the query result to a list of dictionaries
    feature_list = query_result.features
    # Create a pandas DataFrame from the list of dictionaries
    all_data = pd.DataFrame([feature.attributes for feature in feature_list])
    # return data frame
    return all_data


# Trendline
def trendline(df, path_html, x, y, color, color_sequence, x_title, y_title):
    df = df.sort_values(by=x)
    config = {"displayModeBar": False}
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=color_sequence,
    )
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title),
        hovermode="x",
        template="plotly_white",
    )
    fig.write_html(config=config, file=path_html)


# Stacked Percent Bar chart
def stackbar_percent(df, path_html, x, y, facet, color, y_title, x_title):
    config = {"displayModeBar": False}
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode="stack",
        facet_col=facet,
        color_discrete_sequence=["#208385", "#FC9A62"],
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(
        yaxis=dict(tickformat=".0%", hoverformat=".0%", title=y_title),
        xaxis=dict(title=x_title),
        hovermode="x",
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, tickformat=".0%"))
    fig.update_traces(hovertemplate="Year: %{x} <br>Percentage: %{y}")

    fig.write_html(config=config, file=path_html)


# Grouped Percent Bar chart
def groupedbar_percent(df, path_html, x, y, facet, color, y_title, x_title):
    config = {"displayModeBar": False}
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode="group",
        facet_col=facet,
        color_discrete_sequence=["#208385", "#FC9A62"],
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(
        yaxis=dict(tickformat=".0%", hoverformat=".0%", title=y_title),
        xaxis=dict(title=x_title),
        hovermode="x",
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, tickformat=".0%"))
    fig.update_traces(hovertemplate="Year: %{x} <br>Percentage: %{y}")

    fig.write_html(config=config, file=path_html)
