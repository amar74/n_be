"""merge user permissions and notes table branches

Revision ID: 07da41c7db8d
Revises: c5d2c5061ca1, dd2f8cc323b0
Create Date: 2025-09-09 21:38:36.274092

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '07da41c7db8d'
down_revision: Union[str, None] = ('c5d2c5061ca1', 'dd2f8cc323b0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


