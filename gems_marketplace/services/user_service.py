from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import UserRepository
from gems_marketplace.models.models import User


class UserService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository) -> None:
        self.session = session
        self.user_repo = user_repo

    async def get_by_id(self, user_id: int) -> User:
        result = await self.user_repo.get_by_id(user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        return result

    async def get_by_name(self, user_name: str) -> User:
        user = await self.user_repo.get_by_name(user_name)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_by_email(self, email: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def add_in_db(self, user: User) -> None:
        await self.user_repo.add_in_db(user)
        await self.session.flush()
        await self.session.refresh(user)

    async def delete_by_id(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        await self.user_repo.delete(user)
