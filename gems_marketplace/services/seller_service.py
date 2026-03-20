from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import (
    CategoryRepository,
    ProductRepository,
    RoleRepository,
    UserRepository,
)
from gems_marketplace.models.models import Product, User
from gems_marketplace.schemas.product import ProductUpdate


class SellerService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self.session = session
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.product_repo = product_repo
        self.category_repo = category_repo

    async def get_seller_products(self, seller: User) -> list[Product]:
        product_list = await self.product_repo.list_by_seller_id(
            seller_id=seller.id, limit=10, published=True
        )
        return product_list

    async def create_seller_product(
        self, seller: User, product_in: Product, category_name: str
    ) -> Product:
        category = await self.category_repo.get_by_name(category_name)
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )
        # вынети потом в отделную функцию
        product = Product(
            title=product_in.title,
            description=product_in.description,
            price=product_in.price,
            quantity=product_in.quantity,
            category_id=product_in.category_id,
            seller_id=seller.id,
        )
        await self.product_repo.add_in_db(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def update_seller_product(
        self, seller: User, product_id: int, product_in: ProductUpdate
    ) -> Product:
        db_product = await self.product_repo.get_by_id(product_id)
        if db_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )
        if db_product.seller_id != seller.id:
            raise HTTPException(
                status_code=403,
                detail="You cannot edit another seller's product",
            )
        if self.product_repo.get_by_id(product_in.category_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )
        db_product.title = product_in.title
        db_product.description = product_in.description
        db_product.price = product_in.price
        db_product.quantity = product_in.quantity
        db_product.category_id = product_in.category_id
        await self.session.flush()
        await self.session.refresh(db_product)
        return db_product

    async def delete_seller_product_by_id(
        self,
        seller: User,
        product_id: int,
    ) -> None:
        product = await self.product_repo.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.seller_id != seller.id:
            raise HTTPException(
                status_code=403,
                detail="You cannot delete another seller's product",
            )
        await self.product_repo.delete(product)
