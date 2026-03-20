from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from gems_marketplace.dependencies import get_product_service
from gems_marketplace.schemas.product import ProductPublic
from gems_marketplace.services.product_service import ProductService

products_router = APIRouter(tags=["products"])


@products_router.get("/products/{product_id}", response_model=ProductPublic)
async def get_product(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductPublic:
    product = await product_service.get_by_id(product_id)

    if product is None or product.published is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductPublic.model_validate(product)
