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

DF_NAME='fato_av_ppg'

###############################################################################
# Settings

###############################################################################
# Input Objects (parameters)

###############################################################################
# Layout Objects
reg_counter = daq.LEDDisplay(id='fato_av_ppg-reg-counter',
                             label="Registros",
                             labelPosition='bottom',
                             value="0")

columns_counter = daq.LEDDisplay(id='fato_av_ppg-attr-counter',
                             label="Atributos",
                             labelPosition='bottom',
                             value="0")
download_buttons = dbc.ButtonGroup(
    [html.A(dbc.Button("CSV", color="success", id='fato_av_ppg-csv-btn'),
           id='fato_av_ppg-csv-A', download=DF_NAME+".csv"),

     html.A(dbc.Button("ODS", color="success", id='fato_av_ppg-ods-btn'),
           id='fato_av_ppg-ods-A', download=DF_NAME+".ods"),

     html.A(dbc.Button("XLS", color="success", id='fato_av_ppg-xls-btn'),
           id='fato_av_ppg-xls-A', download=DF_NAME+".xlsx"),

    ],
)
table_object = html.Div(id='fato_av_ppg-table-obj')

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
@app.callback(Output('fato_av_ppg-table-obj', 'children'),
             [Input('fato_av_ppg-csv-btn', 'n_clicks'),])
def update_table_object(n_clicks):

    # Parse parameters

    # Lookup data
    #df = lookup_data(DWO)

    # Plotly Table object
    figure = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i,
                  "deletable": True, "selectable": True}
                         for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'center'},
        style_table={'overflowX': 'auto'},
        sort_action='native',
        sort_mode="multi",
        filter_action='native',
        page_size= 20,
    )

    return figure

@app.callback(Output('fato_av_ppg-reg-counter', 'value'),
             [Input('fato_av_ppg-csv-btn', 'n_clicks'),])
def update_reg_counter(n_clicks):
    return str(df_len)

@app.callback(Output('fato_av_ppg-attr-counter', 'value'),
             [Input('fato_av_ppg-csv-btn', 'n_clicks'),])
def update_attr_counter(n_clicks):
    return str(len(df.columns))

@app.callback(
    Output('fato_av_ppg-csv-A', 'href'),
    [Input('fato_av_ppg-csv-btn', 'n_clicks')])
def update_download_csv(n_clicks):

    # Export CVS
    csv_string = df.to_csv(index=False, encoding='utf-8', sep=';')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('fato_av_ppg-xls-A', 'href'),
    [Input('fato_av_ppg-xls-btn', 'n_clicks')])
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
    Output('fato_av_ppg-ods-A', 'href'),
    [Input('fato_av_ppg-ods-btn', 'n_clicks')])
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
def lookup_data(data_src, since=0, until=0, limit=100):

    # Lookup data
    df_len = DWO.query("SELECT COUNT(*) FROM FATO_CAPES_AVALIACAO_PPG")
    df_len = df_len.iloc[0]['count']

    df = DWO.query(f"SELECT * FROM FATO_CAPES_AVALIACAO_PPG LIMIT {limit}")

    # Transform data
    # Lookup data

    return (df, df_len)

###############################################################################
# DASBOARD DATA LOOKUP
df, df_len = lookup_data(DWO)
