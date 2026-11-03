from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response

from gems_marketplace.core.security.jwt_auth import oauth2_scheme
from gems_marketplace.dependencies import (
    get_auth_service,
    get_product_service,
    get_seller_service,
    requred_seller_or_admin_role,
    requred_seller_role,
)
from gems_marketplace.schemas.product import ProductCreate, ProductPublic
from gems_marketplace.services.auth_service import AuthService
from gems_marketplace.services.product_service import ProductService
from gems_marketplace.services.seller_service import SellerService

products_router = APIRouter(tags=["products"])


@products_router.get("/products/{product_id}", response_model=ProductPublic)
async def get_product(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductPublic:
    product = await product_service.get_by_id(product_id)

    if product is None or product.published is False:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductPublic.model_validate(product)


@products_router.post("/products", dependencies=[Depends(requred_seller_role)])
async def create_product(
    product: Annotated[ProductCreate, Body()],
    token: Annotated[str, Depends(oauth2_scheme)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.check_and_get_user_by_token(token)

    new_product = await product_service.add_in_db(product, user.id)
    return ProductPublic.model_validate(new_product)


@products_router.delete(
    "/products/{product_id}",
    dependencies=[Depends(requred_seller_or_admin_role)],
    status_code=204,
)
async def delete_product(
    product_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.check_and_get_user_by_token(token)

    await product_service.delete(product_id, user)
