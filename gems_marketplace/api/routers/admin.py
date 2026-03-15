from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.db.deps import get_session_tx
from gems_marketplace.dependencies import get_user_by_user_id, requred_admin_role
from gems_marketplace.services.admin_services import (
    add_role_in_db,
    change_role_to_buyer,
    change_role_to_seller,
)

admin_router = APIRouter(tags=["admin"], dependencies=[Depends(requred_admin_role)])


@admin_router.post("/admin/add_role")
async def add_role(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    role_name: Annotated[str, Body(embed=True)],
):
    await add_role_in_db(session, role_name)
    return {"status": "completed", role_name: "avialable"}


@admin_router.post("/admin/change_user_role/buyer")
async def change_user_role_to_buyer(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    user_id: Annotated[int, Body(embed=True)],
):
    user = await get_user_by_user_id(user_id, session)

    await change_role_to_buyer(session, user)
    await session.flush()
    await session.refresh(user, ["role"])
    return {"new_user_role": user.role.name}


@admin_router.post("/admin/change_user_role/seller")
async def change_user_role_to_seller(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    user_id: Annotated[int, Body(embed=True)],
):
    user = await get_user_by_user_id(user_id, session)

    await change_role_to_seller(session, user)
    await session.flush()
    await session.refresh(user, ["role"])
    return {"new_user_role": user.role.name}
