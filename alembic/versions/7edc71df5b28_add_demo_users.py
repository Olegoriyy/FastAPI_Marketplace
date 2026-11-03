"""add demo users

Revision ID: 7edc71df5b28
Revises: 63f5d5cf9d7a
Create Date: 2026-10-28 10:08:21.894351

"""

from typing import Sequence, Union

import sqlalchemy as sa
from pwdlib import PasswordHash

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7edc71df5b28"
down_revision: Union[str, Sequence[str], None] = "63f5d5cf9d7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
