import dash
import dash_bootstrap_components as dbc
import pandas as pd
import logging
import json
from app import app, config
from apps import mod_indicator
from dash import Input, Output, html, dcc, ALL

# logger
LOG_FORMAT = '%(levelname)s\t%(asctime)s:\t%(message)s'
logging.basicConfig(level = logging.DEBUG, format = LOG_FORMAT)
log = logging.getLogger(__name__)

###############################################################################
# Settings
DF_NAME='criteria'
DOWNLOAD_FILENAME='datasets.json'
INDICATOR01_FILENAME='dataset_list.xlsx'
INDICATOR02_FILENAME='article_list.xlsx'
PLOT01_FILENAME='plot01_data.xlsx'

###############################################################################
# Layout Objects
###############################################################################
# graph01 = dcc.Graph(id=DF_NAME+'-plot01',)
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
# modal_indicator01 = dbc.Modal( # Datasets
#     [
#         dbc.ModalHeader(dbc.ModalTitle(_('Datasets'))),
#         dbc.ModalBody(id=DF_NAME+"-modal-body-ind01"),
#         dbc.ModalFooter(
#            dbc.Button(html.I(className="fa fa-download mr-1"),
#                 id=DF_NAME+'-download-ind01', #className="ms-auto",
#                       color='Secondary',
#             ),
#         ),
#         dcc.Download(id=DF_NAME+"-download-component-ind01"),
#     ],
#     id=DF_NAME+"-modal-ind01",
#     is_open=False,
#     size='xl',
#     scrollable=True,
# )

###############################################################################
# Dasboard layout
###############################################################################
layout = [

    # Indicators Row
    html.Div(id=DF_NAME+'-indicators-row'),

    dbc.Row(
        [
            dbc.Col(
                [
                    html.H3("Areas"),
                    html.Div(id=DF_NAME+'-areas-table'),
                ],
                # width=4,
            ),

            dbc.Col(
                [
                    html.H3("Temas"),
                    html.Div(id=DF_NAME+'-themes-table'),
                ],
                # width=4,
            ),

            dbc.Col(
                [
                    html.H3("Repositórios"),
                    html.Div(id=DF_NAME+'-repos-table'),
                ],
                # width=4,
            ),

            dbc.Col(
                [
                    html.H3("Datasets"),
                    html.Div(id=DF_NAME+'-ds-table'),
                ],
                # width=4,
            ),

        ]
    ),

    # # Graph row1
    # dbc.Row([
    #
    #     dbc.Col(
    #         dbc.Row([
    #             graph01,
    #         ]),
    #         className='text-center',
    #         width={'size':6, 'offset':0}
    #     ),
    #
    #     dbc.Col(
    #         dbc.Row([
    #             graph02,
    #         ]),
    #         className='text-center',
    #         width={'size':6, 'offset':0}
    #     ),
    # ]),

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

    # Modals div
    # html.Div(modal_indicator01),

    # Stores
    dcc.Store(id=DF_NAME+'-datasets'),

]

###############################################################################
# Data lookup functions
def lookup_data(since=None, until=None):

    try:
        datasets_file = config['LIB']['DATASETS']

        # read datasets.json (criteria file)
        with open(datasets_file, 'r') as f:
            datasets = json.load(f)
            return datasets

    except Exception as e:
        print(f'ERR: Unable to read datasets json file. {e}')
        return {
            "areas":[],
            "themes":[],
            "repositories":[],
            "datasets":[]
        }

def lookup_indicators(data=None, row=1):
    """Lookup indicators data

        data | json

        row | integer
            Row number. Default is 1

    Returns
    -------
        Indicators dict to be consumed be mod_indicator.Row()
    """
    if not data:
        n_datasets = -1
        n_areas = -1
        n_repositories = -1
        n_themes = -1
    else:

        # n_repositories
        try:
            df = pd.DataFrame(data['repositories'])
            df = df[df['id'] != ''].reset_index(drop=True)
            n_repositories = len(df)
        except Exception as e:
            n_repositories = 0

        # n_datasets
        try:
            df = pd.DataFrame(data['datasets'])
            df = df[df['id'] != ''].reset_index(drop=True)
            n_datasets = len(df)
        except Exception as e:
            n_datasets = 0

        # n_areas
        try:
            n_areas = len(data['areas'])
        except Exception as e:
            n_areas = 0

        # n_themes
        try:
            n_themes = len(data['themes'])
        except Exception as e:
            n_themes = 0

    indicators = []
    # Row selector
    if not row or row not in [1,2]:
        row=1

    if row==1:

        # Indicator 1
        indicator_value = n_areas
        indicator = {}
        indicator['id']='id1'
        indicator['title']='Areas'
        indicator['value']=indicator_value
        indicator['color']='text-success'
        indicator['fmt']='number'
        indicators.append(indicator)

        # Indicator 2
        indicator_value = n_themes
        indicator = {}
        indicator['id']='id2'
        indicator['title']='Temas'
        indicator['value']=indicator_value
        indicator['color']='text-success'
        indicator['fmt']='number'
        indicators.append(indicator)

        # Indicator 3
        indicator_value = n_repositories
        indicator = {}
        indicator['id']='id3'
        indicator['title']='Repositórios'
        indicator['value']=indicator_value
        indicator['color']='text-success'
        indicator['fmt']='number'
        indicators.append(indicator)

        # Indicator 4
        indicator_value = n_datasets
        indicator = {}
        indicator['id']='id4'
        indicator['title']='Datasets'
        indicator['value']=indicator_value
        indicator['color']='text-success'
        indicator['fmt']='number'
        indicators.append(indicator)

    return indicators

###############################################################################
# Aux functions
###############################################################################

###############################################################################
# Callbacks
###############################################################################
@app.callback(
    Output(DF_NAME+'-datasets', 'data'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    prevent_initial_call=False,
)
def update_data_store(refresh):
    """update_data_store()
    """
    refresh
    return lookup_data()

@app.callback(
    Output(DF_NAME+'-indicators-row', 'children'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    Input(DF_NAME+'-datasets', 'data'),
    prevent_initial_call=False,
)
def update_indicators(refresh, datasets):
    """update_indicators()
    """
    refresh

    # Parse parameters

    # Lookup data
    data = lookup_indicators(datasets)

    return mod_indicator.Row(data, style=2)

@app.callback(
    Output(DF_NAME+"-download-component", "data"),
    Input(DF_NAME+"-btn", "n_clicks"),
    prevent_initial_call=True,
)
def download_table(n_clicks):

    if n_clicks and n_clicks > 0:
        try:
            return dcc.send_file(config['LIB']['DATASETS'])
        except Exception as e:
            print(e)
            return

    else:
        return

@app.callback(
    Output(DF_NAME+'-areas-table','children'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    Input(DF_NAME+'-datasets', 'data'),
)
def update_areas_table(refresh, data):
    refresh

    try:
        df = pd.DataFrame(data['areas'], columns=['area']).sort_values(by='area')
    except Exception as e:
        print(e)
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
        header=False,
    )

@app.callback(
    Output(DF_NAME+'-themes-table','children'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    Input(DF_NAME+'-datasets', 'data'),
)
def update_themes_table(refresh, data):
    refresh

    try:
        df = pd.DataFrame(data['themes'], columns=['foo']).sort_values(by='foo')
    except Exception as e:
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
        header=False,
    )

@app.callback(
    Output(DF_NAME+'-repos-table','children'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    Input(DF_NAME+'-datasets', 'data'),
)
def update_repos_table(refresh, data):
    refresh

    try:
        df = pd.DataFrame(data['repositories'])
        df = df[['id','name']].sort_values(by='id')
        df = df[df['id'] != ''].reset_index(drop=True)
        df = df[['id']]
        df['id'] = df['id'].apply(
            lambda x: html.Div(
                    x,
                    className='p-0 m-0',
                    id={'type':'repo-table', 'index':x}
                )
            if x else None
        )

    except Exception as e:
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
        header=False,
    )

@app.callback(
    Output(DF_NAME+'-ds-table','children'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    Input(DF_NAME+'-datasets', 'data'),
    Input({'type': 'repo-table', 'index': ALL}, 'n_clicks_timestamp'),
    Input({'type': 'repo-table', 'index': ALL}, 'children'),
)
def update_datasets_table(refresh, data, repo_click, repo_name):
    refresh

    try:
        # Identify repo selected (clicked on repo table)
        if len(repo_click) > 0:
            repo_click = [0 if x is None else x for x in repo_click]
            repo_index = repo_click.index(max(repo_click))
            if max(repo_click)==0:
                repo_index = -1
                repo = ''
            else:
                repo = repo_name[repo_index]
        else:
            repo_index = -1
            repo = ''

        # list datasets
        df = pd.DataFrame(data['datasets'])
        df = df[['id','name', 'repository']].sort_values(by='id')
        df = df[df['id'] != ''].reset_index(drop=True)

        # select clicked repository datasets only
        if repo != '':
            df = df[df['repository'] == repo]

        df = df[['id']]

    except Exception as e:
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
        header=False,
    )

