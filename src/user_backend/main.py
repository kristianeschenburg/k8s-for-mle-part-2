import os
import time

import fastapi
from fastapi import status, HTTPException
import pandas as pd
import uvicorn

CACHED = False
SLEEP_DURATION = int(os.environ.get('SLEEP_DURATION', 10))
DATA_FILE = os.environ.get('DATA_FILE', 'default_users.csv')


def long_function():
    global CACHED
    if not CACHED:
        time.sleep(SLEEP_DURATION)
        CACHED = True
    return True

        
app = fastapi.FastAPI(root_path="/user-backend")


@app.get('/healthz')
def health_check():
    return 'OK'

@app.get('/ready')
def ready_check():
    long_function()
    return 'OK'

@app.get('/user')
def get_user(name: str):
    df = pd.read_csv(DATA_FILE)

    is_name = df.loc[df['first_name'] == name]
    if is_name.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User {name} not found"
        )

    return is_name.to_dict(orient='records')


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)