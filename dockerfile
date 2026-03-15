FROM python:3.13.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root

COPY . .

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
