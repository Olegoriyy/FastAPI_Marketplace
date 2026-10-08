# My FastAPI App (starter)

Минимальный старт: SQLAlchemy ORM + Alembic миграции + PostgreSQL в Docker.

## Требования
- Docker + Docker Compose
- Python (желательно 3.12/3.13) + Poetry

Быстрый старт (локально)

1) Подготовить переменные окружения
Скопируй пример `.env.example` в `.env`:

2) Поднять PostgreSQL
docker compose up -d
docker compose ps

3) Установить зависимости
poetry install

4) Применить Миграции
poetry run alembic upgrade head
