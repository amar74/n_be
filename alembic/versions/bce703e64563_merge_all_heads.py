"""merge all heads

Revision ID: bce703e64563
Revises: opp_ingestion_20251113, 406dbe169215, b32bfc74fab9, add_password_reset_tokens
Create Date: 2025-11-15 07:57:16.367018

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'bce703e64563'
down_revision: Union[str, None] = ('opp_ingestion_20251113', '406dbe169215', 'b32bfc74fab9', 'add_password_reset_tokens')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


