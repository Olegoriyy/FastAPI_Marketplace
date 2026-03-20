from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import RoleRepository
from gems_marketplace.models.models import Role


class SqlAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, role_id: int) -> Role | None:
        return await self.session.get(Role, role_id)

    async def get_by_name(self, role_name: str) -> Role | None:
        stmt = select(Role).where(Role.name == role_name)
        result = await self.session.scalars(stmt)
        return result.one_or_none()

    async def add_in_db(self, role: Role) -> None:
        self.session.add(role)

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)
