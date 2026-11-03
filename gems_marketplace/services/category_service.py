from fastapi import HTTPException
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

        category = await self.category_repo.get_by_name(name)
        if category is None:
            raise HTTPException(404, detail="category not found")
        return category

    async def get_by_id(self, category_id: int) -> Category | None:

        category = await self.category_repo.get_by_id(category_id)

        if category is None:
            raise HTTPException(404, detail="category not found")
        return category

    async def add_in_db(self, category_name: str) -> None:
        category = Category(name=category_name)
        await self.category_repo.add_in_db(category)

    async def get_list_all_categories(self) -> list[Category]:
        return await self.category_repo.get_list_all()

    async def delete(self, category_id: int):
        category = await self.get_by_id(category_id)
        if category is None:
            raise HTTPException(404, detail="category not found")

        await self.category_repo.delete(category.id)
