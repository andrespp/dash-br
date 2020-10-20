import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_table
import xlsxwriter
import urllib
import base64
import io
import pandas as pd
from app import app, DWO
from dash.dependencies import Input, Output

DF_NAME='dim_municipio'

###############################################################################
# Settings

###############################################################################
# Input Objects (parameters)

###############################################################################
# Layout Objects
reg_counter = daq.LEDDisplay(id='dim_municipio-reg-counter',
                             label="Registros",
                             labelPosition='bottom',
                             value="0")

columns_counter = daq.LEDDisplay(id='dim_municipio-attr-counter',
                             label="Atributos",
                             labelPosition='bottom',
                             value="0")
download_buttons = dbc.ButtonGroup(
    [html.A(dbc.Button("CSV", color="success", id='dim_municipio-csv-btn'),
           id='dim_municipio-csv-A', download=DF_NAME+".csv"),

     html.A(dbc.Button("ODS", color="success", id='dim_municipio-ods-btn'),
           id='dim_municipio-ods-A', download=DF_NAME+".ods"),

     html.A(dbc.Button("XLS", color="success", id='dim_municipio-xls-btn'),
           id='dim_municipio-xls-A', download=DF_NAME+".xlsx"),

    ],
)
table_object = html.Div(id='dim_municipio-table-obj')

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
@app.callback(Output('dim_municipio-table-obj', 'children'),
             [Input('dim_municipio-csv-btn', 'n_clicks'),])
def update_table_object(n_clicks):

    # Parse parameters

    # Lookup data
    df = lookup_data(DWO)

    # Plotly Table object
    figure = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i,
                  "deletable": True, "selectable": True}
                         for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'center'},
        sort_action='native',
        sort_mode="multi",
        filter_action='native',
        page_size= 20,
    )

    return figure

@app.callback(Output('dim_municipio-reg-counter', 'value'),
             [Input('dim_municipio-csv-btn', 'n_clicks'),])
def update_reg_counter(n_clicks):
    return str(len(df))

@app.callback(Output('dim_municipio-attr-counter', 'value'),
             [Input('dim_municipio-csv-btn', 'n_clicks'),])
def update_attr_counter(n_clicks):
    return str(len(df.columns))

@app.callback(
    Output('dim_municipio-csv-A', 'href'),
    [Input('dim_municipio-csv-btn', 'n_clicks')])
def update_download_csv(n_clicks):

    # Export CVS
    csv_string = df.to_csv(index=False, encoding='utf-8', sep=';')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('dim_municipio-xls-A', 'href'),
    [Input('dim_municipio-xls-btn', 'n_clicks')])
def update_download_xls(n_clicks):
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=DF_NAME)
    writer.save()
    xlsx_io.seek(0)
    # https://en.wikipedia.org/wiki/Data_URI_scheme
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    return href_data_downloadable

@app.callback(
    Output('dim_municipio-ods-A', 'href'),
    [Input('dim_municipio-ods-btn', 'n_clicks')])
def update_download_ods(n_clicks):
    ods_io = io.BytesIO()
    writer = pd.ExcelWriter(ods_io, engine='odf')
    df.to_excel(writer, sheet_name=DF_NAME)
    writer.save()
    ods_io.seek(0)
    # https://en.wikipedia.org/wiki/Data_URI_scheme
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(ods_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    return href_data_downloadable

###############################################################################
# Data lookup functions
def lookup_data(data_src, since=0, until=0):

    # Lookup data
    #df = pd.DataFrame(data_src)
    df = DWO.query("select * from dim_municipio")

    # Transform data

    return df

###############################################################################
# DASBOARD DATA LOOKUP
df = lookup_data(DWO)
