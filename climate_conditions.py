import pandas as pd
import plotly.express as px
from arcgis.features import FeatureLayer

# from pathlib import Path
# from arcgis import GIS
# import statsmodel


def get_fs_data(service_url):
    feature_layer = FeatureLayer(service_url)
    query_result = feature_layer.query()
    # Convert the query result to a list of dictionaries
    feature_list = query_result.features
    # Create a pandas DataFrame from the list of dictionaries
    all_data = pd.DataFrame([feature.attributes for feature in feature_list])
    # return data frame
    return all_data


def trendline(path_html, service_url, x, y, color, x_title, y_title):
    df = get_fs_data(service_url)
    df = df.sort_values(by=x)
    config = {"displayModeBar": False}
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=["#023f64", "#7ebfb5", "#a48352", "#fc9a61", "#A48794", "#b83f5d"],
    )
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title),
        hovermode="x unified",
        template="plotly_white",
    )
    fig.write_html(config=config, file=path_html)


def scatterplot(path_html, service_url, x, y1, y2, x_title, y_title):
    df = get_fs_data(service_url)
    config = {"displayModeBar": False}
    fig = px.scatter(df, x=x, y=y1, trendline="ols", color_discrete_sequence=["black"])
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title),
        hovermode="x unified",
        template="plotly_white",
    )
    fig.add_trace(px.line(df, x=x, y=y2, color_discrete_sequence=["#208385"]).data[0])
    fig.write_html(config=config, file=path_html)
