"""add_approval_status_and_notes_to_accounts

Revision ID: 27y2jabi8qf1
Revises: 583142f12364
Create Date: 2025-10-25 19:30:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '27y2jabi8qf1'
down_revision: Union[str, None] = '583142f12364'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add approval_status column with default value 'pending'
    op.add_column('accounts', sa.Column('approval_status', sa.String(length=20), nullable=True, server_default='pending'))
    # Add approval_notes column
    op.add_column('accounts', sa.Column('approval_notes', sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column('accounts', 'approval_notes')
    op.drop_column('accounts', 'approval_status')
