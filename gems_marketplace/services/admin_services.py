from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import Role, User
from gems_marketplace.repositories.roles import get_role_by_id, get_role_by_name


async def add_role_in_db(session: AsyncSession, role_name: str) -> None:
    new_role = Role(name=role_name)
    session.add(new_role)


async def change_role_to_buyer(session: AsyncSession, user: User) -> None:
    user_role = await get_role_by_id(user.role_id, session)
    if user_role.name != "buyer":
        user.role = await get_role_by_name("buyer", session)
    else:
        raise HTTPException(status_code=409, detail="user already buyer")


async def change_role_to_seller(session: AsyncSession, user: User) -> None:
    user_role = await get_role_by_id(user.role_id, session)
    if user_role.name != "seller":
        user.role = await get_role_by_name("seller", session)
    else:
        raise HTTPException(status_code=409, detail="user already seller")
