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

###############################################################################
# Settings
DF_NAME='fato_av_ppg'
TABLE_NAME='FATO_CAPES_AVALIACAO_PPG'
PREVIEW=1000

###############################################################################
# Data lookup functions
def lookup_data(data_src, since=0, until=0, limit=100):

    # Lookup data
    df_len = DWO.query(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    df_len = df_len.iloc[0]['count']

    df = DWO.query(f"SELECT * FROM {TABLE_NAME} LIMIT {limit}")

    # Transform data
    # Lookup data

    return (df, df_len)

###############################################################################
# DASBOARD DATA LOOKUP
df, df_len = lookup_data(DWO)

###############################################################################
# Input Objects (parameters)

###############################################################################
# Layout Objects
reg_counter = daq.LEDDisplay(id=DF_NAME+'-reg-counter',
                             label="Registros",
                             labelPosition='bottom',
                             value="0")

columns_counter = daq.LEDDisplay(id=DF_NAME+'-attr-counter',
                             label="Atributos",
                             labelPosition='bottom',
                             value="0")
download_buttons = dbc.ButtonGroup(
    [html.A(dbc.Button("CSV", color="success", id=DF_NAME+'-csv-btn'),
           id=DF_NAME+'-csv-A', download=DF_NAME+".csv"),

     html.A(dbc.Button("ODS", color="success", id=DF_NAME+'-ods-btn'),
           id=DF_NAME+'-ods-A', download=DF_NAME+".ods"),

     html.A(dbc.Button("XLS", color="success", id=DF_NAME+'-xls-btn'),
           id=DF_NAME+'-xls-A', download=DF_NAME+".xlsx"),

    ],
)
filter_form_object = dbc.FormGroup([

    dbc.Label(f'Preview {PREVIEW if PREVIEW <= df_len else df_len} registros',
              id=DF_NAME+'-slider-label',
              html_for=DF_NAME+'-slider'
             ),

    dcc.Slider(id=DF_NAME+'-slider',
               min=1,
               max=df_len,
               value=PREVIEW if PREVIEW <= df_len else df_len
              ),
])

table_object = html.Div(id=DF_NAME+'-table-obj')

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

    # Filters form row
    dbc.Row([dbc.Col(filter_form_object)
            ]),

    # Table row
    dbc.Row([dbc.Col(table_object)
            ]),
]

###############################################################################
# Callbacks
@app.callback(Output(DF_NAME+'-table-obj', 'children'),
             [Input(DF_NAME+'-slider', 'value'),])
def update_table_object(value):

    # Parse parameters

    # Lookup data
    df, df_len = lookup_data(DWO, limit=value)

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

@app.callback(Output(DF_NAME+'-slider-label', 'children'),
             [Input(DF_NAME+'-slider', 'value'),])
def update_slider_object(value):
    return f'Preview {value if value <= df_len else df_len} registros'

@app.callback(Output(DF_NAME+'-reg-counter', 'value'),
             [Input(DF_NAME+'-csv-btn', 'n_clicks'),])
def update_reg_counter(n_clicks):
    return str(df_len)

@app.callback(Output(DF_NAME+'-attr-counter', 'value'),
             [Input(DF_NAME+'-csv-btn', 'n_clicks'),])
def update_attr_counter(n_clicks):
    return str(len(df.columns))

@app.callback(
    Output(DF_NAME+'-csv-A', 'href'),
    [Input(DF_NAME+'-csv-btn', 'n_clicks')])
def update_download_csv(n_clicks):

    # Export CVS
    csv_string = df.to_csv(index=False, encoding='utf-8', sep=';')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output(DF_NAME+'-xls-A', 'href'),
    [Input(DF_NAME+'-xls-btn', 'n_clicks')])
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
    Output(DF_NAME+'-ods-A', 'href'),
    [Input(DF_NAME+'-ods-btn', 'n_clicks')])
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

