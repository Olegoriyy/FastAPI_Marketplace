from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_session_tx
from app.repositories.categories import all_categories
from app.repositories.products import get_product_by_id
from app.schemas.category import CategoryPublic
from app.schemas.product import ProductPublic

products_router = APIRouter(tags=['products'])


@products_router.get('/categories', response_model=list[CategoryPublic])
async def get_categories(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
):
    categories = await all_categories(session)
    return [CategoryPublic.model_validate(category) for category in categories]


@products_router.get('/products/{product_id}', response_model=ProductPublic)
async def get_product(
    product_id: int,
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> ProductPublic:
    product = await get_product_by_id(session, product_id)

    if product is None or product.published is None:
        raise HTTPException(status_code=404, detail='Product not found')

    return ProductPublic.model_validate(product)
