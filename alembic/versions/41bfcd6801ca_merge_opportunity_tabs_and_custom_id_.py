"""merge opportunity tabs and custom id fields

Revision ID: 41bfcd6801ca
Revises: 001, add_custom_id_fields
Create Date: 2025-10-18 03:56:22.482136

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '41bfcd6801ca'
down_revision: Union[str, None] = ('001', 'add_custom_id_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


