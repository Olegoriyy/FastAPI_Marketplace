"""empty message

Revision ID: e804829c8eae
Revises: c78cdce7020d
Create Date: 2026-03-09 16:35:51.965562
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e804829c8eae'
down_revision: Union[str, Sequence[str], None] = 'c78cdce7020d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


productstatus_enum = postgresql.ENUM(
    'DRAFT',
    'PENDING',
    'PUBLISHED',
    'REJECTED',
    name='productstatus',
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    productstatus_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table(
        ' products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('status', productstatus_enum, nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updatet_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index(
        op.f('ix_ products_category_id'),
        ' products',
        ['category_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_ products_seller_id'),
        ' products',
        ['seller_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_ products_seller_id'), table_name=' products')
    op.drop_index(op.f('ix_ products_category_id'), table_name=' products')
    op.drop_table(' products')

    productstatus_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_table('categories')
