"""add_state_hosting_area_approver_approval_date_columns

Revision ID: 856ebd86a964
Revises: 107b6416b56c
Create Date: 2025-10-11 02:46:59.463392

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '856ebd86a964'
down_revision: Union[str, None] = '107b6416b56c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accounts', sa.Column('hosting_area', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('account_approver', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('approval_date', sa.DateTime(), nullable=True))
    op.add_column('address', sa.Column('state', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'state')
    op.drop_column('accounts', 'approval_date')
    op.drop_column('accounts', 'account_approver')
    op.drop_column('accounts', 'hosting_area')


