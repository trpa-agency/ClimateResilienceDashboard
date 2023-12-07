import pandas as pd
import plotly.express as px

def read_file(path_file):
    data = pd.read_csv(path_file)
    return data

def stackbar_percent(path_html, path_file, x, y, facet, color, y_title, x_title):
    df = read_file(path_file)
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
        )
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True,tickformat = ".0%"))
    fig.update_traces(hovertemplate='Year: %{x} <br>Percentage: %{y}')

    fig.write_html(path_html)

stackbar_percent("/Users/cahya/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/3.2(a)/EnergyMix.html", 
          "/Users/cahya/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/3.2(a)/EnergyMix_long.csv",
          "Year","Share","Source","Type","% of Renewable Energy by Share of Total","Year")

