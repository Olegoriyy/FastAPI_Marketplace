from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import RoleRepository, UserRepository
from gems_marketplace.models.models import Role, User


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        role_repo: RoleRepository,
    ) -> None:
        self.session = session
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def _check_user(self, user: User | None) -> User:
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_by_id(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)

        return await self._check_user(user)

    async def get_all_by_role(self, role: str) -> list[User]:
        users = await self.user_repo.get_all_by_role(role)
        if users is None:
            raise HTTPException(404, detail="Users not found")

        return users

    async def get_by_username(self, username: str) -> User:
        user = await self.user_repo.get_by_username(username)

        return await self._check_user(user)

    async def get_by_email(self, email: str) -> User:
        user = await self.user_repo.get_by_email(email)
        return await self._check_user(user)

    async def add_in_db(self, user: User) -> None:
        await self.user_repo.add_in_db(user)
        await self.session.flush()
        await self.session.refresh(user)

    async def delete_by_id(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        await self.user_repo.delete(user)

    async def delete(self, user: User) -> None:
        await self.user_repo.delete(user)
