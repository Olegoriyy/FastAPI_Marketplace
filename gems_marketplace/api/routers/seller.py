from typing import Annotated

from fastapi import APIRouter, Body, Depends

from gems_marketplace.dependencies import (
    get_admin_service,
    get_curent_user_from_token,
    get_seller_service,
    get_user_by_user_id_from_body,
    get_user_service,
    requred_seller_or_admin_role,
    requred_seller_role,
)
from gems_marketplace.models.models import User
from gems_marketplace.schemas.product import ProductCreate, ProductPublic, ProductUpdate
from gems_marketplace.schemas.user import UserPrivate
from gems_marketplace.services.admin_services import AdminService
from gems_marketplace.services.seller_service import SellerService
from gems_marketplace.services.user_service import UserService

seller_router = APIRouter(
    tags=["seller"], dependencies=[Depends(requred_seller_or_admin_role)]
)


@seller_router.get("/seller/product/{product_id}")
async def get_product_by_id(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    seller_service: Annotated[SellerService, Depends(get_seller_service)],
    product_id: int,
):

    result = await seller_service.get_sellers_product_by_id(product_id, user.id)

    return ProductPublic.model_validate(result)


@seller_router.get("/seller/product/list/{count}")
async def get_products_list(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    seller_service: Annotated[SellerService, Depends(get_seller_service)],
    count: int,
):

    products_list = await seller_service.get_sellers_products_list(user.id, count)

    return [ProductPublic.model_validate(product) for product in products_list]


@seller_router.post("/seller/product")
async def create_product(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    product: Annotated[ProductCreate, Body()],
    seller_service: Annotated[SellerService, Depends(get_seller_service)],
):

    result = await seller_service.create_seller_product(user.id, product)

    return ProductPublic.model_validate(result)


@seller_router.patch("/seller/product")
async def update_product(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    product_data: Annotated[ProductUpdate, Body()],
    product_id: int,
    seller_service: Annotated[SellerService, Depends(get_seller_service)],
):
    result = await seller_service.update_seller_product(product_id, product_data, user)

    return ProductPublic.model_validate(result)


@seller_router.delete("/seller/product/{product_id}")
async def delete_product(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    product_id: int,
    seller_service: Annotated[SellerService, Depends(get_seller_service)],
):

    return await seller_service.delete_seller_product(
        seller=user, product_id=product_id
    )
