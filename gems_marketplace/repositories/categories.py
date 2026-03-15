from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import Category


async def create_category(session: AsyncSession, name: str) -> Category:
    new_category = Category(name=name)
    session.add(new_category)
    await session.flush()
    await session.refresh(new_category)
    return new_category


async def get_category_by_id(
    session: AsyncSession, category_id: int
) -> Category | None:
    return await session.get(Category, category_id)


async def get_category_by_name(
    session: AsyncSession, category_name: int
) -> Category | None:
    return await session.scalar(select(Category).where(Category.name == category_name))


async def all_categories(session: AsyncSession) -> list[Category]:
    result = await session.scalars(select(Category))
    return list(result.all())
