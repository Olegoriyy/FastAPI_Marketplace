from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.models.models import Product


async def get_product_by_id(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


async def create_product(session: AsyncSession, product: Product) -> Product:
    session.add(product)
    await session.flush()
    await session.refresh(product)
    return product


async def list_products_by_category(
    session: AsyncSession,
    category_id: int | None,
    limit: int = 10,
    published: bool = True,
) -> list[Product]:
    stmt = (
        select(Product)
        .where(Product.category_id == category_id, Product.published == published)
        .limit(limit)
    )
    result = await session.scalars(stmt)
    return list(result.all())


async def list_products_by_seller(
    session: AsyncSession,
    seller_id: int,
    limit: int = 10,
    published: bool = True,
) -> list[Product]:
    stmt = (
        select(Product)
        .where(Product.seller_id == seller_id, Product.published == published)
        .limit(limit)
    )
    result = await session.scalars(stmt)
    return list(result.all())


async def delete_product(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
