import traceback
import pandas as pd
import dash_bootstrap_components as dbc
from app import app, DWC, DWO
from apps import mod_indicator
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc, html
from uetl import DataWarehouse
from dask_sql import Context

###############################################################################
# Data lookup functions
###############################################################################
def lookup_data(dw, table=None, query=None, limit=None):
    """
    Lookup data from table. If query is provided, table is ignored and query is
    returned instead
    """
    if isinstance(dw, DataWarehouse):
        return lookup_data_uetl(
            dw, table=table, query=query, limit=limit,
        )
    elif isinstance(dw, Context):
        return lookup_data_dasksql(
            dw, table=table, query=query, limit=limit,
        )
    else:
        print('Invalid DW!')
        return None, None

def lookup_data_uetl(dw, table=None, query=None, limit=None):

    try:
        # Lookup data
        if query:
            df = dw.query(query)
            df_len = len(df)

        else:
            df_len = dw.query(f"SELECT COUNT(*) AS CNT FROM {table}")
            df_len = df_len['cnt'].iloc[0]

            if limit:
                df = dw.query(f"SELECT * FROM {table} LIMIT {limit}")
            else:
                df = dw.query(f"SELECT * FROM {table}")

        return (df, df_len)

    except Exception as e:

        traceback.print_exc()

        a = pd.DataFrame([f'unnable to query table {table}.'],
                         columns=['error'],
                        )
        return (a, len(a))

def lookup_data_dasksql(dw, table=None, query=None, limit=None):

    try:
        # Lookup data
        if query:
            df = dw.sql(query).compute()
            df_len = len(df)

        else:
            df_len = dw.sql(f"SELECT COUNT(*) AS CNT FROM {table}").compute()
            df_len = df_len['cnt'].iloc[0]

            if limit:
                df = dw.sql(f"SELECT * FROM {table} LIMIT {limit}").compute()
            else:
                df = dw.sql(f"SELECT * FROM {table}").compute()

        return (df, df_len)

    except Exception as e:

        traceback.print_exc()

        a = pd.DataFrame([f'unnable to query table {table}.'],
                         columns=['error'],
                        )
        return (a, len(a))

def lookup_tables(dw):
    """Retrieve table list from Data Warehouse object"""
    if isinstance(dw, DataWarehouse):
        sql = f"""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_schema, table_name;
        """
        df = dw.query(sql)
        df['table_name'] = df['table_name'].apply(
            lambda x: {'label':x, 'value':x}
        )
        return df['table_name'].to_list()

    elif isinstance(dw, Context):
        df=dw.sql("SHOW TABLES").compute()
        df['table_name'] = df['Table'].apply(lambda x: {'label':x, 'value':x})
        return df['table_name'].to_list()

    else:
        print('Invalid DW!')
        return []

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
# Dasboard layout
###############################################################################
def layout(dw, preview):

    if isinstance(dw, DataWarehouse):
        dw_type = 'sample'
    elif isinstance(dw, Context):
        dw_type = 'full'
    else:
        dw_type = 'unknown'
        print('Invalid DW!')

    tables = lookup_tables(dw)

    # Layout Objects
    download_sample = dbc.Button(
        id='dw-download-sample-btn',
        children=[html.I(className="fa fa-download mr-1"), "Amostra"],
        color="secondary",
        className="mt-1",
        size='sm',
    ),
    table_object = html.Div(id='dw-table1')
    query_object = html.Div(
        [
            dbc.Textarea(
                id='dw-query',
                className="mb-3",
                placeholder="SELECT * FROM TABLE",
                rows=10,
                spellcheck=False,
            ),
            dbc.Button(
                'Enviar',
                id='dw-query-btn',
                color="secondary",
                className="me-1",
                size='sm',
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle('Resultado da consulta')),
                    dbc.ModalBody(id='dw-query-results'),
                    dbc.ModalFooter(
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    id='dw-download-query-btn',
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
                id="dw-query-modal",
                is_open=False,
                size='xl',
            ),
        ],
        className='pt-2',
    )
    modal_attrs = dbc.Modal( # Attributes
        [
            dbc.ModalHeader(dbc.ModalTitle('Atributos')),
            dbc.ModalBody(id="dw-modal-attrs-body"),
            dbc.ModalFooter(
               dbc.Button(
                    html.I(className="fa fa-download mr-1"),
                    id='dw-download-attrs-btn',
                    color='Secondary',
                ),
            ),
        ],
        id="dw-modal-attrs",
        is_open=False,
        size='lg',
        scrollable=True,
    )

    # Layout
    layout = [

        dbc.Row(html.H3('Data Warehouse Preview')),

        # Filters row
        dbc.Row([
            dbc.Col(

                dcc.Dropdown(id='dw-dropdown',
                             placeholder='Selecione a Tabela',
                             options=tables,
                             value=None,
                            ),

                xl=4, lg=5, md=6, sm=10, xs=12
            ),
        ]),

        # Indicators Row
        html.Div(id='dw-indicators-row'),
        modal_attrs,

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
        html.Div(id='dw-layout'),

        # Stores
        html.Div(
            [
                dcc.Store(id='dw-data-store'),
                dcc.Store(id='dw-query-data-store'),
                dcc.Store(id='dw-attrs-data-store'),
            ]
        ),

        # Hidden div inside the app that stores the intermediate value
        html.Div(dw_type, id='dw-type', style={'display': 'none'}),
        html.Div(preview, id='dw-preview', style={'display': 'none'}),

        # Download objects
        dcc.Download(id="dw-download-sample"),
        dcc.Download(id="dw-download-query"),
        dcc.Download(id="dw-download-attrs"),
    ]

    return layout

###############################################################################
# Callbacks
###############################################################################
@app.callback(
    Output('dw-data-store', 'data'),
    Input('dw-dropdown', 'value'),
    State('dw-type', 'children'),
    State('dw-preview', 'children'),
)
def update_data(table, dw_type, preview):

    if dw_type=='sample':
        DW = DWO
    elif dw_type=='full':
        DW = DWC
    else:
        DW = None

    if table:
        df, df_len = lookup_data(DW, table=table, limit=preview)

        data = {
            'table':table,
            'df_len':df_len,
            'df':df.to_dict(),
        }

        return data

    else:
        return None

@app.callback(
    Output('dw-indicators-row', 'children'),
    Input('dw-data-store', 'data'),
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
    indicator['id']='attrs'
    indicator['title']='Atributos'
    indicator['value']=indicator_value
    indicator['color']='text-success'
    indicator['fmt']='number'
    indicators.append(indicator)

    return mod_indicator.Row(indicators, style=2)

@app.callback(
    Output('dw-table1', 'children'),
    Input('dw-indicators-row', 'children'),
    State('dw-data-store', 'data'),
    prevent_initial_call=True,
)
def update_table_object(table, data):
    """update_table_object()
    """

    # unpack data
    table, df_len, df = unpack_data(data)
    df_len

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
    Output("dw-query-modal", "is_open"),
    Input("dw-query-btn", "n_clicks"),
    State("dw-query-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("dw-query-results", "children"),
    Output("dw-query-data-store", "data"),
    Input("dw-query-btn", "n_clicks"),
    State("dw-query", "value"),
    State('dw-type', 'children'),
    prevent_initial_call=True,
)
def trigger_query(n_clicks, sql, dw_type):

    if dw_type=='sample':
        DW = DWO
    elif dw_type=='full':
        DW = DWC
    else:
        DW = None

    if n_clicks and DW:

        error = None

        try:
            df, df_len = lookup_data(DW, query=sql)
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
    Output("dw-download-sample", "data"),
    Input("dw-download-sample-btn", "n_clicks"),
    State('dw-data-store', 'data'),
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
    Output("dw-download-query", "data"),
    Input("dw-download-query-btn", "n_clicks"),
    State('dw-query-data-store', 'data'),
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

@app.callback(
    Output('dw-modal-attrs', 'is_open'),
    Input('attrs-link', 'n_clicks'),
    State('dw-modal-attrs', 'is_open'),
    prevent_initial_call=True,
)
def toggle_modal_attrs(n1, is_open):
    """toggle indicators modal
    """
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output('dw-modal-attrs-body', 'children'),
    Output('dw-attrs-data-store', 'data'),
    Input('attrs-link', 'n_clicks'),
    State('dw-type', 'children'),
    State('dw-dropdown', 'value'),
    prevent_initial_call=True,
)
def update_modal_attrs(n1, dw_type, table):
    n1

    # Parse parameters

    if table and dw_type=='sample':
        DW = DWO
        sql = f"""
        SELECT
           table_name,
           column_name,
           data_type
        FROM
           information_schema.columns
        WHERE
           table_name = '{table}';
        """
        df, df_len = lookup_data(DW, query=sql)
        df_len

    elif table and dw_type=='full':
        DW = DWC
        sql = f"""
        SHOW COLUMNS FROM {table}
        """
        df, df_len = lookup_data(DW, query=sql)
        df['table_name'] = table
        df = df.rename(
            columns={
                'Column':'column_name',
                'Type':'data_type',
            }
        )
        df = df[['table_name', 'column_name', 'data_type']]
        df_len

    else:
        df = pd.DataFrame(columns=['table_name', 'column_name', 'data_type'])

    body = dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
    )
    return body, df.to_dict()

@app.callback(
    Output('dw-download-attrs', 'data'),
    Input('dw-download-attrs-btn', 'n_clicks'),
    State('dw-attrs-data-store', 'data'),
    prevent_initial_call=True,
)
def download_modal_attrs(n_clicks, data):

    if n_clicks:

        df = pd.DataFrame(data)

        return dcc.send_data_frame(
            df.to_excel, 'atributos.xlsx', sheet_name="sheet1"
        )
    else:
        return
