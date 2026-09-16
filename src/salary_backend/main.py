import os
import time

import fastapi
from fastapi import status, HTTPException
import pandas as pd
import requests
import uvicorn

from constants import DEFAULT_USERS_BACKEND_URL

CACHED = False
SLEEP_DURATION = int(os.environ.get('SLEEP_DURATION', 10))
BACKEND_URL = os.environ.get('BACKEND_URL', DEFAULT_USERS_BACKEND_URL)
REQUEST_TIMEOUT = float(os.environ.get('REQUEST_TIMEOUT', 5))


def long_function():
    global CACHED
    if not CACHED:
        time.sleep(SLEEP_DURATION)
        CACHED = True
    return True

        
app = fastapi.FastAPI(root_path="/salary-backend")


@app.get('/healthz')
def health_check():
    return 'OK'

@app.get('/ready')
def ready_check():
    long_function()
    return 'OK'


@app.get('/age')
def get_age(name: str):
    """
    Age endpoint goes through the backend API to first check if the user exists.
    """
    get_user_from_backend(name)
    return get_age_from_csv(name)


@app.get('/salary')
def salary(name: str):
    """
    Look up a user's salary in the salary table.
    """
    return get_salary_from_csv(name)


def get_user_from_backend(name: str):
    """
    Get a user from the user backend.

    Raises an HTTPException with 404 if the user doesn't exist, or 502 if
    the user backend is unreachable or returns an unexpected error.
    """
    headers = {
        'accept': 'application/json',
    }

    params = {
        'name': name,
    }

    try:
        response = requests.get(
            f'{BACKEND_URL}/user', params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"User backend unreachable: {e}"
        ) from e

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {name} not found"
        )
    if not response.ok:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"User backend returned {response.status_code}: {response.text}"
        )

    return response.json()


def get_age_from_csv(name: str):
    data_file = 'ages.csv'
    
    df = pd.read_csv(data_file)

    is_name = df.loc[df['first_name'] == name]
    if is_name.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Name {name} not found in age table."
        )

    return is_name.to_dict(orient='records')


def get_salary_from_csv(name: str):
    data_file = 'salaries.csv'
    
    df = pd.read_csv(data_file)

    is_name = df.loc[df['first_name'] == name]
    if is_name.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Name {name} not found in salary table."
        )

    return is_name.to_dict(orient='records')



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)