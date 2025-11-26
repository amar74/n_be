"""merge survey branches

Revision ID: b32bfc74fab9
Revises: profile_fields_001, survey_002
Create Date: 2025-11-15 07:56:56.010623

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b32bfc74fab9'
down_revision: Union[str, None] = ('profile_fields_001', 'survey_002')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


