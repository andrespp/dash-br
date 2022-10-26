import dash_bootstrap_components as dbc
import dash_daq as daq
import dash
import xlsxwriter
import urllib
import io
import pandas as pd
from app import app, DWO
from dash.dependencies import Input, Output
from dash import dcc, html
from dash import dash_table
from sqlalchemy import MetaData
from sqlalchemy_schemadisplay import create_schema_graph


###############################################################################
# Settings
DF_NAME='schema'
CLICKS=0

###############################################################################
# Sample Data

###############################################################################
# Layout Objects
img_obj = html.Img(id=DF_NAME+'-img-obj',
                   src=app.get_asset_url('dynamic/dbschema.png')
                  )
update_buttons = dbc.ButtonGroup(
    [html.A(dbc.Button("Update",
                       color="success",
                       size='sm',
                       id=DF_NAME+'-update-btn'),
            '#'),
    ],
)
###############################################################################
# Dasboard layout
layout = [

    dbc.Row([dbc.Col(update_buttons)]),
    dbc.Row([dbc.Col(html.Div(id=DF_NAME+'-container', children=img_obj))]),

]

###############################################################################
# Callbacks
@app.callback(Output(DF_NAME+'-container', 'children'),
             [Input(DF_NAME+'-update-btn', 'n_clicks'),],
              prevent_initial_call=True,
             )
def update_schema_img(n_clicks):

    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    elif n_clicks > CLICKS:


        # Update image file
        graph = create_schema_graph(
          metadata=MetaData(
          f'postgresql://{DWO.user}:{DWO.pswd}@{DWO.host}:{DWO.port}/{DWO.base}'
          ),
          show_datatypes=True, # img would get nasty big if we'd show the dtypes
          show_indexes=False, # ditto for indexes
          rankdir='LR', # From left to right (instead of top to bottom)
          concentrate=False # Don't try to join the relation lines together
        )
        graph.write_png('assets/dynamic/dbschema.png') # write out the file

    img_obj = html.Img(id=DF_NAME+'-img-obj',
                       src=app.get_asset_url('dynamic/dbschema.png')
                      )
    return img_obj
