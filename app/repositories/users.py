from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Users


async def get_user_by_username(session: AsyncSession, username: str):
    return await session.scalar(select(Users).where(Users.username == username))


async def get_user_by_email(session: AsyncSession, email: str):
    return await session.scalar(select(Users).where(Users.email == email))


async def add_user_in_db(session: AsyncSession, user: Users):
    return session.add(user)
