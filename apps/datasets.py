"""datasets.py
"""
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
from app import app
from apps import datasets_tab1 as tab1
#from apps import datasets_tab2 as tab2

###############################################################################
# Settings
###############################################################################
DF_NAME='datasets'

###############################################################################
# Report Definition
###############################################################################

def layout():
    """Define dashboard layout
    """

    # Page Layout
    layout = [

            # Header
            html.H3('Datasets', id=DF_NAME+'-header'),

            # Tabs
            html.Div([
                dbc.Tabs(
                    [
                        dbc.Tab(label="Overview", tab_id=DF_NAME+"-tab1"),
                        dbc.Tab(label="Lookup", tab_id=DF_NAME+"-tab2"),
                        dbc.Tab(label="Browse", tab_id=DF_NAME+"-tab3"),
                    ],
                    id=DF_NAME+"-tabs",
                    active_tab=DF_NAME+"-tab1",
                ),
                html.Div(id=DF_NAME+"-content"),
            ])

    ]

    return layout

###############################################################################
# Callbacks
###############################################################################

@app.callback(
    Output(DF_NAME+"-content", "children"),
    Input(DF_NAME+"-tabs", "active_tab")
)
def switch_tab(at):
    if at == DF_NAME+"-tab1":
        return tab1.layout
    elif at == DF_NAME+"-tab2":
        #return tab2.layout
        return html.P('Dataset lookup')
    elif at == DF_NAME+"-tab3":
        return html.P('Browse dataset')
    return html.P("This shouldn't ever be displayed...")

