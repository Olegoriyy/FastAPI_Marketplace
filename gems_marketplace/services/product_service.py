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
