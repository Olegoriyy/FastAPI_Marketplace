import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import AsyncQdrantClient

from gems_marketplace.config import settings
from gems_marketplace.db.sessions import async_engine, async_session_factory
from gems_marketplace.dependencies import (
    AiService,
    get_ai_service,
    get_category_repository,
    get_category_service,
    get_embeddings,
    get_llm,
    get_product_repository,
    get_product_service,
    get_qdrant_client,
    get_role_repository,
    get_role_service,
)

logger = logging.getLogger(__name__)


async def create_ai_service(session, qdrant_client, embeddings, llm):
    # Вызываем существующие фабрики с явными аргументами.
    category_service = await get_category_service(
        session=session,
        category_repo=await get_category_repository(session=session),
    )

    role_service = await get_role_service(
        session=session,
        role_repo=await get_role_repository(session=session),
    )

    product_service = await get_product_service(
        session=session,
        product_repo=await get_product_repository(session=session),
        category_service=category_service,
        role_service=role_service,
    )

    return await get_ai_service(
        session=session,
        qdrant_client=qdrant_client,
        embeddings=embeddings,
        llm=llm,
        product_service=product_service,
    )


async def sync_loop(qdrant_client, embeddings, llm):
    while True:
        try:
            # Все сервисы этого прохода используют одну новую сессию.
            async with async_session_factory() as session:
                ai_service = await create_ai_service(
                    session=session,
                    qdrant_client=qdrant_client,
                    embeddings=embeddings,
                    llm=llm,
                )

                await ai_service.syncronize_bd_products_in_qdrant()

        except Exception:
            logger.exception("Ошибка синхронизации PostgreSQL и Qdrant")

        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Клиенты API создаются один раз на время работы приложения.
    qdrant_client = await get_qdrant_client()
    embeddings = await get_embeddings()
    llm = await get_llm()

    task = asyncio.create_task(
        sync_loop(qdrant_client, embeddings, llm),
        name="product-qdrant-sync",
    )

    try:
        yield
    finally:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        await qdrant_client.close()
        await async_engine.dispose()
