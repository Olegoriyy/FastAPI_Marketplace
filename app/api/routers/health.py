from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import text

from app.db.deps import AsyncSession, get_session_tx

health_router = APIRouter(tags=['health'])


@health_router.get('/health', status_code=status.HTTP_200_OK)
async def health():
    return {'status': 'ok'}


@health_router.get('/ready')
async def ready(session: Annotated[AsyncSession, Depends(get_session_tx)]):
    await session.execute(text('SELECT 1'))
    return {'status': 'ready'}
