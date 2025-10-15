"""create_opportunities_table

Revision ID: 62a366661d81
Revises: 312564f1bf0a
Create Date: 2025-10-14 00:54:22.286429

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '62a366661d81'
down_revision: Union[str, None] = '312564f1bf0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


