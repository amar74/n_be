"""add accounts, address, and contacts tables

Revision ID: 21c72d6b7d1a
Revises: f7ac03cbc5f6
Create Date: 2025-08-28 13:45:58.650124

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '21c72d6b7d1a'
down_revision: Union[str, None] = 'f7ac03cbc5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


