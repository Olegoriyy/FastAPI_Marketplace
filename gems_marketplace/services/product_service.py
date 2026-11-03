from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.contracts.repositories import ProductRepository
from gems_marketplace.models.models import Product, User
from gems_marketplace.schemas.product import ProductCreate, ProductPublic, ProductUpdate
from gems_marketplace.services.category_service import CategoryService
from gems_marketplace.services.role_service import RoleService


class ProductService:
    def __init__(
        self,
        session: AsyncSession,
        product_repo: ProductRepository,
        category_service: CategoryService,
        role_service: RoleService,
    ):
        self.session = session
        self.product_repo = product_repo
        self.category_service = category_service
        self.role_service = role_service

    async def get_by_id(self, product_id: int) -> Product:
        result = await self.product_repo.get_by_id(product_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return result

    async def add_in_db(self, product_in: ProductCreate, user_id: int) -> Product:
        category = await self.category_service.get_by_id(product_in.category_id)
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        product = Product(
            title=product_in.title,
            description=product_in.description,
            price=product_in.price,
            quantity=product_in.quantity,
            category_id=category.id,
            seller_id=user_id,
        )

        await self.product_repo.add_in_db(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def update(self, product_id: int, product_data: ProductUpdate, user: User):

        user_role = await self.role_service.get_by_id(user.role_id)
        db_product = await self.get_by_id(product_id)

        if user_role.name == "seller":
            if db_product.seller_id != user.id:
                raise HTTPException(
                    status_code=403,
                    detail="You cannot edit another seller's product",
                )

        data = {}

        for key, value in product_data:
            if value is not None:
                data[key] = value

        if "category_id" in data:
            category = await self.category_service.get_by_id(data["category_id"])
            if category is None:
                raise HTTPException(404, "No such Category")

        new_product = await self.product_repo.update(product_id=product_id, data=data)

        return new_product

    async def list_by_category_id(
        self, category_id: int, limit: int, published: bool, all: bool = True
    ) -> list[Product]:
        return await self.product_repo.list_by_category_id(
            category_id, limit, published, all=all
        )

    async def list_by_seller_id(
        self, seller_id: int, limit: int = 10, published: bool = True
    ) -> list[Product]:
        return await self.product_repo.list_by_seller_id(seller_id, limit, published)

    async def delete(self, product_id: int, user: User) -> None:
        product = await self.get_by_id(product_id)
        user_role = await self.role_service.get_by_id(user.role_id)

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        if user_role.name == "seller":
            if product.seller_id != user.id:
                raise HTTPException(
                    status_code=403,
                    detail="You cannot delete another seller's product",
                )

        await self.product_repo.delete(product)

    async def get_all_products(self):
        return await self.product_repo.list_all_products()
