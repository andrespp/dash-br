"""caged.py
"""
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
from app import _, app, DWO
from apps import mod_datepicker, mod_indicator
from apps import novo_caged_tab1 as tab1
""" from apps import novo_caged_tab2 as tab2 """

###############################################################################
# Settings
###############################################################################
DF_NAME='caged'

###############################################################################
# Report Definition
###############################################################################

def layout():
    """Define dashboard layout
    """

    # Page Layout
    layout = [

            # Header
            html.H3(_('Datasets'), id=DF_NAME+'-header'),

            # Tabs
            html.Div([
                dbc.Tabs(
                    [
                        dbc.Tab(label=_("Overview"), tab_id=DF_NAME+"-tab1"),
                        dbc.Tab(label=_("Analisys"), tab_id=DF_NAME+"-tab2"),
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
        return tab1.layout()
        return "foo"
    elif at == DF_NAME+"-tab2":
        """ return tab2.layout """
        return "bar"
    return html.P("This shouldn't ever be displayed...")

