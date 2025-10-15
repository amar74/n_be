"""removed org name unique

Revision ID: 5ae020ae8f4f
Revises: a672e6862546
Create Date: 2025-08-31 20:35:09.299539

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5ae020ae8f4f'
down_revision: Union[str, None] = 'a672e6862546'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('formbricks_projects', sa.Column('organization_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'formbricks_projects', 'organizations', ['organization_id'], ['id'])
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=True)
    op.drop_constraint(None, 'formbricks_projects', type_='foreignkey')
    op.drop_column('formbricks_projects', 'organization_id')


