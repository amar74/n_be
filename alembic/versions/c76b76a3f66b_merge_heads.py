"""merge heads

Revision ID: c76b76a3f66b
Revises: 856ebd86a964, add_vendors_table
Create Date: 2025-10-13 04:42:02.672959

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c76b76a3f66b'
down_revision: Union[str, None] = ('856ebd86a964', 'add_vendors_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


