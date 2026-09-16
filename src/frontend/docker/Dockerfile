# syntax=docker/dockerfile:1
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tini \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_REQUESTS_TIMEOUT=120

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/tmp/poetry_cache \
    s=; \
    for i in 1 2 3 4 5; do \
      poetry install --only main --no-root && s=ok && break; \
      echo "poetry install attempt $i failed; retrying in 10s..."; sleep 10; \
    done; \
    [ "$s" = ok ] || { echo "poetry install failed after retries"; exit 1; }

COPY callbacks.py layouts.py main.py constants.py ./

EXPOSE 8050

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py"]
