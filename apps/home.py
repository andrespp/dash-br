"""home.py
"""
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

layout = dbc.Col([ dbc.Col(html.Div("One of three columns")),
                    dbc.Col(html.Div("One of three columns")),
                    dbc.Col(html.Div("One of three columns")),
                  ], className="p-3")
