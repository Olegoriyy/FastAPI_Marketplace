from typing import Annotated

from fastapi import APIRouter, Body, Depends

from gems_marketplace.dependencies import (
    get_admin_service,
    get_user_by_user_id_from_body,
    requred_admin_role,
)
from gems_marketplace.models.models import User
from gems_marketplace.schemas.user import UserPublic
from gems_marketplace.services.admin_services import AdminService

admin_router = APIRouter(tags=["admin"], dependencies=[Depends(requred_admin_role)])
# admin_router = APIRouter(tags=['admin'])


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
) -> UserPublic:
    await admin_service.change_role_to_buyer(user)

    return UserPublic.model_validate(user)


@admin_router.post("/admin/change_user_role/seller")
async def change_user_role_to_seller(
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    user: Annotated[User, Depends(get_user_by_user_id_from_body)],
) -> UserPublic:
    await admin_service.change_role_to_seller(user)

    return UserPublic.model_validate(user)


# @admin_router.post('/admin/change_user_role/seller')
# async def change_user_role_to_seller(
#     session: Annotated[AsyncSession, Depends(get_session_tx)],
#     user_id: Annotated[int, Body(embed=True)],
# ):
#     user = await get_user_by_user_id(user_id, session)

#     await change_role_to_seller(session, user)
#     await session.flush()
#     await session.refresh(user, ['role'])
#     return {'new_user_role': user.role.name}
