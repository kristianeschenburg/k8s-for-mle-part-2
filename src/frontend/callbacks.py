import os
from dash import callback, html, Input, Output, State, no_update

from constants import DEFAULT_USER_BACKEND_URL, DEFAULT_SALARY_BACKEND_URL
from pods import list_pods, pod_panel_namespaces

import requests

USER_BACKEND_URL = os.environ.get('USER_BACKEND_URL', DEFAULT_USER_BACKEND_URL)
SALARY_BACKEND_URL = os.environ.get('SALARY_BACKEND_URL', DEFAULT_SALARY_BACKEND_URL)
# Longer than the backends' own timeout, so a backend's 502 reaches us
# before we give up on it.
REQUEST_TIMEOUT = float(os.environ.get('REQUEST_TIMEOUT', 8))


@callback(
     Output('findings', 'children'),
     Input('name-button','n_clicks'),
     State('name', 'value'),
     State('currency', 'value'),
     prevent_initial_call=True)
def update_main(n, name, currency):
    if not n or not name:
        return no_update

    # Direct path (blocked by network policy)
    user_direct, user_direct_status = fetch(USER_BACKEND_URL, '/user', name=name)

    # Indirect path (allowed by network policy)
    user_indirect, user_indirect_status = fetch(SALARY_BACKEND_URL, '/user', name=name)

    salary, salary_status = fetch(SALARY_BACKEND_URL, '/salary', name=name, currency=currency)
    age, age_status = fetch(SALARY_BACKEND_URL, '/age', name=name)

    # One line per network edge, so a blocked edge is visible by name.
    return [
        html.Li(f'frontend → user-backend (direct): {user_direct_status}'),
        html.Li(f'frontend → salary-backend → user-backend (indirect): {user_indirect_status}'),
        html.Li(f'frontend → salary-backend /salary: {salary_status}'),
        html.Li(f'frontend → salary-backend /age (→ user-backend): {age_status}'),
        html.Hr(),
        html.Li(summarize(name, user_indirect, salary, age)),
    ]


@callback(
     Output('pods', 'children'),
     Input('name-button','n_clicks'),
     prevent_initial_call=True)
def update_pods(n):
    return [
        html.Li(line)
        for namespace in pod_panel_namespaces()
        for line in list_pods(namespace)
    ]


def fetch(base_url: str, path: str, **params):
    """
    GET a backend endpoint. Returns (json or None, human-readable status).
    """
    headers = {
        'accept': 'application/json',
    }

    try:
        response = requests.get(
            f'{base_url}{path}', params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as e:
        return None, f'unreachable ({type(e).__name__})'

    if not response.ok:
        return None, f'{response.status_code}: {response.text}'
    return response.json(), 'ok'


def summarize(name, user, salary, age):
    if user is None:
        return f'{name} is not a user (or the user backend is unreachable)'

    parts = [f"{user[0]['first_name']} {user[0]['last_name']} is a user"]
    if salary:
        parts.append(f"earns {salary['salary']} {salary['currency']}")
    if age:
        parts.append(f"is {age[0]['age']}")
    return ', '.join(parts) + '.'
