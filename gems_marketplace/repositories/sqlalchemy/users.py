from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import UserRepository
from gems_marketplace.models.models import User


class SqlalchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_name(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        user = await self.session.scalars(stmt)
        return user.one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        user = await self.session.get(User, user_id)
        return user

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        user = await self.session.scalars(stmt)
        return user.one_or_none()

    async def add_in_db(self, user: User) -> None:
        return self.session.add(user)

    async def delete(self, user: User) -> None:
        return await self.session.delete(user)


######
# async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
#     stmt = select(User).where(User.username == username)
#     user = await session.scalars(stmt)
#     return user.one_or_none()


# async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
#     stmt = select(User).where(User.email == email)
#     result = await session.execute(stmt)
#     return result.scalar_one_or_none()


# async def add_user_in_db(session: AsyncSession, user: User) -> None:
#     return session.add(user)


# async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
#     return await session.get(User, user_id)
