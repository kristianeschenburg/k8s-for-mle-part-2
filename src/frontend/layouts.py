from dash import html, dcc
import dash_bootstrap_components as dbc


def main_layout():

    return html.Div(
        children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dcc.Input(id='name', placeholder='How old are your friends?')
                    ], width=3),
                dbc.Col(children=[
                    html.Button('Submit', id='name-button', n_clicks=0)
                ], width=3),
                dbc.Col(children=[
                    html.Div(id='findings')

                ], width=3)
            ])
        ])