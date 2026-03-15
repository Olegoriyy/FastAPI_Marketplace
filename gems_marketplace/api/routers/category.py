from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.db.deps import get_session_tx
from gems_marketplace.repositories.categories import (
    all_categories,
)
from gems_marketplace.schemas.category import CategoryPublic

categories_router = APIRouter(tags=["products"])


@categories_router.get("/categories", response_model=list[CategoryPublic])
async def get_categories(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
):
    categories = await all_categories(session)
    return [CategoryPublic.model_validate(category) for category in categories]
