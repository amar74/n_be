"""merge_variance_explanations_with_vendor_qualifications

Revision ID: 0d32e3791e12
Revises: variance_explanations_20250129, 858159ac3384
Create Date: 2025-12-01 22:44:05.242832

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0d32e3791e12'
down_revision: Union[str, None] = ('variance_explanations_20250129', '858159ac3384')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


