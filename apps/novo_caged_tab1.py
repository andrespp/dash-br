import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from app import _, app, DWC

DF_NAME='caged-'

###############################################################################
# Layout Objects
###############################################################################
refresh_button = dbc.Button(
    id=DF_NAME+'-refresh-btn',
    children=[html.I(className="fa fa-sync"), "Refresh"],
    color="secondary",
    className="mt-1",
    size='sm',
),
download_button = dbc.Button(
    id=DF_NAME+'-btn',
    children=[html.I(className="fa fa-download mr-1"), "Dataset"],
    color="secondary",
    className="mt-1",
    size='sm',
),

###############################################################################
# Report Definition

def layout():
    """Define dashboard layout
    """

    # Page Layout
    layout = [

        # Title Row
        dbc.Row(
            [
                dbc.Col(html.P(_('CAGED Dasboard'),
                               className='p-5 m-0 text-center'
                              ),
                        width={'size':12, 'offset':0},
                        className='px-3',
                ),
            ]
        ),

        # Graph Row
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id=DF_NAME+'graph01')
                ),
            ]
        ),

        # Table Row
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id=DF_NAME+'table01')
                ),

                dbc.Col(
                    html.Div(id=DF_NAME+'table02')

                ),

            ]
        ),

        dcc.Store(id=DF_NAME+'store'),

        # Download and Refresh buttons
        dcc.Download(id=DF_NAME+"-download-component"),
        dbc.Row(
            dbc.ButtonGroup(
                [
                    html.Div(download_button),
                    html.Div(refresh_button),
                ]
            )
        ),
            

    ]

    return layout

###############################################################################
# Data lookup functions
###############################################################################
def lookup_data():
    """Lookup report data
    """
    print(f'{DF_NAME} lookup_data()')

    df = DWC.sql(
        """
        SELECT
            COMPETENCIAMOV
            ,SUM(SALDOMOVIMENTACAO) AS SALDOMOV
        FROM STG_CAGED
        GROUP BY COMPETENCIAMOV
        """
    ).compute()
    df['competenciamov'] = df['competenciamov'].apply(int)
    df = df.sort_values(by='competenciamov')
    df['competenciamov'] = df['competenciamov'].apply(str)
    df['saldomov'] = df['saldomov'].apply(int)

    print(df)

    return df.to_dict('records')


###############################################################################
# Callbacks
###############################################################################

@app.callback(
    Output(DF_NAME+'store', 'data'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    prevent_initial_call=False,
)
def update_data_store(refresh):
    """update_data_store()
    """
    refresh
    return lookup_data()

@app.callback(
    Output('caged-graph01','figure'),
    Input(DF_NAME+'store','data'),
)
def update_graph01(data):
    """update_graph01 callback
    """

    # Lookup data
    df = pd.DataFrame(data)

    # Build figure
    return px.bar(
        df,
        x='competenciamov',
        y=['saldomov'],
        title=_("Employment balance by year")
    )

@app.callback(
    Output(DF_NAME+'table01','children'),
    Input(DF_NAME+'store','data'),
)
def update_table01(data):

    df = pd.DataFrame(data)
    df['year'] = df['competenciamov'].apply(
        lambda x: x[:4]
    )
    df = df[['year', 'saldomov']].groupby('year').agg(sum).reset_index()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
        header=True,
    )

