"""merge employee branches

Revision ID: 406dbe169215
Revises: staff_alloc_escalation, create_account_team_001
Create Date: 2025-11-15 07:56:59.428569

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '406dbe169215'
down_revision: Union[str, None] = ('staff_alloc_escalation', 'create_account_team_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


