import dash_bootstrap_components as dbc
import dash_daq as daq
import xlsxwriter
import urllib
import base64
import io
import pandas as pd
import traceback
from app import app, DWO
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc, html

###############################################################################
# Data lookup functions
def lookup_data(data_src, table, since=0, until=0, limit=None, len_only=False):

    try:
        # Lookup data
        df_len = DWO.query(f"SELECT COUNT(*) FROM {table}")
        df_len = df_len.iloc[0]['count']

        if len_only:
            return None, df_len

        if limit:
            df = DWO.query(f"SELECT * FROM {table} LIMIT {limit}")
        else:
            df = DWO.query(f"SELECT * FROM {table}")

        return (df, df_len)

    except Exception as e:

        traceback.print_exc()

        a = pd.DataFrame([f'unnable to query table {table}.'],
                         columns=['error'],
                        )
        return (a, len(a))

###############################################################################
# Dasboard layout

def Table(table, limit):
    """Generate DWTABLE Layout

    Parameters
    ----------
        table | string
            Table name

        limit | integer
            Maximum number of elements to be retrieved

    Returns
    -------
        Layout object (a list of dbc.Row() objects)
    """
    # Initial data lookup
    df, df_len = lookup_data(DWO, table=table, limit=limit)

    # Layout obj
    layout = [

        # Gagets row
        dbc.Row([

            # Reg Counter
            dbc.Col([
                daq.LEDDisplay(id='reg-counter',
                               label="Registros",
                               labelPosition='bottom',
                               value="0"
                              )
            ],className='d-flex justify-content-center'
            ),

            # Attr counter
            dbc.Col([
                daq.LEDDisplay(id='attr-counter',
                               label="Atributos",
                               labelPosition='bottom',
                               value="0"
                              )
            ],className='d-flex justify-content-center'
            ),

            # Download buttons
            dbc.Col(
                dbc.ButtonGroup([
                    html.A(
                        dbc.Button("CSV", id='csv-btn'),
                        id='csv-A', download=table+".csv"
                    ),
                    html.A(
                        dbc.Button("ODS", id='ods-btn'),
                        id='ods-A', download=table+".ods"
                    ),
                    html.A(
                        dbc.Button("XLS", id='xls-btn'),
                        id='xls-A', download=table+".xls"
                    ),
                ]),
                className='d-flex align-items-center justify-content-center'
            ),

        ]),

        # Filters form row
        dbc.Row([
            dbc.Col([
                #
                dbc.Label(
                    f'Preview {limit if limit <= df_len else df_len}' \
                    f' registros',
                    id='slider-label',
                    html_for=table+'-slider'
                ),
                dcc.Slider(
                    id='slider',
                    min=1,
                    max=df_len,
                    value=limit if limit <= df_len else df_len
                ),

            ]),
        ]),

        # Table row
        dbc.Row([
            dbc.Col(
                html.Div(id='table-obj',
                        )
            ),
        ]),

        # Hidden div inside the app that stores the intermediate value
        html.Div(id='table-name', style={'display': 'none'},
                 children=str(table),
                ),

    ]

    return layout

###############################################################################
# Callbacks
@app.callback(Output('table-obj', 'children'),
              Input('table-name', 'children'),
              Input('slider', 'value'),
             )
def update_table_object(table_name, limit_value):

    # Parse parameters

    # Lookup data
    df, df_len = lookup_data(DWO,
                             table=table_name,
                             limit=limit_value
                            )

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

@app.callback(
    Output('slider-label', 'children'),
    Input('slider', 'value'),
    State('table-name', 'children'),
)
def update_slider_object(value, table_name):
    df, df_len = lookup_data(DWO, table=table_name, len_only=True)
    return f'Preview {value if value <= df_len else df_len} registros'

@app.callback(
    Output('reg-counter', 'value'),
    Input('csv-btn', 'n_clicks'),
    State('table-name', 'children'),
)
def update_reg_counter(n_clicks, table_name):
    df, df_len = lookup_data(DWO, table=table_name, len_only=True)
    return str(df_len)

@app.callback(
    Output('attr-counter', 'value'),
    Input('csv-btn', 'n_clicks'),
    State('table-name', 'children'),
)
def update_attr_counter(n_clicks, table_name):
    df, df_len = lookup_data(DWO, table=table_name, limit=1)
    return str(len(df.columns))

@app.callback(
    Output('csv-A', 'href'),
    Input('csv-btn', 'n_clicks'),
    Input('table-name', 'children'),
    Input('slider', 'value'),
)
def update_download_csv(n_clicks, table_name, limit_value):

    # Lookup data
    df, df_len = lookup_data(DWO,
                             table=table_name,
                             limit=limit_value
                            )

    # Export CVS
    csv_string = df.to_csv(index=False, encoding='utf-8', sep=';')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('xls-A', 'href'),
    Input('xls-btn', 'n_clicks'),
    Input('table-name', 'children'),
    Input('slider', 'value'),
)
def update_download_xls(n_clicks, table_name, limit_value):

    # Lookup data
    df, df_len = lookup_data(DWO,
                             table=table_name,
                             limit=limit_value
                            )

    # Export XLS
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=table_name, index=False)
    writer.save()
    xlsx_io.seek(0)
    # https://en.wikipedia.org/wiki/Data_URI_scheme
    media_type = \
       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    return href_data_downloadable

@app.callback(
    Output('ods-A', 'href'),
    Input('ods-btn', 'n_clicks'),
    Input('table-name', 'children'),
    Input('slider', 'value'),
)
def update_download_ods(n_clicks, table_name, limit_value):

    # Lookup data
    df, df_len = lookup_data(DWO,
                             table=table_name,
                             limit=limit_value
                            )

    # Export ODS
    ods_io = io.BytesIO()
    writer = pd.ExcelWriter(ods_io, engine='odf')
    df.to_excel(writer, sheet_name=table_name, index=False)
    writer.save()
    ods_io.seek(0)
    # https://en.wikipedia.org/wiki/Data_URI_scheme
    media_type = \
       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(ods_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    return href_data_downloadable

