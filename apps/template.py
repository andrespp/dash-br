import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_table
import urllib
import pandas as pd
from app import app, DWO
from dash.dependencies import Input, Output

###############################################################################
# Sample Data
sample = {'country':['Brazil', 'Russia','India', 'China', 'South Africa'],
         'population':[200, 144, 1252, 1357, 55],
         'area':[8515767, 17098242, 3287590, 9596961, 1221037],
         'capital':['Brasilia', 'Moscow', 'New Delhi', 'Beijing', 'Pretoria'],
}
DF_NAME='template'

###############################################################################
# Settings

###############################################################################
# Input Objects (parameters)

###############################################################################
# Layout Objects
reg_counter = daq.LEDDisplay(id='reg-counter',
                             label="Registros",
                             labelPosition='bottom',
                             value="0")

columns_counter = daq.LEDDisplay(id='attr-counter',
                             label="Atributos",
                             labelPosition='bottom',
                             value="0")
download_buttons = dbc.ButtonGroup(
    [html.A(dbc.Button("CSV", color="success", id='csv-btn'),
           id='csv-A', download=DF_NAME+".csv"),

     dbc.Button("ODS", color="success"),
     dbc.Button("XLS", color="success"),
    ],
)
table_object = html.Div(id='table-obj')

###############################################################################
# Dasboard layout
layout = [

    # Gagets row
    dbc.Row([ dbc.Col(reg_counter,
                      className='d-flex justify-content-center'),

              dbc.Col(columns_counter,
                      className='d-flex justify-content-center'),

              dbc.Col(html.Div(download_buttons),
                      className='d-flex align-items-center justify-content-center'
                     ),
            ]),

    # Table row
    dbc.Row([dbc.Col(table_object)]),
]

###############################################################################
# Callbacks
@app.callback(Output(component_id='table-obj', component_property='children'),
             [Input(component_id='csv-btn', component_property='n_clicks'),])
def update_table_object(n_clicks):

    # Parse parameters

    # Lookup data
    #df = lookup_data(sample)

    # Plotly Table object
    figure = dash_table.DataTable()
    figure = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'center'},
)


    return figure

@app.callback(Output(component_id='reg-counter', component_property='value'),
             [Input(component_id='csv-btn', component_property='n_clicks'),])
def update_reg_counter(n_clicks):
    return str(len(df))

@app.callback(Output(component_id='attr-counter', component_property='value'),
             [Input(component_id='csv-btn', component_property='n_clicks'),])
def update_attr_counter(n_clicks):
    return str(len(df.columns))

@app.callback(
    Output(component_id='csv-A', component_property='href'),
    [Input(component_id='csv-btn', component_property='n_clicks')])
def update_download(n_clicks):

    # Export CVS
    csv_string = df.to_csv(index=False, encoding='utf-8', sep=';')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

###############################################################################
# Data lookup functions
def lookup_data(data_src, since=0, until=0):

    # Lookup data
    df = pd.DataFrame(data_src)

    # Transform data

    return df

###############################################################################
# DASBOARD DATA LOOKUP
df = lookup_data(sample)
