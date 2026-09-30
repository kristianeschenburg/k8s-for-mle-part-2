from dash import html, dcc
import dash_bootstrap_components as dbc


def main_layout():

    return html.Div(
        children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dcc.Input(id='name', placeholder='Look up a user')
                    ], width=3),
                dbc.Col(children=[
                    dcc.Dropdown(id='currency', options=['USD', 'EUR', 'GBP'], value='USD', clearable=False)
                    ], width=2),
                dbc.Col(children=[
                    html.Button('Submit', id='name-button', n_clicks=0)
                ], width=1),
            ]),
            dbc.Row(children=[
                dbc.Col(children=[
                    html.H5('Lookup'),
                    html.Ul(id='findings')
                ], width=6),
                dbc.Col(children=[
                    html.H5('Pods visible to my ServiceAccount'),
                    html.Ul(id='pods')
                ], width=6)
            ])
        ])
