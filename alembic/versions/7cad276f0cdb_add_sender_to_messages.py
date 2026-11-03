"""add sender to messages

Revision ID: 7cad276f0cdb
Revises: 7edc71df5b28
Create Date: 2026-10-28 11:29:35.179308

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7cad276f0cdb"
down_revision: Union[str, Sequence[str], None] = "7edc71df5b28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


sender_enum = postgresql.ENUM(
    "ai",
    "first_user",
    "second_user",
    name="sender",
    create_type=False,
)


def upgrade() -> None:
    sender_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "messages",
        sa.Column("sender", sender_enum, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("messages", "sender")
    sender_enum.drop(op.get_bind(), checkfirst=True)
