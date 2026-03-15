from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import User


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    user = await session.scalars(stmt)
    return user.one_or_none()


# async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
#     return await session.scalar(select(User).where(User.email == email))


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_user_in_db(session: AsyncSession, user: User) -> None:
    return session.add(user)


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)
