from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Role


async def get_role_by_id(id: int, session: AsyncSession):
    return await session.get(Role, id)


async def get_role_by_name(name: str, session: AsyncSession):
    return await session.scalar(select(Role).where(Role.name == name))
