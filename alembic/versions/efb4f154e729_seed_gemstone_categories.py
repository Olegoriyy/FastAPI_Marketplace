"""seed gemstone categories

Revision ID: efb4f154e729
Revises: 44e96c3d20aa
Create Date: 2026-03-12 15:03:38.710739

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "efb4f154e729"
down_revision: Union[str, Sequence[str], None] = "44e96c3d20aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

GEMSTONE_CATEGORIES: tuple[str, ...] = (
    "Diamond",
    "Emerald",
    "Ruby",
    "Sapphire",
    "Topaz",
    "Amethyst",
    "Aquamarine",
    "Opal",
    "Garnet",
    "Pearl",
    "Jade",
    "Turquoise",
    "Citrine",
    "Tanzanite",
    "Tourmaline",
    "Peridot",
    "Morganite",
    "Moonstone",
    "Onyx",
    "Amber",
    "Quartz",
    "Spinel",
    "Zircon",
    "Alexandrite",
    "Beryl",
)

categories_table = sa.table(
    "categories",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String(length=100)),
)

products_table = sa.table(
    "products",
    sa.column("category_id", sa.Integer),
)


def upgrade() -> None:
    stmt = insert(categories_table).values(
        [{"name": category_name} for category_name in GEMSTONE_CATEGORIES]
    )

    stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
    op.execute(stmt)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "products" in inspector.get_table_names():
        category_in_use = bind.execute(
            sa.select(sa.literal(1))
            .select_from(
                products_table.join(
                    categories_table,
                    products_table.c.category_id == categories_table.c.id,
                )
            )
            .where(categories_table.c.name.in_(GEMSTONE_CATEGORIES))
            .limit(1)
        ).first()

        if category_in_use is not None:
            raise RuntimeError(
                "Cannot downgrade this migration: some seeded categories "
                "are already used by products. Reassign or delete those "
                "products first."
            )

    bind.execute(
        categories_table.delete().where(
            categories_table.c.name.in_(GEMSTONE_CATEGORIES)
        )
    )
