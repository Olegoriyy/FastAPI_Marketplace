from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.db.deps import get_session_tx
from gems_marketplace.repositories.products import get_product_by_id
from gems_marketplace.schemas.product import ProductPublic

products_router = APIRouter(tags=["products"])


@products_router.get("/products/{product_id}", response_model=ProductPublic)
async def get_product(
    product_id: int,
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> ProductPublic:
    product = await get_product_by_id(session, product_id)

    if product is None or product.published is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductPublic.model_validate(product)
