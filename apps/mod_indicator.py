"""mod_indicator.py
"""
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import locale

locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

def get_card(title, value, id_prefix, color='text-dark', style=1, fmt='currency'):
    """Card generator

    Parameters
    ----------
        title | string
            Card Title

        value | number
            Card value

        id_prefix | string
            Id prefix (id-title, id-value, id-link)

        color | string
            Bootstrat 'text-*' color. (ie 'text-success', 'text-danger',...)

        style | integer
            Style number (1 to 4). Default is 1

        fmt | string
            Number format option. Can be either 'currency' (default)', 'number'

    Returns
    -------
        dbc.Card() object
    """

    # Parse parameters
    if style not in [1, 2, 3 , 4]:
        raise ValueError
    if not isinstance(style, int):
        raise ValueError
    if not isinstance(title, str):
        raise ValueError
    try:
        float(value)
    except:
        raise ValueError

    # Number formating
    if fmt=='currency':
        value = locale.currency(value,grouping=True)


    # Style 1
    if style == 1:
        return dbc.Card(
                dbc.CardBody([
                    html.H6(title, className='m-1', id=f'{id_prefix}-title'),
                    html.Hr(className='m-1'),
                    html.H4(value,
                            id=f'{id_prefix}-value',
                            className=f'my-4 {color}'),
                    html.A('', className='stretched-link', href='#',
                           id=f'{id_prefix}-link'),
                ], className='p-1'
                ),
        )

    # Style 2
    elif style == 2:
        return dbc.Card(
            dbc.CardBody([
                html.H4(value,
                        id=f'{id_prefix}-value',
                        className=f'my-4 {color}'),
                html.Hr(className='m-1'),
                html.H6(title, className='m-1', id=f'{id_prefix}-title'),
                html.A('', className='stretched-link', href='#',
                       id=f'{id_prefix}-link'),
            ], className='p-1'
            ),
        )

    # Style 3
    elif style == 3:
        return dbc.Card([
            #
            dbc.CardBody([
                html.H4(value,
                        id=f'{id_prefix}-value',
                        className=f'my-4 {color}'),
                #html.Hr(className='m-1'),
                html.H6(title,
                        id=f'{id_prefix}-title',
                        className='m-1',
                        style={'font-size':'15px'}),
                html.A('', className='stretched-link', href='#',
                       id=f'{id_prefix}-link'),
            ], className='p-1'
            ),
        ], className='border-0'
        )

    # Style 4
    elif style == 4:
        return dbc.Card([
            dbc.CardHeader(title, className='p-1', id=f'{id_prefix}-title'),
            dbc.CardBody([
                html.H4(value,
                        id=f'{id_prefix}-value',
                        className=f'my-4 {color}'),
                html.A('', className='stretched-link', href='#',
                       id=f'{id_prefix}-link'),
            ], className='p-1'
            ),
        ])

    # Never to be reached
    else: return dbc.Card()

def Row(data, style=1):
    """ Indicators row generator

    Parameters
    ----------
        data | list
            List of Indicators [{'title':'A Pagar',         # required
                                 'value':'R$ 1.000,00',     # required
                                 'color':'text-success',
                                 'id':'my-id',
                                 }].
            Maximum of 4 is allowed.

        style | integer
            Style number (1 to 4). Default is 1

    Returns
    -------
        dbc.Row() object
    """

    # Parse parameters
    parse_parameters(data, style)

    # Get cards
    cards = []

    for d in data:

        if 'color' not in d.keys():
            d['color'] = 'text-dark'
        if 'fmt' not in d.keys():
            d['fmt'] = 'currency'

        cards.append(
            dbc.Col(
                get_card(
                    d['title'],
                    d['value'],
                    d['id'],
                    d['color'],
                    style=style,
                    fmt=d['fmt'],
                ),
                id=d['id'],
            )
        )

    return dbc.Row(cards, className='my-3 text-center', align='around')

def parse_parameters(data, style):

    if not isinstance(data, list) or not isinstance(style, int):
        raise TypeError

    # Validate required parameters
    if style not in [1, 2, 3, 4]:
        raise ValueError

    for i in data:
        if len(i.keys()) < 2:
            raise ValueError
        if 'title' not in i.keys() or  'value' not in i.keys():
            raise ValueError

        # Validate optional parameters
        if 'fmt' in i.keys():
            if i['fmt'] not in ['currency', 'number']:
                raise ValueError


