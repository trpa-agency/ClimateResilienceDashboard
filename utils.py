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


# Gets data with query from the TRPA server
def get_fs_data_query(service_url, query_params):
    feature_layer = FeatureLayer(service_url)
    query_result = feature_layer.query(query_params)
    # Convert the query result to a list of dictionaries
    feature_list = query_result.features
    # Create a pandas DataFrame from the list of dictionaries
    all_data = pd.DataFrame([feature.attributes for feature in feature_list])
    # return data frame
    return all_data


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


# Gets spatially enabled dataframe from TRPA server
def get_fs_data_spatial(service_url):
    feature_layer = FeatureLayer(service_url)
    query_result = feature_layer.query().sdf
    return query_result


# Gets spatially enabled dataframe with query
def get_fs_data_spatial_query(service_url, query_params):
    feature_layer = FeatureLayer(service_url)
    query_result = feature_layer.query(query_params).sdf
    return query_result


# Trendline
def trendline(
    df,
    path_html,
    div_id,
    x,
    y,
    color,
    color_sequence,
    sort,
    orders,
    x_title,
    y_title,
    format,
    hovertemplate,
    markers,
    hover_data,
    tickvals,
    ticktext,
    tickangle,
    hovermode,
):
    df = df.sort_values(by=sort)
    config = {"displayModeBar": False}
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=color_sequence,
        category_orders=orders,
        markers=markers,
        hover_data=hover_data,
    )
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title, showgrid=False),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
    )
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_yaxes(tickformat=format)
    fig.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        tickangle=tickangle,
    )
    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )


# Stacked Percent Bar chart
def stackedbar(
    df,
    path_html,
    div_id,
    x,
    y,
    facet,
    color,
    color_sequence,
    orders,
    y_title,
    x_title,
    hovertemplate,
    hovermode,
    orientation,
    format,
    additional_formatting=None,
    facet_row=None,
):
    config = {"displayModeBar": False}
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode="stack",
        facet_col=facet,
        facet_row=facet_row,
        color_discrete_sequence=color_sequence,
        category_orders=orders,
        orientation=orientation,
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(
        yaxis=dict(tickformat=format, hoverformat=format, title=y_title),
        xaxis=dict(title=x_title),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend_title=None,
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, tickformat=format))
    fig.update_xaxes(tickformat=".0f")
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_layout(additional_formatting)

    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )


# Grouped Percent Bar chart
def groupedbar_percent(
    df,
    path_html,
    div_id,
    x,
    y,
    facet,
    color,
    color_sequence,
    orders,
    y_title,
    x_title,
    hovertemplate,
    hovermode,
    format,
):
    config = {"displayModeBar": False}
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode="group",
        facet_col=facet,
        color_discrete_sequence=color_sequence,
        category_orders=orders,
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(
        yaxis=dict(tickformat=format, hoverformat=format, title=y_title),
        xaxis=dict(title=x_title),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend_title=None,
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, tickformat=format))
    fig.update_traces(hovertemplate=hovertemplate)

    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )


# Scatterplot
def scatterplot(
    df,
    path_html,
    div_id,
    x,
    y,
    y2,
    color,
    color_sequence,
    y_title,
    x_title,
    hovertemplate,
    hovermode,
    legend_number,
    legend_otherline,
):
    config = {"displayModeBar": False}
    fig = px.scatter(
        df,
        x=x,
        y=y,
        trendline="ols",
        color=color,
        color_discrete_sequence=color_sequence,
        trendline_scope="overall",
        trendline_color_override="black",
    )
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title, showgrid=False),
        template="plotly_white",
        hovermode=hovermode,
        dragmode=False,
    )
    fig.update_yaxes(autorangeoptions=dict(include=0))
    fig.add_trace(px.line(df, x=x, y=y2, color_discrete_sequence=["#208385"]).data[0])
    fig.data[legend_number].name = legend_otherline
    fig.data[legend_number].showlegend = True
    fig.update_traces(hovertemplate=hovertemplate)
    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )


# Stacked Area Chart
def stacked_area(
    df,
    path_html,
    div_id,
    x,
    y,
    color,
    line_group,
    color_sequence,
    x_title,
    y_title,
    hovermode,
    format,
    hovertemplate,
):
    fig = px.area(
        df,
        x=x,
        y=y,
        color=color,
        line_group=line_group,
        color_discrete_sequence=color_sequence,
    )
    fig.update_layout(
        yaxis=dict(tickformat=format, hoverformat=format, title=y_title),
        xaxis=dict(title=x_title, tickformat=format, showgrid=False),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend=dict(
            orientation="h",
            entrywidth=200,
            # entrywidthmode="fraction",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.8,
        ),
    )
    fig.update_traces(hovertemplate=hovertemplate)

    config = {"displayModeBar": False}

    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )
