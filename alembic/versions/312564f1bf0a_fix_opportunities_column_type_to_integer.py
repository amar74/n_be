"""fix opportunities column type to Integer

Revision ID: 312564f1bf0a
Revises: 247287955082
Create Date: 2025-10-13 22:49:00.591835

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '312564f1bf0a'
down_revision: Union[str, None] = '247287955082'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


