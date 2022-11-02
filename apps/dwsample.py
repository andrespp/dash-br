import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, dash_table
from app import app, DWO
from apps import mod_dw, mod_indicator
from dash.dependencies import Input, Output, State

###############################################################################
# Settings
###############################################################################
PREVIEW=10000
DF_NAME='sampledw'

###############################################################################
# Data Lookup
###############################################################################
# Data Lookup
if DWO:
    sql = f"""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_schema, table_name;
    """
    df = DWO.query(sql)
    df['table_name'] = df['table_name'].apply(lambda x: {'label':x, 'value':x})
    tables = df['table_name'].to_list()
else:
    tables = []

###############################################################################
# Layout Objects
###############################################################################
data = dcc.Store(id=DF_NAME+'-data-store')
query = dcc.Store(id=DF_NAME+'-query-data-store')
download_sample = dbc.Button(
    id=DF_NAME+'-download-sample-btn',
    children=[html.I(className="fa fa-download mr-1"), "Amostra"],
    color="secondary",
    className="mt-1",
    size='sm',
),
table_object = html.Div(id=DF_NAME+'-table1')
query_object = html.Div(
    [
        dbc.Textarea(
            id=DF_NAME+'-query',
            className="mb-3",
            placeholder="SELECT * FROM TABLE",
            rows=10,
            spellcheck=False,
        ),
        dbc.Button(
            'Enviar',
            id=DF_NAME+'-query-btn',
            color="secondary",
            className="me-1",
            size='sm',
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle('Resultado da consulta')),
                dbc.ModalBody(id=DF_NAME+'-query-results'),
                dbc.ModalFooter(
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                id=DF_NAME+'-download-query-btn',
                                children=[
                                    html.I(className="fa fa-download mr-1"),
                                    "Resultado"
                                ],
                                color="secondary",
                                className="mt-1",
                                size='sm',
                            ),

                        ]
                    )
                ),
            ],
            id=DF_NAME+"-query-modal",
            is_open=False,
            size='xl',
        ),
    ],
    className='pt-2',
)

###############################################################################
# Dasboard layout
###############################################################################
layout = [

    dbc.Row(html.H3('Data Warehouse Preview')),

    # Filters row
    dbc.Row([
        dbc.Col(

            dcc.Dropdown(id=DF_NAME+'-dropdown',
                         placeholder='Selecione a Tabela',
                         options=tables,
                         value=None,
                        ),

            xl=4, lg=5, md=6, sm=10, xs=12
        ),
    ]),

    # Indicators Row
    html.Div(id=DF_NAME+'-indicators-row'),

    # Tabs row
    dbc.Row(
        [
            dbc.Col(
                dbc.Tabs(
                    [
                        # tab1
                        dbc.Tab(
                            [
                                table_object,
                                dbc.Row(
                                    dbc.ButtonGroup(
                                        [
                                            html.Div(download_sample),
                                            # html.Div(refresh_button),
                                        ]
                                    )
                                ),

                            ], label="Preview"

                        ),
                        # tab2
                        dbc.Tab(query_object, label="SQL Query"),
                    ]
                ),
            )
        ]
    ),

    # Graph row
    html.Div(id=DF_NAME+'-layout'),

    # Stores
    html.Div([data, query]),

    # Download objects
    dcc.Download(id=DF_NAME+"-download-sample"),
    dcc.Download(id=DF_NAME+"-download-query"),

]

###############################################################################
# Aux Functions
###############################################################################
def unpack_data(data):
    """Unpack data store

    Returns
    -------
        table_name, df_len, df
    """
    if data:
        # Unpack data
        table = data['table']
        df_len = data['df_len']
        df = pd.DataFrame(data['df'])

    else:
        table = ''
        df_len = 0
        df = pd.DataFrame()

    return table, df_len, df


###############################################################################
# Callbacks
###############################################################################
@app.callback(
    Output(DF_NAME+'-data-store', 'data'),
    Input(DF_NAME+'-dropdown', 'value'),
)
def update_layout(table):

    if table:
        df, df_len = mod_dw.lookup_data(DWO, table=table, limit=PREVIEW)

        data = {
            'table':table,
            'df_len':df_len,
            'df':df.to_dict(),
        }

        return data

    else:
        return None

@app.callback(
    Output(DF_NAME+'-indicators-row', 'children'),
    Input(DF_NAME+'-data-store', 'data'),
    prevent_initial_call=True,
)
def update_indicators(data):
    """update_indicators()
    """

    # unpack data
    table, df_len, df = unpack_data(data)
    table

    # Build Indicators
    indicators = []

    # Indicator 1
    indicator_value = df_len
    indicator = {}
    indicator['id']='id1'
    indicator['title']='Registros'
    indicator['value']=indicator_value
    indicator['color']='text-success'
    indicator['fmt']='number'
    indicators.append(indicator)

    # Indicator 2
    indicator_value = len(df.columns)
    indicator = {}
    indicator['id']='id2'
    indicator['title']='Atributos'
    indicator['value']=indicator_value
    indicator['color']='text-success'
    indicator['fmt']='number'
    indicators.append(indicator)

    return mod_indicator.Row(indicators, style=2)

@app.callback(
    Output(DF_NAME+'-table1', 'children'),
    Input(DF_NAME+'-indicators-row', 'children'),
    State(DF_NAME+'-data-store', 'data'),
    prevent_initial_call=True,
)
def update_table_object(table, data):
    """update_table_object()
    """

    # unpack data
    table, df_len, df = unpack_data(data)

    table =  dash_table.DataTable(
        df.to_dict('records'),
        [{"name": i, "id": i} for i in df.columns],
        style_as_list_view=True,
        style_cell={'textAlign': 'center'},
        sort_action='native',
        #filter_action='native',
        page_size=15,
        style_table={'overflowX': 'auto'},
    )

    return table

@app.callback(
    Output(DF_NAME+"-query-modal", "is_open"),
    Input(DF_NAME+"-query-btn", "n_clicks"),
    State(DF_NAME+"-query-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output(DF_NAME+"-query-results", "children"),
    Output(DF_NAME+"-query-data-store", "data"),
    Input(DF_NAME+"-query-btn", "n_clicks"),
    State(DF_NAME+"-query", "value"),
    prevent_initial_call=True,
)
def trigger_query(n_clicks, sql):

    if n_clicks and DWO:

        error = None

        try:
            # df = DWO.sql(sql).compute() # perform query
            df, df_len = mod_dw.lookup_data(DWO, query=sql)
            df_len

        except Exception as e:
            error = f'{e}'
            df = pd.DataFrame()

        finally:

            data = {
                'table':'query',
                'df_len':len(df),
                'df':df.to_dict(),
            }

            table =  dash_table.DataTable(
                df.to_dict('records'),
                [{"name": i, "id": i} for i in df.columns],
                style_as_list_view=True,
                style_cell={'textAlign': 'center'},
                sort_action='native',
                #filter_action='native',
                page_size=15,
                style_table={'overflowX': 'auto'},
            )

            if error: return html.Div(error), None
            else: return table, data

    else:
        return None, None

@app.callback(
    Output(DF_NAME+"-download-sample", "data"),
    Input(DF_NAME+"-download-sample-btn", "n_clicks"),
    State(DF_NAME+'-data-store', 'data'),
    prevent_initial_call=True,
)
def download_sample_ds(n_clicks, data):

    if n_clicks:
        # unpack data
        table, df_len, df = unpack_data(data)
        df_len

        return dcc.send_data_frame(
            df.to_excel, f'{table}_sample.xlsx', sheet_name="sheet1"
        )
    else:
        return

@app.callback(
    Output(DF_NAME+"-download-query", "data"),
    Input(DF_NAME+"-download-query-btn", "n_clicks"),
    State(DF_NAME+'-query-data-store', 'data'),
    prevent_initial_call=True,
)
def download_query_data(n_clicks, data):

    if n_clicks:
        # unpack data
        table, df_len, df = unpack_data(data)
        df_len

        return dcc.send_data_frame(
            df.to_excel, f'{table}.xlsx', sheet_name="sheet1"
        )
    else:
        return

