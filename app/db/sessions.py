from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

async_engine = create_async_engine(settings.DATABASE_URL_asyncpg)

async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)
