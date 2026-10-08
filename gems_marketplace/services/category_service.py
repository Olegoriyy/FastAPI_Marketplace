from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import CategoryRepository
from gems_marketplace.models.models import Category


class CategoryService:
    def __init__(
        self,
        session: AsyncSession,
        category_repo: CategoryRepository,
    ) -> None:
        self.category_repo = category_repo
        self.session = session

    async def add_category(self, category_name: str) -> None:
        category = Category(name=category_name)
        await self.category_repo.add_in_db(category)

    async def get_list_all_categories(self) -> list[Category]:
        return await self.category_repo.get_list_all()
