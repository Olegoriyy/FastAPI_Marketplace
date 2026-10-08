from typing import Annotated

from fastapi import APIRouter, Body, Depends

from gems_marketplace.dependencies import (
    get_admin_service,
    get_user_by_user_id_from_body,
    get_user_service,
    requred_admin_role,
)
from gems_marketplace.models.models import User
from gems_marketplace.schemas.user import UserPrivate
from gems_marketplace.services.admin_services import AdminService
from gems_marketplace.services.user_service import UserService

admin_router = APIRouter(tags=["admin"], dependencies=[Depends(requred_admin_role)])


@admin_router.delete("/admin/user/{user_id}")
async def delete_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_id: int,
) -> None:
    return await user_service.delete_by_id(user_id)


@admin_router.post("/admin/add_role")
async def add_role(
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    role_name: Annotated[str, Body(embed=True)],
) -> dict[str, str]:
    await admin_service.add_role_in_db(role_name)

    return {"status": "completed", role_name: "avialable"}


@admin_router.post("/admin/change_user_role/buyer")
async def change_user_role_to_buyer(
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    user: Annotated[User, Depends(get_user_by_user_id_from_body)],
) -> UserPrivate:
    await admin_service.change_role_to_buyer(user)

    return UserPrivate.model_validate(user)


@admin_router.post("/admin/change_user_role/seller")
async def change_user_role_to_seller(
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    user: Annotated[User, Depends(get_user_by_user_id_from_body)],
) -> UserPrivate:
    await admin_service.change_role_to_seller(user)

    return UserPrivate.model_validate(user)
