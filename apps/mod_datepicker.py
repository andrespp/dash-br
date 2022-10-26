import ast
import dash
import dash_bootstrap_components as dbc
import datetime as dt
from dash import dcc, html
from dash.dependencies import Input, Output, State
from app import app, DWO

###############################################################################
# Layout Objects
###############################################################################

###############################################################################
# Object Generators
###############################################################################
def get_filter_card(df_name):
    """
    Gerenates filter row with local filters placeholder with
    id=DF_NAME-'filters'.

    Return dbc.Card() object
    """

    # Datepicker row
    layout = dbc.Row([

        # Period Dropdown
        dbc.Col([
            dcc.Dropdown(
                id='period-dropdown',
                placeholder='Período',
            ),
        ], xl=4, lg=4, md=8, sm=8, xs=12,
        ),

        # DatePickerRange
        dbc.Col([
            html.Div(
                dcc.DatePickerRange(
                    id='date-picker',
                    display_format='DD/MM/YYYY',
                    minimum_nights=0,
                    show_outside_days=True,
                    with_portal=False,
                    number_of_months_shown=1,
                    clearable=True,
                    start_date_placeholder_text='Data Inicial',
                    end_date_placeholder_text='Data Final',
                    updatemode='singledate',
                ),
                id='date-picker-container'
            ),
        ], xl=4, lg=4, md=8, sm=8, xs=12,
        ),

        # Arrows
        dbc.Col([
            html.Div([
                dbc.ButtonGroup([

                    dbc.Button(
                        html.Img(
                            src=app.get_asset_url('arrow-left-square-fill.svg')
                        ),
                        color='light',
                        id='period-left-btn'),

                    dbc.Button(
                        html.Img(
                            src=app.get_asset_url('arrow-right-square-fill.svg')
                        ),
                        color='light',
                        id='period-right-btn'),

                    ], size="sm", className="mr-1",
                )

            ], id='period-arrows', style={'display': 'none'}
            )
        ]),

        # Hidden div inside the app that stores the intermediate value
        html.Div(id='period-type', style={'display': 'none'}),
        html.Div(id='update-defaults', style={'display': 'none'}),

    ], className='pt-2',
    )

    # Filter collapse
    filterCard = dbc.Card([

        dbc.CardBody([

            # Title Row
            dbc.Row([

                dbc.Col([
                    dbc.Button('Filtros',
                               id='filter-btn',
                               size='sm',
                               active=True),
                ], align='center',
                ),

            ], justify='between'),

            # Collapsed Row
            dbc.Collapse([

                # Datepicker row
                html.Div(layout),

                html.Hr(className='my-2'),

                # Extra filters placeholder containers
                html.Div(id=df_name+'-filters'),

            ], id='filter-collapse'),

        ], className='m-0 p-2'),

    ])

    return filterCard

###############################################################################
# Lookup functions
###############################################################################
def lookup_daterange(desired_period, start_date=None, end_date=None):
    """ Returns date ranges

    Parameters
    ----------

        name | String
            Desired period: '*_day', '*_month', '*_week', '*_year', where the
            '*' can be 'this', 'previus' or 'next'. Valid examples are:
                "this_year", "next_mont", "previous_year".

        start_date | Integer
            Current start date (YYYYMMDD), required for 'previous' or 'next'
            lookups

        end_date | Integer
            Current end date (YYYYMMDD), required for 'previous' or 'next'
            lookups

    Returns
    -------
        "start_state,end_date" string in "YYYYMMDD,YYYYMMDD" format
    """

    if start_date:
        d = str(start_date)
        d = dt.date(int(d[0:4]), int(d[4:6]), int(d[6:8]))
    else:
        d = dt.date.today() # today

    if len(desired_period.split('_')) == 2:
        mode, period = desired_period.split('_')

        # Current
        if mode == 'this':
            if period == 'day':
                start_date = d
                end_date = d

            elif period == 'week':
                start_date = d - dt.timedelta(days=d.isoweekday() % 7)
                end_date = start_date + dt.timedelta(6)

            elif period == 'month':
                start_date = dt.date(d.year, d.month, 1)
                end_date = dt.date(year=(d.year + int(d.month % 12 == 0)),
                                   month=(d.month % 12) + 1,
                                   day=1) - dt.timedelta(days=1)

            elif period == 'year':
                start_date = dt.date(d.year, 1 ,1)
                end_date = dt.date(year=d.year, month=12, day=31)

            else:
                start_date = end_date = None

            # Format output
            if start_date and end_date:
                start_date = start_date.strftime('%Y%m%d')
                end_date = end_date.strftime('%Y%m%d')
                return f'{start_date},{end_date}'
            else:
                return None

        # Previous
        elif mode == 'previous':

            if period == 'day':
                start_date = dt.date(d.year,
                                     d.month,
                                     d.day) - dt.timedelta(days=1)
                end_date = start_date

            elif period == 'week':
                lw = d - dt.timedelta(days=7)
                start_date = lw - dt.timedelta(days=d.isoweekday() % 7)
                end_date = start_date + dt.timedelta(6)

            elif period == 'month':
                ld = dt.date(d.year, d.month, 1) - dt.timedelta(days=1)
                start_date = dt.date(ld.year, ld.month, 1)
                end_date = dt.date(d.year, d.month, 1) - dt.timedelta(days=1)

            elif period == 'year':
                start_date = dt.date(d.year-1, 1 ,1)
                end_date = dt.date(year=d.year-1, month=12, day=31)

            # Format output
            if start_date and end_date:
                start_date = start_date.strftime('%Y%m%d')
                end_date = end_date.strftime('%Y%m%d')
                return f'{start_date},{end_date}'
            else:
                return None

        # Next
        elif mode == 'next':

            if period == 'day':
                start_date = dt.date(d.year, d.month, d.day) + \
                                dt.timedelta(days=1)
                end_date = start_date

            elif period == 'week':
                nw = d + dt.timedelta(days=7)
                start_date = nw - dt.timedelta(days=d.isoweekday() % 7)
                end_date = start_date + dt.timedelta(6)

            elif period == 'month':
                ld = dt.date(d.year, d.month, 28) + dt.timedelta(days=5)
                start_date = dt.date(ld.year, ld.month, 1)

                ld = dt.date(d.year, d.month, 28) + dt.timedelta(days=35)
                end_date = dt.date(ld.year, ld.month, 1) - dt.timedelta(days=1)

            elif period == 'year':
                start_date = dt.date(d.year+1, 1 ,1)
                end_date = dt.date(year=d.year+1, month=12, day=31)

            # Format output
            if start_date and end_date:
                start_date = start_date.strftime('%Y%m%d')
                end_date = end_date.strftime('%Y%m%d')
                return f'{start_date},{end_date}'
            else:
                return None

    else:
        return None

    return None

###############################################################################
# Callbacks
###############################################################################
@app.callback(
    Output("filter-collapse", "is_open"),
    Output("filter-btn", "active"),
    Input("filter-btn", "n_clicks"),
    Input('update-defaults', 'children'),
    State("filter-collapse", "is_open"),
)
def toggle_collapse(n, defaults, is_open):
    """toggle_collapse()
    """

    # Identify wich component fired the callback
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Process defaults
    if button_id=='update-defaults' and defaults:
        # remove '(),' and convert to dict()
        defaults = ast.literal_eval(defaults[1:-2])

        # Process 'is_open' from defaults
        if 'is_open' in defaults.keys(): # Key exists
            #if isinstance(defaults['period'], bool):
            if defaults['is_open']:
                return True, True
            else:
                return False, False

    if n:
        return not is_open, not is_open
    return is_open, is_open

@app.callback(
    Output('date-picker', 'start_date'),
    Output('date-picker', 'end_date'),
    Output('period-type', 'children'),
    Output('period-arrows', 'style'),
    Output('period-dropdown', 'value'),
    Input('period-dropdown', 'value'),
    Input('period-left-btn', 'n_clicks'),
    Input('period-right-btn', 'n_clicks'),
    Input('date-picker-container', 'n_clicks'),
    Input('update-defaults', 'children'),
    State('date-picker', 'start_date'),
    State('date-picker', 'end_date'),
    State('period-type', 'children'),
)
def update_datepicker(period, left_btn, right_btn, dt_picker_btn, defaults,
                       start_date, end_date, period_type):

    # Identify wich component fired the callback
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Process date_picker clicked
    if button_id == 'date-picker-container':
        return start_date, end_date, None, {'display': 'none'}, None

    # Process dropdown
    if button_id == 'period-dropdown':

        if not period:
            return None, None, None, {'display': 'none'}, period

        else:
            s = str(period.split(',')[0])
            e = str(period.split(',')[1])
            start_date = dt.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
            end_date = dt.date(int(e[:4]), int(e[4:6]), int(e[6:8]))

            display_arrows = {} # display arrows

            if f'{s},{e}' == lookup_daterange('this_day'):
                period_type = 'day'
            elif f'{s},{e}' == lookup_daterange('this_week'):
                period_type = 'week'
            elif f'{s},{e}' == lookup_daterange('this_month'):
                period_type = 'month'
            elif f'{s},{e}' == lookup_daterange('this_year'):
                period_type = 'year'
            else:
                period_type = None
                display_arrows = {'display': 'none'} # do not display arrows

            return start_date, end_date, period_type, display_arrows, period

    # Process 'previous' arrow button
    elif button_id == 'period-left-btn':

        if not start_date:
            return None, None, None, {}, period

        elif not period_type:
            return start_date, end_date, None, {}, period

        else:
            a = lookup_daterange(f'previous_{period_type}',
                                 start_date.replace('-','')
                                )
            s, e = a.split(',')
            start_date = dt.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
            end_date = dt.date(int(e[:4]), int(e[4:6]), int(e[6:8]))
            return start_date, end_date, period_type, {}, period

    # Process 'next' arrow button
    elif button_id == 'period-right-btn':

        if not start_date:
            return None, None, None, {}, period

        elif not period_type:
            return start_date, end_date, None, {}, period

        else:
            a = lookup_daterange(f'next_{period_type}',
                                 start_date.replace('-','')
                                )
            s, e = a.split(',')
            start_date = dt.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
            end_date = dt.date(int(e[:4]), int(e[4:6]), int(e[6:8]))
            return start_date, end_date, period_type, {}, period

    # Process 'next' arrow button
    elif button_id == 'period-right-btn':
        return None, None, None, {}, period

    # Process update defaults fired the callback
    elif button_id == 'update-defaults':
        if defaults:
            # remove '(),' and convert to dict()
            defaults = ast.literal_eval(defaults[1:-2])

            # Process 'period' from defaults
            if 'period' in defaults.keys(): # Key exists
                if defaults['period']:      # Key is not None
                    a = lookup_daterange(defaults['period'])
                    if a:
                        period = defaults['period']
                        period_value = a
                        period_type = period.split('_')[1]
                        display_arrows = {}
                        s, e = a.split(',')
                        start_date = dt.date(int(s[:4]),
                                             int(s[4:6]),
                                             int(s[6:8]))
                        end_date = dt.date(int(e[:4]),
                                           int(e[4:6]),
                                           int(e[6:8]))
                    else:
                        start_date = end_date = None
                        period_type = period_value = None
                        display_arrows = {'display': 'none'}
                else:
                    start_date = end_date = None
                    period_type = period_value = None
                    display_arrows = {'display': 'none'}
            else:
                start_date = end_date = None
                period_type = period_value = None
                display_arrows = {'display': 'none'}

        return start_date, end_date, period_type, display_arrows, period_value

    else:
        return None, None, None, {'display': 'none'}, period

@app.callback(
    Output('period-dropdown', 'options'),
    Input('period-dropdown', 'options'),
)
def update_period_dropdown(options):

    if not options:

        today = lookup_daterange('this_day')
        this_week = lookup_daterange('this_week')
        this_month = lookup_daterange('this_month')
        this_year = lookup_daterange('this_year')

        periods = [
            {'label':'Hoje', 'value':today, 'title':today},
            {'label':'Semana atual', 'value':this_week, 'title':this_week},
            {'label':'Mês atual', 'value':this_month, 'title':this_month},
            {'label':'Ano atual', 'value':this_year, 'title':this_year},
        ]
        #predefined_periods = DWO.query('SELECT * FROM DIM_PERIODO')
        #predefined_periods['options'] = predefined_periods.apply(lambda x:
        #        {'label':x['nome'],
        #         'value':f"{x['date_from']},{x['date_to']}",
        #         'title':x['descricao'],
        #        }
        #                                                         ,axis=1)
        #options = periods + predefined_periods['options'].to_list()
        options = periods

    return options

@app.callback(
    Output('update-defaults', 'children'),
    Input('defaults', 'children'),
)
def set_defaults(defaults):
    return defaults

