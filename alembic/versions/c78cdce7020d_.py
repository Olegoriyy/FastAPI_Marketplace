"""empty message

Revision ID: c78cdce7020d
Revises: 48201efd3864
Create Date: 2026-03-07 12:47:37.551129
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c78cdce7020d'
down_revision: Union[str, Sequence[str], None] = '48201efd3864'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_USERS_ROLE_ID_ROLES = 'fk_users_role_id_roles'


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))

    op.create_foreign_key(
        FK_USERS_ROLE_ID_ROLES,
        'users',
        'roles',
        ['role_id'],
        ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    fk_name = None
    for fk in inspector.get_foreign_keys('users'):
        if fk.get('referred_table') == 'roles' and fk.get('constrained_columns') == [
            'role_id'
        ]:
            fk_name = fk.get('name')
            break

    if fk_name:
        op.drop_constraint(fk_name, 'users', type_='foreignkey')

    op.drop_column('users', 'role_id')
    op.drop_table('roles')
