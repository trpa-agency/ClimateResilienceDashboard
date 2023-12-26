import plotly.express as px

from utils import read_file


def get_data_3_2_a():
    return read_file("data/EnergyMix_long.csv")


def plot_3_2_a(df):
    stackbar_percent(
        df,
        path_html="html/3.2(a)_EnergyMix.html",
        x="Year",
        y="Share",
        facet="Source",
        color="Type",
        y_title="% of Renewable Energy by Share of Total",
        x_title="Year",
    )


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
def groupedbar_percent(path_html, path_file, x, y, facet, color, y_title, x_title):
    df = read_file(path_file)
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
