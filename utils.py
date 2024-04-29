from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import pytz
from arcgis.features import FeatureLayer
import plotly.graph_objects as go
import numpy as np


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


# Function to convert Unix timestamp to UTC datetime
def convert_to_utc(timestamp):
    return datetime.utcfromtimestamp(timestamp // 1000).replace(tzinfo=pytz.utc)


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
    custom_data,
    additional_formatting=None,
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
        custom_data=custom_data,
    )
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title, showgrid=False),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend_title=None,
    )
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_yaxes(tickformat=format)
    fig.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        tickangle=tickangle,
    )
    fig.update_layout(additional_formatting)
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
    color,
    color_sequence,
    orders,
    y_title,
    x_title,
    custom_data,
    hovertemplate,
    hovermode,
    format,
    name=None,
    additional_formatting=None,
    orientation=None,
    facet=None,
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
        custom_data=custom_data,
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
    # fig.for_each_yaxis(lambda yaxis: yaxis.update(tickfont = dict(color = 'rgba(0,0,0,0)')), secondary_y=True)
    fig.update_yaxes(
        col=2, row=1, showticklabels=False, tickfont=dict(color="rgba(0,0,0,0)"), title=None
    )
    fig.update_yaxes(
        col=3, row=1, showticklabels=False, tickfont=dict(color="rgba(0,0,0,0)"), title=None
    )
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
    custom_data=None,
    additional_formatting=None,
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
        custom_data=custom_data,
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(
        yaxis=dict(tickformat=format, hoverformat=format, title=y_title),
        xaxis=dict(title=x_title),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend_title=None,
        legend=dict(
            orientation="h",
            entrywidth=200,
            # entrywidthmode="fraction",
            yanchor="bottom",
            y=1.2,
            xanchor="right",
            x=0.8,
        ),
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, tickformat=format))
    fig.update_yaxes(
        col=2, row=1, showticklabels=False, tickfont=dict(color="rgba(0,0,0,0)"), title=None
    )
    fig.update_yaxes(
        col=3, row=1, showticklabels=False, tickfont=dict(color="rgba(0,0,0,0)"), title=None
    )
    # fig.update_yaxes(col=4,row=1, showticklabels=False,tickfont = dict(color = 'rgba(0,0,0,0)'), title=None)
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_layout(additional_formatting)
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
    custom_data=None,
    additional_formatting=None,
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
        legend_title=None,
    )
    fig.update_yaxes(autorangeoptions=dict(include=0))
    fig.add_trace(px.line(df, x=x, y=y2, color_discrete_sequence=["#208385"]).data[0])
    fig.data[legend_number].name = legend_otherline
    fig.data[legend_number].showlegend = True
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_layout(additional_formatting)
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
    custom_data=None,
    additional_formatting=None,
):
    fig = px.area(
        df,
        x=x,
        y=y,
        color=color,
        line_group=line_group,
        color_discrete_sequence=color_sequence,
        custom_data=custom_data,
    )
    fig.update_layout(
        yaxis=dict(tickformat=format, hoverformat=format, title=y_title),
        xaxis=dict(title=x_title, tickformat=format, showgrid=False),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend_title=None,
    )
    fig.update_traces(hovertemplate=hovertemplate)
    config = {"displayModeBar": False}
    fig.update_layout(additional_formatting)
    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )

def create_dropdown_bar_chart(df, path_html, dropdown_column, x, y, color_sequence, orders,
                              x_title, y_title,
                              hovertemplate, hovermode,
                              title_text):
    """
    Create an interactive bar chart with a dropdown menu.

    Args:
    - df (DataFrame): The DataFrame containing the data.
    - path_html (str): The path to save the HTML file.
    - dropdown_column (str): The column name to be used for dropdown menu options.
    - x (str): The column name for the x-axis.
    - y (str): The column name for the y-axis.
    - color_sequence (list of str): List of color codes for each trace.
    - orders (dict): Dictionary specifying the order of dropdown menu options.
    - x_title (str): The title for the x-axis. Default is "Year".
    - y_title (str): The title for the y-axis. Default is "Median Household Income ($)".
    - hovertemplate (str): The hover template for the chart. Default is "%{y}".
    - hovermode (str): The hover mode for the chart. Default is "x unified".

    Returns:
    - None
    """
    fig = go.Figure()

    def create_trace(dff, name, color,custom_data):
        return go.Bar(
            x=dff[x],
            y=dff[y],
            name=name,
            hovertemplate=hovertemplate,
            marker_color=color,
            visible=False,
            customdata=dff[custom_data]
        )

    traces = []
    for i, region in enumerate(orders[dropdown_column]):
        query_string = f"{dropdown_column} == '{region}'"
        dff = df.query(query_string)
        trace = create_trace(dff, region, color_sequence[i],custom_data)
        traces.append(trace)

    fig.add_traces(traces)
    fig.update_traces(visible=True, selector=0)
    buttons = []
    for i, region in enumerate(orders[dropdown_column]):
        visible_state = [False] * len(orders[dropdown_column])
        visible_state[i] = True
        button = dict(
            label=region,
            method='update',
            args=[{'visible': visible_state}, {'title': f'Median Income in {region}'}]
        )
        buttons.append(button)

    fig.update_layout(
        barmode='group',
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode=hovermode,
        title=f'{title_text} {orders[dropdown_column][0]}',
        title_x=0.5
    )

    fig.layout.updatemenus = [{
        'buttons': buttons,
        'type': "buttons",
        'direction': "right",
        'active': 0,
        'x': 0.25,
        'y': 1.05
    }]

    fig.show()
    fig.write_html(path_html)

def create_stacked_bar_plot_with_dropdown(df,
                                  path_html,
                                  div_id,
                                  x,
                                   y,
                                    color_column,
                                     dropdown_column,
                                      color_sequence,
                                      sort_order,
                                      title_text,
                                       y_title,
                                        x_title,
                                         hovertemplate,
                                          hovermode,
                                           format,
                                           custom_data=None,
                                            additional_formatting = None):
    config = {"displayModeBar": False}
    years = df[x].unique()
    categories = df[color_column].unique()
    categories =sorted(categories, key=lambda x: sort_order.index(x))
    print(categories)
    second_categories = df[dropdown_column].unique()

    values = {}
    for second_category in second_categories:
        values[second_category] = []
        for category in categories:
            #values[second_category].append(df[df[dropdown_column]==second_category].loc[df[color_column]==category, y].tolist())
            filtered_df = df[(df[dropdown_column] == second_category) & (df[color_column] == category)]
            y_values = filtered_df[y].tolist()
            category_values = filtered_df[color_column].tolist()
            values[second_category].append([y_values, category_values])
    # Create traces for each category
    traces = []
    print(values)
    df_custom_data = pd.DataFrame(categories, columns=['categories'])
    my_array = np.stack(categories)
    custom_data_list = []
    print(my_array)
    for i, category in enumerate(categories):
        print(values[second_categories[0]][i][0])
        trace = go.Bar(
            x=years,
            y=values[second_categories[0]][i][0],  # Default to the first second category
            name=category,
            marker=dict(color=color_sequence[i]),
            customdata=values[second_categories[0]][i][1],
            
            hovertemplate=hovertemplate
        )
        #custom_data_list.append(category)
        traces.append(trace)

    # Layout
    layout = go.Layout(
        title=title_text,
        xaxis=dict(title='Year'),
        yaxis=dict(title='Values'),
        updatemenus=[
            dict(
                buttons=list([
                    dict(label=second_category,
                         method='update',
                         args=[{'y': [values[second_category][i] for i in range(len(categories))]},
                               {'yaxis': {'title': 'Values'}}])
                    for second_category in second_categories
                ]),
                direction='right',
                type='buttons',
                showactive=True,
                x=0.1,
                xanchor='left',
                y=1.05,
                yanchor='top'
            ),
        ]
    )

    # Create the figure
    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(barmode='stack')
    fig.update_layout(
        yaxis=dict(tickformat=format, hoverformat=format, title=y_title),
        xaxis=dict(title=x_title),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend_title=None
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, tickformat=format))
    # fig.for_each_yaxis(lambda yaxis: yaxis.update(tickfont = dict(color = 'rgba(0,0,0,0)')), secondary_y=True)

    fig.update_xaxes(tickformat=".0f")
    #print(custom_data_list)
    #fig.update_traces(customdata=custom_data_list)

    fig.update_layout(additional_formatting)

    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )


