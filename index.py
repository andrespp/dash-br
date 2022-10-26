import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
from app import app, config
from apps import dwtable
from apps import schema
from apps import home

# Header
header = html.H3(#config['SITE']['HEADER'],
            style={"height":"62px",
                   "background-image":"linear-gradient(#006600, #cccc00)",
                   #"background-image":"linear-gradient(#166c67, #00b68b)",
                   },
                className="p-3 m-0 text-white text-center",
               )

# Navbar
navbar = dbc.NavbarSimple([
        # Dcc Location
        dcc.Location(id='url', refresh=False),

        # Saúde
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("DATASETS", header=True),
                dbc.DropdownMenuItem("DataSUS", href="/datasus"),
            ],
            nav=True,
            in_navbar=True,
            label="Saúde",
        ),
        # Economia
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("DATASETS", header=True),
                dbc.DropdownMenuItem("CAGED", href="/nfse"),
                dbc.DropdownMenuItem("RAIS", href="/nfse"),
            ],
            nav=True,
            in_navbar=True,
            label="Economia",
        ),

        # Data Warehouse
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Aux", header=True),
                dbc.DropdownMenuItem("Schema", href="/schema"),
                dbc.DropdownMenuItem("Tables", href="/dwtables"),
            ],
            nav=True,
            in_navbar=True,
            label="Data Warehouse",
        ),
    ],
    brand = "Início",
    brand_href='/',
    className='p-0',
)

# Content
content = html.Div(id='page-content')

# Dash App's layout
app.title = config['SITE']['TITLE']

app.layout = dbc.Container([

    # Header Row
    dbc.Row(

        dbc.Col(header,
                className='p-0',
                width={'size':12, 'offset':0},
               ),
            className='mt-3',

           ),

    # Navbar
    dbc.Row(dbc.Col(navbar,
                    className='p-0',
                    width={'size':12, 'offset':0},
                   ),
           ),

    # Contents
    html.Div(id='page-content',
            className='mt-2'
            ),

],fluid=False)

###############################################################################
# Callbacks
@app.callback(Output('page-content', 'children'),
                            [Input('url', 'pathname')])
def display_page(pathname):
    err= html.Div([html.P('Page not found!')])
    switcher = {
        '/': home.layout,
        '/dwtables': dwtable.layout,
        '/schema': schema.layout,
    }
    return switcher.get(pathname, err)

###############################################################################
## Main
if __name__ == '__main__':

    if config['SITE']['DEBUG'] == "True":
        DEBUG=True
    else:
        DEBUG=False

    # Run Server
    app.run_server(host='0.0.0.0', debug=DEBUG)

