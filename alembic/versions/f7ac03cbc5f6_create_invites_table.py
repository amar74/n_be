"""create invites table

Revision ID: f7ac03cbc5f6
Revises: a9aa2b485524
Create Date: 2025-08-27 22:10:33.417480

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta


revision: str = 'f7ac03cbc5f6'
down_revision: Union[str, None] = 'a9aa2b485524'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invites",
        sa.Column("id", sa.UUID(), primary_key=True, default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("org_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String, nullable=False, default="admin"),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("invited_by", sa.UUID(),  nullable=False),
        sa.Column("token", sa.String, nullable=False),
        sa.Column("status", sa.String, default="pending", nullable=False),
        sa.Column("expires_at", sa.DateTime(), default=datetime.utcnow() + timedelta(days=7), nullable=False),
        sa.Column("created_at", sa.DateTime(), default=datetime.utcnow, nullable=False),
    )
    

def downgrade() -> None:
    op.drop_table("invites")



