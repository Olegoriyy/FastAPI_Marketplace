from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.core.security.jwt_auth import (
    check_and_decode_access_token,
    oauth2_scheme,
)
from gems_marketplace.db.deps import get_session_tx
from gems_marketplace.models.models import Role, User
from gems_marketplace.repositories.roles import get_role_by_id
from gems_marketplace.repositories.users import (
    get_user_by_email,
    get_user_by_id,
)
from gems_marketplace.repositories.users import (
    get_user_by_username as repo_get_user_by_username,
)


async def check_seller_role(user: User, session: AsyncSession) -> bool:
    role = await session.get(Role, user.role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="user haven't role")
    return role.name == "seller"


async def check_admin_role(user: User, session: AsyncSession) -> bool:
    role = await session.get(Role, user.role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="user haven't role")
    return role.name == "admin"


async def get_user_by_user_id(user_id: int, session: AsyncSession) -> User:
    user = await get_user_by_id(session=session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user


async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
    user = await repo_get_user_by_username(session, username)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:
    return await get_user_by_email(session, email)


async def get_curent_user_from_token(
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    payload = check_and_decode_access_token(token)
    user = await session.get(User, payload["user_id"])
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    return user


async def requred_admin_role(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> bool:
    user_role = await get_role_by_id(user.role_id, session)
    if user_role.name != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        return True


async def requred_seller_role(
    user: Annotated[User, Depends(get_curent_user_from_token)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
):
    user_role = await get_role_by_id(user.role_id, session)
    if user_role.name != "seller":
        raise HTTPException(status_code=403, detail="Seller role required")
    else:
        return True
