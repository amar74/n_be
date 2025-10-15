"""add invite status enum

Revision ID: e0f52551bb55
Revises: bf6419186bf8
Create Date: 2025-09-02 12:34:45.546124

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e0f52551bb55'
down_revision: Union[str, None] = '86256bdba01e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE invitestatus AS ENUM ('PENDING', 'ACCEPTED', 'EXPIRED')")
    
    op.execute("ALTER TABLE invites ALTER COLUMN status TYPE invitestatus USING status::invitestatus")


def downgrade() -> None:
    op.execute("ALTER TABLE invites ALTER COLUMN status TYPE character varying USING status::character varying")
    
    op.execute("DROP TYPE invitestatus")
