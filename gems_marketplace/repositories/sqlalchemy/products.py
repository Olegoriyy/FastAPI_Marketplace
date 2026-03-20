from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import ProductRepository
from gems_marketplace.models.models import Product


class SqlalchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def add_in_db(self, product: Product) -> None:
        return self.session.add(product)

    async def list_by_category_id(
        self,
        category_id: int | None,
        limit: int = 10,
        published: bool = True,
    ) -> list[Product]:
        stmt = (
            select(Product)
            .where(Product.category_id == category_id, Product.published == published)
            .limit(limit)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def list_by_seller_id(
        self,
        seller_id: int,
        limit: int = 10,
        published: bool = True,
    ) -> list[Product]:
        stmt = (
            select(Product)
            .where(Product.seller_id == seller_id, Product.published == published)
            .limit(limit)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)
