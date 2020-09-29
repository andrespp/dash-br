"""home.py
"""
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

layout = dbc.Jumbotron(
    [
        html.H3("Painel DW-Bra", className="display-3"),
        html.Hr(className="my-2"),
        html.P(
            "Ferramenta de visualização de dados do Data Warehouse DW-Bra.",
        ),
        html.P(dbc.Button("Mais Informações",
                          color="primary",
                          href="https://github.com/andrespp/dw-bra",
                          external_link=True,
                         )
               , className="lead"),
    ]
)
