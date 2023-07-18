import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
from app import app, config, DWC, DWO
from apps import novo_caged
from apps import datasets
from apps import home
from apps import mod_dw
from apps import schema

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
        #dbc.DropdownMenu(
        #    children=[
        #        dbc.DropdownMenuItem("DATASETS", header=True),
        #        dbc.DropdownMenuItem("DataSUS", href="/datasus"),
        #    ],
        #    nav=True,
        #    in_navbar=True,
        #    label="Saúde",
        #),
        # Economia
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("DATASETS", header=True),
                dbc.DropdownMenuItem("CAGED", href="/novo_caged"),
                dbc.DropdownMenuItem("RAIS", href="/rais", disabled=True),
            ],
            nav=True,
            in_navbar=True,
            label="Economia",
        ),

        # Data Warehouse
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Browsing", header=True),
                dbc.DropdownMenuItem("Datasets", href="/datasets"),
                # dbc.DropdownMenuItem("Aux", header=True),
                dbc.DropdownMenuItem("Schema", href="/schema", disabled=True),
                dbc.DropdownMenuItem("Tables (Sample DW)", href="/sampledw"),
                dbc.DropdownMenuItem("Tables (Full DW)", href="/parquet"),
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
        '/novo_caged': novo_caged.layout(),
        '/datasets': datasets.layout(),
        '/parquet': mod_dw.layout(DWC, preview=100),
        '/sampledw': mod_dw.layout(DWO, preview=1000),
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

