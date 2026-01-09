"""merge_contracts_and_vendors

Revision ID: 8a42655a3477
Revises: contracts_module_20250128, 34f372e002b6
Create Date: 2025-12-31 05:05:39.515320

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8a42655a3477'
down_revision: Union[str, None] = ('contracts_module_20250128', '34f372e002b6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


