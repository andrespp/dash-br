import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app, config, DWO
from apps import home
from apps import template

# Header
header = html.H3(config['SITE']['HEADER'],
            style={"height":"62px",
                   "text-color":"white",
                   "background-image":"linear-gradient(#006600, #cccc00)",
                   "margin": "0",
                   "text-align":"center",
                   "font-family":"Verdana",
                   "font-size":"1.8em",
                   "font-weight":"100",
                   },
                className="align-middle text-white",
               )

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        #dbc.NavLink("Page 1", href="#"),
        # Economia
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("MTE", header=True),
                dbc.DropdownMenuItem("RAIS", href="#"),
                dbc.DropdownMenuItem("CAGED", href="#"),
                dbc.DropdownMenuItem("IBGE", header=True),
                dbc.DropdownMenuItem("IPCA", href="#"),
                dbc.DropdownMenuItem("INPC", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Economia",
        ),
        # Educação
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("CAPES", header=True),
                dbc.DropdownMenuItem("Avaliação Pós", href="/template"),
                dbc.DropdownMenuItem("MEC", header=True),
                dbc.DropdownMenuItem("Cursos de Graduação", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Educação",
        ),
    ],
    brand = config['SITE']['HEADER'],
    brand_href='/',
)

# Content
content = html.Div(id='content', children='content')

# Dash App's layout
app.title = config['SITE']['TITLE']
app.layout = html.Div([

    # Header
    dbc.Row(dbc.Col(header)
           ),

    # Navbar
    dbc.Row(dbc.Col(navbar),
           ),

    # Contents
    html.Div(id='content', children=home.layout,
            ),

    ], style={"width":"80%", "margin":"0px auto", "padding-top":"20px",}
)

# Callbacks
@app.callback(Output('content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    print(pathname)    
    err= html.Div([html.P('Page not found!')])
    switcher = {
        '/': home.layout,
        '/template': template.layout,
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

