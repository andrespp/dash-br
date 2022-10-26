import dash_bootstrap_components as dbc
from dash import dcc, html
from app import app, DWO
from apps import mod_dw
from dash.dependencies import Input, Output, State

###############################################################################
# Settings
PREVIEW=100

###############################################################################
# Data Lookup
sql = f"""
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_schema, table_name;
"""
df = DWO.query(sql)
df['table_name'] = df['table_name'].apply(lambda x: {'label':x, 'value':x})
tables = df['table_name'].to_list()

###############################################################################
# Dasboard layout
layout = [

    # Filters row
    dbc.Row([
        dbc.Col(

            dcc.Dropdown(id='dwtable-dropdown',
                         placeholder='Selecione a Tabela',
                         options=tables,
                        ),

            xl=4, lg=5, md=6, sm=10, xs=12
        ),
    ]),

    # Graph row
    html.Div(id='dwtable-layout'),

]

###############################################################################
# Callbacks
@app.callback(
    Output('dwtable-layout', 'children'),
    Input('dwtable-dropdown', 'value'),
)
def update_layout(table):

    if table:
        return mod_dw.Table(table, PREVIEW)

