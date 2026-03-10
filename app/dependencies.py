from typing import Annotated

from fastapi import Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.jwt_auth import check_and_decode_access_token, oauth2_scheme
from app.db.deps import AsyncSession, get_session_tx
from app.models.models import Role, User
from app.repositories.roles import get_role_by_id
from app.repositories.users import (
    get_user_by_email,
    get_user_by_id,
)
from app.repositories.users import (
    get_user_by_username as repo_get_user_by_username,
)


async def check_seller_role(user: User, session: AsyncSession):
    role = await session.get(Role, user.role_id)
    return role.name == 'seller'


async def check_admin_role(user: User, session: AsyncSession):
    role = await session.get(Role, user.role_id)
    return role.name == 'admin'


async def get_user_by_user_id(user_id: int, session: AsyncSession):
    user = await get_user_by_id(session=session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404)
    return user


async def get_user_by_username(username: str, session: AsyncSession):
    return await repo_get_user_by_username(username, session)


async def get_user_by_email(email: str, session: AsyncSession):
    return await get_user_by_email(email, session)


async def get_curent_user_from_token(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    payload = check_and_decode_access_token(token)
    user = await session.get(User, payload['user_id'])
    return user


async def requred_admin_role(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
):
    user_role = await get_role_by_id(user.role_id, session)
    if user_role.name != 'admin':
        raise HTTPException(status_code=403, detail='Not enough permissions')
    else:
        return True
