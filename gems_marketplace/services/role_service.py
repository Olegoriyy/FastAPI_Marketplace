from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import RoleRepository
from gems_marketplace.models.models import Role


class RoleService:
    def __init__(self, session: AsyncSession, role_repo: RoleRepository) -> None:
        self.session = session
        self.role_repo = role_repo

    async def get_by_id(self, role_id: int) -> Role:
        role = await self.role_repo.get_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail=("role not found"))
        return role

    async def get_by_name(self, role_name: str) -> Role:
        role = await self.role_repo.get_by_name(role_name)
        if role is None:
            raise HTTPException(status_code=404, detail=("role not found"))
        return role

    async def add_in_db_by_name(self, role_name: str) -> None:
        role = Role(name=role_name)
        await self.role_repo.add_in_db(role)

    async def delete_by_name(self, role_name: str) -> None:
        role = await self.get_by_name(role_name)
        await self.role_repo.delete(role)
