from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Role, User
from app.repositories.roles import get_role_by_name
from app.repositories.users import get_user_by_id


async def add_role_in_db(session: AsyncSession, role_name: str):
    new_role = Role(name=role_name)
    session.add(new_role)


async def change_role_to_buyer(session: AsyncSession, user: User):
    if user.role.name != 'buyer':
        user.role = await get_role_by_name('buyer', session)
    else:
        raise HTTPException(status_code=409, detail='user already buyer')


async def change_role_to_seller(session: AsyncSession, user: User):
    if user.role.name != 'seller':
        user.role = await get_role_by_name('seller', session)
    else:
        raise HTTPException(status_code=409, detail='user already seller')
