"""empty message

Revision ID: 6f2a0f1f7c31
Revises: efb4f154e729
Create Date: 2026-03-20 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6f2a0f1f7c31"
down_revision: Union[str, Sequence[str], None] = "efb4f154e729"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Увеличиваем длины строк в products
    op.alter_column(
        "products",
        "title",
        existing_type=sa.String(length=200),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    op.alter_column(
        "products",
        "description",
        existing_type=sa.String(length=256),
        type_=sa.String(length=3000),
        existing_nullable=False,
    )

    # 2) Если вдруг есть старые users с NULL role_id,
    #    присваиваем им роль buyer перед NOT NULL
    op.execute(
        sa.text(
            """
            UPDATE users
            SET role_id = roles.id
            FROM roles
            WHERE users.role_id IS NULL
              AND roles.name = 'buyer'
            """
        )
    )

    # 3) Делаем users.role_id обязательным
    op.alter_column(
        "users",
        "role_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    bind = op.get_bind()

    # Защитная проверка:
    # если уже есть данные длиннее старых лимитов, откат должен падать явно,
    # а не ломаться неочевидно посередине ALTER COLUMN.
    too_long_title = bind.execute(
        sa.text(
            """
            SELECT 1
            FROM products
            WHERE length(title) > 200
            LIMIT 1
            """
        )
    ).first()

    if too_long_title is not None:
        raise RuntimeError(
            "Cannot downgrade: there are products with title length > 200."
        )

    too_long_description = bind.execute(
        sa.text(
            """
            SELECT 1
            FROM products
            WHERE length(description) > 256
            LIMIT 1
            """
        )
    ).first()

    if too_long_description is not None:
        raise RuntimeError(
            "Cannot downgrade: there are products with description length > 256."
        )

    op.alter_column(
        "users",
        "role_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.alter_column(
        "products",
        "description",
        existing_type=sa.String(length=3000),
        type_=sa.String(length=256),
        existing_nullable=False,
    )

    op.alter_column(
        "products",
        "title",
        existing_type=sa.String(length=255),
        type_=sa.String(length=200),
        existing_nullable=False,
    )
