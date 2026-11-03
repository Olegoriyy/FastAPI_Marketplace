from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import Product, User
from gems_marketplace.schemas.product import ProductCreate, ProductUpdate
from gems_marketplace.services.product_service import ProductService


class SellerService:
    def __init__(
        self,
        session: AsyncSession,
        product_service: ProductService,
    ) -> None:
        self.session = session
        self.product_service = product_service

    async def get_sellers_product_by_id(self, product_id: int, seller_id: int):
        product = await self.product_service.get_by_id(product_id)

        if seller_id != product.seller_id:
            raise HTTPException(
                status_code=403, detail="You can get only yours product"
            )
        return product

    async def get_sellers_products_list(
        self, seller_id: int, limit: int = 10, published: bool = True
    ) -> list[Product]:

        result = await self.product_service.list_by_seller_id(
            seller_id, limit, published
        )

        return result

    async def create_seller_product(
        self, seller_id: int, product: ProductCreate
    ) -> Product:
        result = await self.product_service.add_in_db(
            product_in=product, user_id=seller_id
        )
        return result

    async def update_seller_product(
        self, product_id: int, product_data: ProductUpdate, seller: User
    ):
        result = await self.product_service.update(product_id, product_data, seller)
        return result

    async def delete_seller_product(self, product_id: int, seller: User):
        await self.product_service.delete(product_id, seller)
