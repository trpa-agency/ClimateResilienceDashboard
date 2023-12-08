import pandas as pd
import plotly.express as px
from pathlib import Path

# Reads in csv file
def read_file(path_file):
    p = Path(path_file)
    p.expanduser()
    data = pd.read_csv(p)
    return data

# Stacked Percent Bar chart
def stackbar_percent(path_html, path_file, x, y, facet, color, y_title, x_title):
    df = read_file(path_file)
    config = {'displayModeBar': False}
    fig = px.bar(df, x=x, y=y, color=color, barmode="stack", facet_col=facet,
             color_discrete_sequence =["#208385","#FC9A62"])
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(
        yaxis = dict(
            tickformat = ".0%",
            hoverformat = ".0%",
            title = y_title
        ),
        xaxis = dict(
            title = x_title
        ),
        hovermode = "x"
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True,tickformat = ".0%"))
    fig.update_traces(hovertemplate='Year: %{x} <br>Percentage: %{y}')
    
    fig.write_html(config=config, file=path_html)

# Grouped Percent Bar chart
def groupedbar_percent(path_html, path_file, x, y, facet, color, y_title, x_title):
    df = read_file(path_file)
    config = {'displayModeBar': False}
    fig = px.bar(df, x=x, y=y, color=color, barmode="group", facet_col=facet,
             color_discrete_sequence =["#208385","#FC9A62"])
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(
        yaxis = dict(
            tickformat = ".0%",
            hoverformat = ".0%",
            title = y_title
        ),
        xaxis = dict(
            title = x_title
        ),
        hovermode = "x"
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True,tickformat = ".0%"))
    fig.update_traces(hovertemplate='Year: %{x} <br>Percentage: %{y}')
    
    fig.write_html(config=config, file=path_html)

