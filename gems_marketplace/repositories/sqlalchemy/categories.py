from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import CategoryRepository
from gems_marketplace.models.models import Category


class SqlalchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_in_db(self, category: Category) -> None:
        self.session.add(category)

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self.session.get(Category, category_id)

    async def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        category = await self.session.scalars(stmt)
        return category.one_or_none()

    async def get_list_all(self) -> list[Category]:
        result = await self.session.scalars(select(Category))
        return list(result.all())
