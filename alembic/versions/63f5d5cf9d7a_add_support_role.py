"""add support role

Revision ID: 63f5d5cf9d7a
Revises: 2480482fbcba
Create Date: 2026-10-28 09:35:11.981249

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63f5d5cf9d7a"
down_revision: Union[str, Sequence[str], None] = "2480482fbcba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO roles (name) VALUES ('support') ON CONFLICT (name) DO NOTHING"
    )


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE name = 'support'")
