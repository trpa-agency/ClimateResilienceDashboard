import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='lake-level-chart'),
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds
        n_intervals=0
    ),
])

def get_usgs_data():
    # Replace 'SITE_NUMBER' with the actual USGS site number for Lake Tahoe
    site_number = 10337000
    
    # USGS API URL for Lake Tahoe site
    url = f'https://waterservices.usgs.gov/nwis/iv/?format=json&sites={site_number}&parameterCd=00065'

    # Make a request to the USGS API
    response = requests.get(url)
    data = response.json()

    # Extract relevant data
    time_series_data = data['value']['timeSeries'][0]['values'][0]['value']

    # Create a DataFrame
    df = pd.DataFrame(time_series_data)

    # Convert data types
    df['value'] = pd.to_numeric(df['value'])
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    df['value'] = df['value'] + 6220
    return df


@app.callback(
    Output('lake-level-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_chart(n):
    df = get_usgs_data()

    # Create a line chart using Plotly Express
    fig = px.line(df, x='dateTime', y='value', title='Lake Tahoe Water Level')
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Water Level (ft)')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
