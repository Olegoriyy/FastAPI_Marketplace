from typing import Annotated

from fastapi import APIRouter, Body, Depends

from gems_marketplace.core.security.jwt_auth import oauth2_scheme
from gems_marketplace.dependencies import (
    get_auth_service,
    get_category_service,
    requred_admin_role,
)
from gems_marketplace.schemas.category import CategoryCreate, CategoryPublic
from gems_marketplace.services.auth_service import AuthService
from gems_marketplace.services.category_service import CategoryService

categories_router = APIRouter(tags=["categories"])


@categories_router.get("/categories", response_model=list[CategoryPublic])
async def get_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryPublic]:
    categories = await category_service.get_list_all_categories()
    return [CategoryPublic.model_validate(category) for category in categories]


@categories_router.get("/categories/{category_id}")
async def get_category(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    category_id: int,
) -> CategoryPublic:
    category = await category_service.get_by_id(category_id)
    return CategoryPublic.model_validate(category)


@categories_router.post("/categories", dependencies=[Depends(requred_admin_role)])
async def create_category(
    category: Annotated[CategoryCreate, Body()],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
):

    await category_service.add_in_db(category.name)


@categories_router.delete(
    "/categories/{category_id}",
    dependencies=[Depends(requred_admin_role)],
    status_code=204,
)
async def delete_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
):

    await category_service.delete(category_id)
