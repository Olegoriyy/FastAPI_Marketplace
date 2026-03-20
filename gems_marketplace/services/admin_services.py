from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import Role, User
from gems_marketplace.services.role_service import RoleService
from gems_marketplace.services.user_service import UserService


class AdminService:
    def __init__(
        self,
        session: AsyncSession,
        role_service: RoleService,
        user_service: UserService,
    ) -> None:
        self.session = session
        self.role_service = role_service
        self.user_service = user_service

    async def add_role_in_db(self, role_name: str) -> Role:
        await self.role_service.add_in_db_by_name(role_name)
        role_in_db = await self.role_service.get_by_name(role_name)
        return role_in_db

    async def change_role_to_buyer(self, user: User) -> None:
        role_from_db = await self.role_service.get_by_name("buyer")
        user_role_name = await self.role_service.get_by_id(user.role_id)

        if user_role_name.name == "buyer":
            raise HTTPException(status_code=409, detail="user already buyer")
        user.role = role_from_db
        await self.session.flush()
        await self.session.refresh(user)

    async def change_role_to_seller(self, user: User) -> None:
        role_from_db = await self.role_service.get_by_name("seller")
        user_role_name = await self.role_service.get_by_id(user.role_id)

        if user_role_name.name == "seller":
            raise HTTPException(status_code=409, detail="user already seller")
        user.role = role_from_db
        await self.session.flush()
        await self.session.refresh(user)
