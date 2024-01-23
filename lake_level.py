import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime, timedelta

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='lake-level-chart'),
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds
        n_intervals=0
    ),
    html.Label('Select Time Range:'),
    dcc.Dropdown(
        id='time-range-dropdown',
        options=[
            {'label': 'One Month', 'value': 30},
            {'label': 'One Year', 'value': 365},
            {'label': 'Ten Years', 'value': 3650},
        ],
        value=365,  # default value is one year
    ),
])

def get_usgs_data(days):
    site_number = 10337000
    
    # Calculate the start and end dates based on the selected time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    url = f'https://waterservices.usgs.gov/nwis/iv/?format=json&sites={site_number}&parameterCd=00065&startDT={start_date_str}&endDT={end_date_str}'

    response = requests.get(url)
    data = response.json()

    time_series_data = data['value']['timeSeries'][0]['values'][0]['value']

    df = pd.DataFrame(time_series_data)
    df['value'] = pd.to_numeric(df['value'])
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    df['value'] = df['value'] + 6220
    return df

@app.callback(
    Output('lake-level-chart', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('time-range-dropdown', 'value')]
)
def update_chart(n, selected_days):
    df = get_usgs_data(selected_days)

    fig = px.line(df, x='dateTime', y='value', title='Lake Tahoe Water Level')
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Water Level (ft)')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
