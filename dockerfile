FROM python:3.13.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --with dev --no-root

COPY . .

CMD ["python", "-m", "uvicorn", "gems_marketplace.main:gems_marketplace", "--host", "0.0.0.0", "--port", "8000"]
