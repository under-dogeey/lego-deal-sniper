FROM python:3.12-slim

WORKDIR /backend

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY alembic.ini .
COPY ./alembic ./alembic
COPY ./app ./app

ENV PATH="/backend/.venv/bin:$PATH"

CMD ["python", "-m" , "app.ingest.poller"]