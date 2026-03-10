from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Roles


async def get_role_by_id(id: int, session: AsyncSession):
    return await session.get(Roles, id)
