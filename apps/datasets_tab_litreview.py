import dash_bootstrap_components as dbc
import pandas as pd
import logging
import json
import plotly.express as px
from app import _, app, config
from apps import mod_indicator
from internals import tags
from dash import Input, Output, State, html, dcc

# TODO
# Graph Ideias
## Average number of datasets per article

# logger
LOG_FORMAT = '%(levelname)s\t%(asctime)s:\t%(message)s'
logging.basicConfig(level = logging.DEBUG, format = LOG_FORMAT)
log = logging.getLogger(__name__)

###############################################################################
# Settings
DF_NAME='datasets'
DOWNLOAD_FILENAME='datasets.xlsx'
INDICATOR01_FILENAME='dataset_list.xlsx'
INDICATOR02_FILENAME='article_list.xlsx'
PLOT01_FILENAME='plot01_data.xlsx'

###############################################################################
# Layout Objects
###############################################################################
graph01 = dcc.Graph(id=DF_NAME+'-plot01',)
graph02 = dcc.Graph(id=DF_NAME+'-pie01',)
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
    disabled=True,
),
modal_indicator01 = dbc.Modal( # Datasets
    [
        dbc.ModalHeader(dbc.ModalTitle(_('Datasets'))),
        dbc.ModalBody(id=DF_NAME+"-modal-body-ind01"),
        dbc.ModalFooter(
           dbc.Button(html.I(className="fa fa-download mr-1"),
                id=DF_NAME+'-download-ind01', #className="ms-auto",
                      color='Secondary',
            ),
        ),
        dcc.Download(id=DF_NAME+"-download-component-ind01"),
    ],
    id=DF_NAME+"-modal-ind01",
    is_open=False,
    size='xl',
    scrollable=True,
)
modal_indicator02 = dbc.Modal( # Articles
    [
        dbc.ModalHeader(dbc.ModalTitle(_('Articles'))),
        dbc.ModalBody(id=DF_NAME+"-modal-body-ind02"),
        dbc.ModalFooter(
           dbc.Button(html.I(className="fa fa-download mr-1"),
                id=DF_NAME+'-download-ind02', #className="ms-auto",
                      color='Secondary',
            ),
        ),
        dcc.Download(id=DF_NAME+"-download-component-ind02"),
    ],
    id=DF_NAME+"-modal-ind02",
    is_open=False,
    size='xl',
    scrollable=True,
)
modal_plot01 = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle(
                _('Dataset citation on scientifc articles by year')
            )
        ),
        dbc.ModalBody(id=DF_NAME+"-modal-body-plot01"),
        dbc.ModalFooter(
           dbc.Button(html.I(className="fa fa-download mr-1"),
                id=DF_NAME+'-download-plot01', #className="ms-auto",
                      color='Secondary',
            ),
        ),
        dcc.Download(id=DF_NAME+"-download-component-plot01"),
    ],
    id=DF_NAME+"-modal-plot01",
    is_open=False,
    size='xl',
    scrollable=True,
)

###############################################################################
# Dasboard layout
###############################################################################
layout = [

    # Indicators Row
    html.Div(id=DF_NAME+'-indicators-row'),

    # Graph row1
    dbc.Row([

        dbc.Col(
            dbc.Row([
                graph01,
            ]),
            className='text-center',
            width={'size':12, 'offset':0}
        ),

        # dbc.Col(
        #     dbc.Row([
        #         graph02,
        #     ]),
        #     className='text-center',
        #     width={'size':6, 'offset':0}
        # ),
    ]),

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
    html.Div(modal_indicator01),
    html.Div(modal_indicator02),
    html.Div(modal_plot01),

    # Stores
    dcc.Store(id=DF_NAME+'-datasets'),
    dcc.Store(id=DF_NAME+'-articles'),
    dcc.Store(id=DF_NAME+'-plot01-data'),

]

###############################################################################
# Data lookup functions
def lookup_data(since=None, until=None):

    lib_fname = config['LIB']['ARTICLES']
    datasets_file = config['LIB']['DATASETS']

    # read articles from json
    with open(lib_fname, 'r') as f:
        articles = json.load(f)
        log.info(f'"{lib_fname}" read. {len(articles)} entries.')

    # read datasets.json
    with open(datasets_file, 'r') as f:
        datasets = json.load(f)
        log.info(
            f'"{datasets_file}" read. ' \
            f'{len(datasets["areas"])} areas, ' \
            f'{len(datasets["themes"])} themes, ' \
            f'{len(datasets["datasets"])} datasets.'
        )

    # check article classification consistence
    for article in articles:
        tags.validate_classification(article, datasets)

    return datasets, articles

def lookup_indicators(datasets=None, articles=None, row=1):
    """Lookup indicators data

        datasets | json

        articles | json

        row | integer
            Row number. Default is 1

    Returns
    -------
        Indicators dict to be consumed be mod_indicator.Row()
    """
    if not datasets:
        n_datasets = -1
    else:
        df = pd.DataFrame(datasets['datasets'])
        df = df[df['id'] != ''].reset_index(drop=True)
        n_datasets = len(df)

    if not articles:
        n_articles = -1
    else:
        df = pd.DataFrame(articles)
        df = df[df['name'] != ''].reset_index(drop=True)
        n_articles = len(df)

    indicators = []
    # Row selector
    if not row or row not in [1,2]:
        row=1

    if row==1:

        # Indicator 1
        indicator_value = n_datasets
        indicator = {}
        indicator['id']='id1'
        indicator['title']=_('Datasets')
        indicator['value']=indicator_value
        indicator['color']='text-success'
        indicator['fmt']='number'
        indicators.append(indicator)

        # Indicator 2
        indicator_value = n_articles
        indicator = {}
        indicator['id']='id2'
        indicator['title']=_('Articles')
        indicator['value']=indicator_value
        indicator['color']='text-success'
        indicator['fmt']='number'
        indicators.append(indicator)

    return indicators

###############################################################################
# Aux functions
###############################################################################
def parse_datepicker(start_date, end_date):
    """Parse DatePickerRange start and end dates and return as date_sk integers
    (YYYYMMDD)
    """
    if start_date and end_date:
        a = start_date.split('-')
        since = int(a[0] + a[1] + a[2])
        a = end_date.split('-')
        until = int(a[0] + a[1] + a[2])
        if until < since: until = since
    else:
        since = until = 0

    return since, until

###############################################################################
# Callbacks
###############################################################################
@app.callback(
    Output(DF_NAME+'-datasets', 'data'),
    Output(DF_NAME+'-articles', 'data'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    prevent_initial_call=False,
)
def update_data_store(refresh):
    """update_data_store()
    """
    datasets, articles = lookup_data()
    return datasets, articles

@app.callback(
    Output(DF_NAME+'-indicators-row', 'children'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    Input(DF_NAME+'-datasets', 'data'),
    Input(DF_NAME+'-articles', 'data'),
    prevent_initial_call=False,
)
def update_indicators(refresh, datasets, articles):
    """update_indicators()
    """
    refresh

    # Parse parameters

    # Lookup data
    data = lookup_indicators(datasets, articles)

    return mod_indicator.Row(data, style=2)

@app.callback(
    Output(DF_NAME+"-download-component", "data"),
    Input(DF_NAME+"-btn", "n_clicks"),
    prevent_initial_call=True,
)
def download_table(n_clicks):

    # Parse parameters
    # since, until = parse_datepicker(start_date, end_date)

    if n_clicks and n_clicks > 0:

        # Lookup data
        df = pd.DataFrame()

        return dcc.send_data_frame(
            df.to_excel, DOWNLOAD_FILENAME, sheet_name="sheet1"
        )
    else:
        return

@app.callback(
    Output(DF_NAME+'-modal-ind01', 'is_open'),
    Input('id1-link', 'n_clicks'),
    State(DF_NAME+'-modal-ind01', 'is_open'),
    prevent_initial_call=True,
)
def toggle_modal_indicator01(n1, is_open):
    """toggle indicators modal
    """
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output(DF_NAME+'-modal-body-ind01', 'children'),
    Input('id1-link', 'n_clicks'),
    State(DF_NAME+'-datasets', 'data'),
    prevent_initial_call=True,
)
def update_modal_indicator01(n1, data):
    n1

    if data:
        df = pd.json_normalize(data['datasets'])
        df = df[df['id'] != ''].reset_index(drop=True)
        df['link'] = df['link'].apply(lambda x:
            dbc.Button(
                html.A(
                    html.P(className="fa fa-external-link-alt"),
                    href=str(x),
                    target='_blank',
                ),
                color='link', size='sm',
                className='bg-transparent',
                id={'type':'update-user', 'index':x},
            )
            if x else None
        )
        df = df[[
            'id', 'name', 'publisher', 'link', 'description',
        ]]
    else:
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
    )

@app.callback(
    Output(DF_NAME+"-download-component-ind01", "data"),
    Input(DF_NAME+"-download-ind01", "n_clicks"),
    State(DF_NAME+'-datasets', 'data'),
    prevent_initial_call=True,
)
def download_modal_indicator01(n_clicks, data):

    if n_clicks:

        if data:
            df = pd.json_normalize(data['datasets'])
        else:
            df = pd.DataFrame()

        return dcc.send_data_frame(
            df.to_excel, INDICATOR01_FILENAME, sheet_name="sheet1"
        )
    else:
        return

@app.callback(
    Output(DF_NAME+'-modal-ind02', 'is_open'),
    Input('id2-link', 'n_clicks'),
    State(DF_NAME+'-modal-ind02', 'is_open'),
    prevent_initial_call=True,
)
def toggle_modal_indicator02(n1, is_open):
    """toggle indicators modal
    """
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output(DF_NAME+'-modal-body-ind02', 'children'),
    Input('id2-link', 'n_clicks'),
    State(DF_NAME+'-articles', 'data'),
    prevent_initial_call=True,
)
def update_modal_indicator02(n1, data):
    n1

    if data:
        df = pd.json_normalize(data)
        df = df[df['name'] != ''].reset_index(drop=True)
        df['link'] = df['link'].apply(lambda x:
            dbc.Button(
                html.A(
                    html.P(className="fa fa-external-link-alt"),
                    href=str(x),
                    target='_blank',
                ),
                color='link', size='sm',
                className='bg-transparent',
                id={'type':'update-user', 'index':x},
            )
            if x else None
        )
        df['repo'] = df['repo'].apply(lambda x:
            dbc.Button(
                html.A(
                    html.P(className="fa fa-external-link-alt"),
                    href=str(x),
                    target='_blank',
                ),
                color='link', size='sm',
                className='bg-transparent',
                id={'type':'update-user', 'index':x},
            )
            if x else None
        )
        # df = df[[
        #     'id', 'name', 'publisher', 'link', 'description',
        # ]]
    else:
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
    )

@app.callback(
    Output(DF_NAME+"-download-component-ind02", "data"),
    Input(DF_NAME+"-download-ind02", "n_clicks"),
    State(DF_NAME+'-articles', 'data'),
    prevent_initial_call=True,
)
def download_modal_indicator02(n_clicks, data):

    if n_clicks:

        if data:
            df = pd.json_normalize(data)
        else:
            df = pd.DataFrame()

        return dcc.send_data_frame(
            df.to_excel, INDICATOR02_FILENAME, sheet_name="sheet1"
        )
    else:
        return

@app.callback(
    Output(DF_NAME+'-plot01', 'figure'),
    Output(DF_NAME+'-plot01-data', 'data'),
    Input(DF_NAME+'-articles', 'data'),
    Input(DF_NAME+'-datasets', 'data'),
    Input(DF_NAME+'-refresh-btn', 'n_clicks'),
    prevent_initial_call=False,
)
def update_plot01(articles, datasets, refresh):

    refresh

    # lookup data
    df = pd.json_normalize(
        articles,
        record_path='datasets',
        meta=['name', 'year'],
        record_prefix='ds'
    )
    df.rename(
        index=str,
        columns={'ds0':'dataset', 'name':'article'},
        inplace=True
    )
    df = df[df['dataset']!=''].reset_index(drop=True)
    df = df[['dataset', 'article', 'year']]
    dfg = df.groupby(['year','dataset']).agg({'article':'count'}).reset_index()

    dfa = pd.json_normalize(datasets, record_path='datasets')
    dfa = dfa[['id', 'publisher']]
    dfa.rename(index=str, columns={'id':'dataset'}, inplace=True)

    dfg = pd.merge(dfg, dfa, on='dataset', how='left')

    # https://plotly.com/python/bubble-charts/
    fig = px.scatter(
        dfg,
        x='dataset',
        y='year',
        size='article',
        color='publisher',
        hover_name='publisher'
    )
    fig.update_layout(
        title=_('Dataset citation on scientifc articles by year'),
        xaxis_title=_('Dataset'),
        yaxis_title=_('Year'),
    )

    return fig, dfg.to_dict('records')

@app.callback(
    Output(DF_NAME+'-modal-plot01', 'is_open'),
    Input(DF_NAME+'-plot01', 'clickData'),
    State(DF_NAME+'-modal-plot01', 'is_open'),
    prevent_initial_call=True,
)
def toggle_modal_plot01(n1, is_open):
    """toggle indicators modal
    """
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output(DF_NAME+'-modal-body-plot01', 'children'),
    Input(DF_NAME+'-plot01', 'clickData'),
    State(DF_NAME+'-plot01-data', 'data'),
    prevent_initial_call=True,
)
def update_modal_indicator01(n1, data):
    n1

    if data:
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm',
        style={'textAlign':'center'},
    )

@app.callback(
    Output(DF_NAME+"-download-component-plot01", "data"),
    Input(DF_NAME+"-download-plot01", "n_clicks"),
    State(DF_NAME+'-plot01-data', 'data'),
    prevent_initial_call=True,
)
def download_modal_indicator01(n_clicks, data):

    if n_clicks:

        if data:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame()

        return dcc.send_data_frame(
            df.to_excel, PLOT01_FILENAME, sheet_name="sheet1"
        )
    else:
        return

