from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
        all: bool = False,
    ) -> list[Product]:

        if all is True:
            stmt = select(Product).where(
                Product.category_id == category_id, Product.published == published
            )
        else:
            stmt = (
                select(Product)
                .where(
                    Product.category_id == category_id, Product.published == published
                )
                .limit(limit)
            )

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def list_all_products(self) -> list[Product]:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.published.is_(True), Product.quantity > 0)
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

    async def update(self, product_id: int, data: dict):
        product = await self.session.get(Product, product_id)

        if product is None:
            return None

        for field, value in data.items():
            setattr(product, field, value)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)
