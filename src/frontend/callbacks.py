import os
from dash import callback, Input, Output, State, no_update

from constants import DEFAULT_USERS_BACKEND_URL

import requests

BACKEND_URL = os.environ.get('BACKEND_URL', DEFAULT_USERS_BACKEND_URL)
REQUEST_TIMEOUT = float(os.environ.get('REQUEST_TIMEOUT', 5))


@callback(
     Output('findings', 'children'),
     Input('name-button','n_clicks'),
     State('name', 'value'),
     prevent_initial_call=True)
def update_main(n, name):
    if not n or not name:
        return no_update

    try:
        response = get_user_from_backend(name)
    except requests.RequestException as e:
        return f'Could not reach the user backend: {e}'

    if response.status_code == 404:
        return f'{name} is not a user'
    if not response.ok:
        return f'User backend returned an error ({response.status_code})'

    data = response.json()[0]
    return f"{data['first_name']} {data['last_name']} is a user!"


def get_user_from_backend(name: str):
    """
    Get a user from the user backend.
    """
    headers = {
        'accept': 'application/json',
    }

    params = {
        'name': name,
    }

    return requests.get(
        f'{BACKEND_URL}/user', params=params, headers=headers, timeout=REQUEST_TIMEOUT
    )
