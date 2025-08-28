"""fix clienttype enum values

Revision ID: c3c200e56056
Revises: 4639c8c5af9a
Create Date: 2025-08-28 15:43:57.612895

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3c200e56056'
down_revision: Union[str, None] = '4639c8c5af9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


