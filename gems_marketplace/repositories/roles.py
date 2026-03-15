from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import Role


async def get_role_by_id(id: int, session: AsyncSession) -> Role | None:
    return await session.get(Role, id)


async def get_role_by_name(name: str, session: AsyncSession) -> Role | None:
    stmt = select(Role).where(Role.name == name)
    result = await session.scalars(stmt)
    return result.one_or_none()
