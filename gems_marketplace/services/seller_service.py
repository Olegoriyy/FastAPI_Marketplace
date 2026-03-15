from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import Product, User
from gems_marketplace.repositories.categories import (
    get_category_by_id,
    get_category_by_name,
)
from gems_marketplace.repositories.products import (
    create_product,
    delete_product,
    get_product_by_id,
    list_products_by_seller,
)
from gems_marketplace.schemas.product import ProductUpdate


async def create_seller_product(
    session: AsyncSession, seller: User, product_in: Product, category_name: str
):
    category = await get_category_by_name(session, category_name)
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
        category_id=product_in.category_id,
        seller_id=seller.id,
    )
    created_product = await create_product(session, product)
    return created_product


async def get_seller_products(session: AsyncSession, seller: User):
    product_list = await list_products_by_seller(session, seller.id)
    return product_list


async def update_seller_prouct(
    session: AsyncSession, seller: User, product_id: int, product_in: ProductUpdate
) -> Product:
    db_product = await get_product_by_id(session, product_id)
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
    if get_category_by_id(product_in.category_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    db_product.title = product_in.title
    db_product.description = product_in.description
    db_product.price = product_in.price
    db_product.quantity = product_in.quantity
    db_product.category_id = product_in.category_id
    await session.flush()
    updated_product = await get_product_by_id(session, db_product.id)
    return updated_product


async def delete_seller_product_by_id(
    session: AsyncSession,
    seller: User,
    product_id: int,
) -> None:
    product = await get_product_by_id(session, product_id)
    if product.seller_id != seller.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete another seller's product",
        )
    await delete_product(session, product)
