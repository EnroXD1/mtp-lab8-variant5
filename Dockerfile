FROM python:3.12-slim-bookworm AS build

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

WORKDIR /app
RUN pip install --no-cache-dir poetry==2.2.1

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

COPY README.md ./
COPY src ./src
RUN poetry build --format wheel \
    && .venv/bin/python -m pip install --no-index --no-deps dist/*.whl

FROM python:3.12-slim-bookworm

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUTF8=1

WORKDIR /app
COPY --from=build /app/.venv ./.venv
USER 10001:10001

ENTRYPOINT ["mtp-title"]
