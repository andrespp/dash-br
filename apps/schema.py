import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_table
import xlsxwriter
import urllib
import io
import pandas as pd
from app import app, DWO
from dash.dependencies import Input, Output
from sqlalchemy import MetaData
from sqlalchemy_schemadisplay import create_schema_graph


###############################################################################
# Settings
DF_NAME='schema'

###############################################################################
# Sample Data

###############################################################################
# Layout Objects
img_obj = html.Img(id=DF_NAME+'-img-obj', src='children')

###############################################################################
# Dasboard layout
layout = [

    dbc.Row([dbc.Col(img_obj)]),

]

###############################################################################
# Callbacks
@app.callback(Output(DF_NAME+'-img-obj', 'src'),
             [Input(DF_NAME+'-img-obj', 'n_clicks'),])
def update_schema_img(n_clicks):

    # Update image file
    graph = create_schema_graph(
       metadata=MetaData(
           f'postgres://{DWO.user}:{DWO.pswd}@{DWO.host}:{DWO.port}/{DWO.base}'
       ),
       show_datatypes=False, # img would get nasty big if we'd show the dtypes
       show_indexes=False, # ditto for indexes
       rankdir='LR', # From left to right (instead of top to bottom)
       concentrate=False # Don't try to join the relation lines together
    )
    graph.write_png('assets/dynamic/dbschema.png') # write out the file

    return app.get_asset_url('dynamic/dbschema.png')
