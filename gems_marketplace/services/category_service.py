from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import CategoryRepository
from gems_marketplace.models.models import Category, User


class CategoryService:
    def __init__(
        self,
        session: AsyncSession,
        category_repo: CategoryRepository,
    ) -> None:
        self.category_repo = category_repo
        self.session = session

    async def get_by_name(self, name: str) -> Category | None:
        return await self.category_repo.get_by_name(name)

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self.category_repo.get_by_id(category_id)

    async def add_in_db(self, category_name: str) -> None:
        category = Category(name=category_name)
        await self.category_repo.add_in_db(category)

    async def get_list_all_categories(self) -> list[Category]:
        return await self.category_repo.get_list_all()

    async def delete(self, category_id: int):
        await self.category_repo.delete(category_id)
