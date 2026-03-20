from typing import Annotated

from fastapi import APIRouter, Depends

from gems_marketplace.dependencies import get_category_service
from gems_marketplace.schemas.category import CategoryPublic
from gems_marketplace.services.category_service import CategoryService

categories_router = APIRouter(tags=["products"])


@categories_router.get("/categories", response_model=list[CategoryPublic])
async def get_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryPublic]:
    categories = await category_service.get_list_all_categories()
    return [CategoryPublic.model_validate(category) for category in categories]
