"""add organization_id to accounts table

Revision ID: 86256bdba01e
Revises: 5ae020ae8f4f
Create Date: 2025-09-01 21:10:22.932388

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '86256bdba01e'
down_revision: Union[str, None] = '5ae020ae8f4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accounts', sa.Column('org_id', sa.UUID(), nullable=True))
    
    op.create_foreign_key(
        'accounts_org_id_fkey',
        'accounts', 'organizations',
        ['org_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('accounts_org_id_fkey', 'accounts', type_='foreignkey')
    
    op.drop_column('accounts', 'org_id')


