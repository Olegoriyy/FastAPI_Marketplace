from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User


async def get_user_by_username(session: AsyncSession, username: str):
    return await session.scalar(select(User).where(User.username == username))


async def get_user_by_email(session: AsyncSession, email: str):
    return await session.scalar(select(User).where(User.email == email))


async def add_user_in_db(session: AsyncSession, user: User):
    return session.add(user)


async def get_user_by_id(session: AsyncSession, user_id: int):
    return await session.get(User, user_id)
