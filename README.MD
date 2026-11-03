# FastAPI Marketplace

Backend маркетплейса камней с каталогом товаров, чатами и AI-помощником.

## Возможности

- Регистрация и JWT-аутентификация.
- Роли пользователей и управление объявлениями.
- Категории товаров и кабинет продавца.
- Чаты с продавцами, поддержкой и AI через WebSocket.
- Поиск товаров через Qdrant и фоновая синхронизация с PostgreSQL.

## Стек

Python 3.13+, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Qdrant, LangChain, OpenRouter, Docker Compose.

## Локальный запуск

Требуются Python 3.13+, Poetry и Docker Compose. Команды выполняются из корня проекта.

**1. Установить зависимости и создать `.env`:**

```powershell
poetry install --no-root
Copy-Item .env.example .env
```

**2. Заполнить `.env`:**

Указать параметры PostgreSQL и разные секретные ключи для access- и refresh-токенов. Для локального запуска использовать `DB_HOST=localhost`.

Дополнительно добавить настройки Qdrant и AI, заменив значения моделей и API-ключа:

```dotenv
QDRANT_HOST=http://localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=marketplace_products_v1

OPENROUTER_API_KEY=your-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_MODEL=your-embedding-model
CHAT_MODEL=your-chat-model
```

**3. Запустить сервисы, применить миграции и поднять приложение:**

```powershell
docker compose up -d
docker compose ps
```

После готовности PostgreSQL:

```powershell
poetry run alembic upgrade head
poetry run uvicorn gems_marketplace.main:gems_marketplace --reload
```

Документация API: [Swagger UI](http://localhost:8000/docs).

## Тесты

```powershell
poetry run pytest
```
