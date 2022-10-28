import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, dash_table
from app import app, DWC
from apps import mod_dw, mod_indicator
from dash.dependencies import Input, Output, State

###############################################################################
# Settings
###############################################################################
PREVIEW=100
DF_NAME='dwparquet'

###############################################################################
# Data Lookup
###############################################################################
df=DWC.sql("SHOW TABLES").compute()
df['table_name'] = df['Table'].apply(lambda x: {'label':x, 'value':x})
tables = df['table_name'].to_list()

###############################################################################
# Layout Objects
###############################################################################
data = dcc.Store(id=DF_NAME+'-data-store')
table_object = html.Div(id=DF_NAME+'-table1')

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
                        ),

            xl=4, lg=5, md=6, sm=10, xs=12
        ),
    ]),

    # Indicators Row
    html.Div(id=DF_NAME+'-indicators-row'),

    # Table row
    dbc.Row([dbc.Col(table_object)]),

    # Graph row
    html.Div(id=DF_NAME+'-layout'),

    # Stores
    html.Div([data]),

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
        df, df_len = mod_dw.lookup_data(DWC, table=table, limit=PREVIEW)

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
    # Input(DF_NAME+'-dropdown', 'value'),
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
