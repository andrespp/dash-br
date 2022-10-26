"""home.py
"""
import dash_bootstrap_components as dbc
from dash import dcc, html

jumbotron = html.Div(
    dbc.Container(
        [
            html.H1("Painel DW-BRA", className="display-3"),
            html.P("",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                "Ferramenta de visualização de dados do Data Warehouse DW-Bra.",
                className="lead",
            ),
            html.P(
                dbc.Button(
                    "Mais Informações",
                    color="success",
                    href="https://github.com/andrespp/dw-bra",
                    external_link=True,
                    target='_blank',
                ),
            ),
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 bg-light rounded-3",
)

layout = dbc.Row([
    dbc.Col([
        jumbotron
    ], className='p-0', width=12)
])
