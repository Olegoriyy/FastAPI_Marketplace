from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import ProductRepository
from gems_marketplace.models.models import Product


class ProductService:
    def __init__(
        self,
        session: AsyncSession,
        product_repo: ProductRepository,
    ):
        self.session = session
        self.product_repo = product_repo

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.product_repo.get_by_id(product_id)

    async def add_in_db(self, product: Product) -> None:

        return await self.product_repo.add_in_db(product)

    async def list_by_category_id(
        self, category_id: int, limit: int, published: bool
    ) -> list[Product]:
        return await self.product_repo.list_by_category_id(
            category_id, limit, published
        )

    async def list_by_seller_id(
        self, seller_id: int, limit: int, published: bool
    ) -> list[Product]:
        return await self.product_repo.list_by_seller_id(seller_id, limit, published)

    async def delete(self, product: Product) -> None:
        await self.product_repo.delete(product)
