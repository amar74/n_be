"""auto

Revision ID: a672e6862546
Revises: bf6419186bf8
Create Date: 2025-08-31 20:01:03.955173

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a672e6862546'
down_revision: Union[str, None] = 'bf6419186bf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('formbricks_projects',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('project_id', sa.String(length=255), nullable=True),
    sa.Column('dev_env_id', sa.String(length=255), nullable=True),
    sa.Column('prod_env_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_formbricks_projects_id'), 'formbricks_projects', ['id'], unique=True)
    op.add_column('organizations', sa.Column('formbricks_organization_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('formbricks_user_id', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'formbricks_user_id')
    op.drop_column('organizations', 'formbricks_organization_id')
    op.drop_index(op.f('ix_formbricks_projects_id'), table_name='formbricks_projects')
    op.drop_table('formbricks_projects')


