import asyncio
import json
from decimal import Decimal
from getpass import getpass
from pathlib import Path

from sqlalchemy import select

from gems_marketplace.core.security.hashing_password import hashing_password
from gems_marketplace.db.sessions import (
    async_engine,
    async_session_factory,
)
from gems_marketplace.models.models import Category, Product, Role, User


async def main() -> None:
    data_path = Path(__file__).with_name("demo_products.json")
    products_data = json.loads(data_path.read_text(encoding="utf-8"))

    try:
        async with async_session_factory() as session:
            seller_role = await session.scalar(
                select(Role).where(Role.name == "seller")
            )

            if seller_role is None:
                raise RuntimeError("В базе отсутствует роль seller")

            seller = await session.scalar(
                select(User).where(User.username == "rag_demo_seller")
            )

            if seller is None:
                password = getpass("Пароль тестового продавца: ")

                seller = User(
                    username="rag_demo_seller",
                    email="rag_demo_seller@example.test",
                    hashed_password=hashing_password(password),
                    role_id=seller_role.id,
                )

                session.add(seller)
                await session.commit()

                print(f"Тестовый продавец создан: id={seller.id}")
            else:
                if (
                    seller.role_id != seller_role.id
                    or seller.email != "rag_demo_seller@example.test"
                ):
                    raise RuntimeError(
                        "Имя rag_demo_seller занято другой учётной записью"
                    )

                print(f"Тестовый продавец уже существует: id={seller.id}")

            categories = list(await session.scalars(select(Category)))
            categories_by_name = {category.name: category.id for category in categories}

            existing_titles = set(
                await session.scalars(
                    select(Product.title).where(Product.seller_id == seller.id)
                )
            )

            added = 0
            skipped = 0

            for item in products_data:
                if item["title"] in existing_titles:
                    skipped += 1
                    continue

                category_id = categories_by_name.get(item["category_name"])
                if category_id is None:
                    raise RuntimeError(f"Категория не найдена: {item['category_name']}")

                product = Product(
                    seller_id=seller.id,
                    category_id=category_id,
                    title=item["title"],
                    description=item["description"],
                    price=Decimal(item["price"]),
                    quantity=item["quantity"],
                    published=item["published"],
                )

                session.add(product)
                existing_titles.add(item["title"])
                added += 1

            await session.commit()
            print(f"Добавлено: {added}. Уже существовало: {skipped}.")

    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
