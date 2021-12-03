# dependencies
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.express as px

import io
import base64

# initialisation
app = dash.Dash('', external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# store uploaded data in an attempt to speed up application
airline_df = None
uploaded_filename = None

# set layouts
app.layout = html.Div([
        html.H1('Airline Reporting Carrier Ontime Performance'),
        html.H2('Average Monthly Delays Per Year'),
        html.Br(),
        dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=True
            ), 
        html.Span(id='upload-file-name'),
        html.Br(),
        html.H3('Select Delay Type'),
        dcc.Dropdown(options=[
                    { 'label' : 'Carrier Delay', 'value': 'CarrierDelay'},
                    { 'label' : 'Weather Delay', 'value': 'WeatherDelay'},
                    { 'label' : 'National Air System Delay', 'value': 'NASDelay'},
                ], id='type_of_delay'),
        html.Br(),
        html.H3('Select Year'),
        dcc.Slider(
            id='my-range-slider',
            min=2010,
            max=2020,
            step=1,
            value=2015
            ),
        html.Div(id='output-container-range-slider'),
        html.Br(),
        dcc.Graph(id='airline-data', figure={})
])

# callbacks
@app.callback(
    Output(component_id='upload-file-name', component_property='children'),
    Output(component_id='output-container-range-slider', component_property='children'),
    Output(component_id='airline-data', component_property='figure'),
    Input(component_id='my-range-slider', component_property='value'),
    Input(component_id='type_of_delay', component_property='value'),
    Input(component_id='upload-data', component_property='contents'),
    State(component_id='upload-data', component_property='filename')
)
def calldata(year, delay_type, uploaded_csv, csv_name):
    global airline_df
    global uploaded_filename

    if delay_type is None and uploaded_csv is not None:
        if airline_df is None:
            for index in range(0, len(uploaded_csv)):
                uploaded_filename = csv_name[index]
            return f'Uploaded file: {uploaded_filename}', year, {}

    if (delay_type and uploaded_csv ) is not None:
        # check is there is not an airline_df stored and store one if there isn't
        if airline_df is None:
            for index in range(0, len(uploaded_csv)):
                uploaded_airline_file = uploaded_csv[index]
                uploaded_filename = csv_name[index]
                file_type, file_in_base64 = uploaded_airline_file.split(',')
                decoded_file = base64.b64decode(file_in_base64)
                file_as_stream = io.StringIO(decoded_file.decode('unicode-escape'))
                airline_df = pd.read_csv(file_as_stream, encoding='ISO-8859-1')

        # filter the dataframe based on year and return
        filter_by_year = airline_df[airline_df['Year'] == year]
        monthly_av_carrier_delay = filter_by_year.groupby(['Month','Reporting_Airline']).mean().reset_index()
        figure = px.line(monthly_av_carrier_delay, x='Month', y=delay_type, color='Reporting_Airline')
        return f'Uploaded file: {uploaded_filename}', year, figure
    else:
        return '', year, {}

# run server
if __name__ == "__main__":
    app.run_server(debug=True)