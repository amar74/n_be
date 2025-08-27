"""create address and contact tables

Revision ID: e7a38d7ff1cd
Revises: 269154e6abcb
Create Date: 2025-08-26 11:49:41.909133

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e7a38d7ff1cd'
down_revision: Union[str, None] = '269154e6abcb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "address",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("line1", sa.String(255), nullable=False),
        sa.Column("line2", sa.String(255), nullable=True),
        sa.Column("pincode", sa.Integer(), nullable=True),
        sa.Column("org_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "address_org_id_fkey",
        "address", "organizations",
        ["org_id"], ["id"],
        ondelete="CASCADE"
    )
    
    op.create_table(
        "contact",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("org_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "contact_org_id_fkey",
        "contact", "organizations",
        ["org_id"], ["id"],
        ondelete="CASCADE"
    )

def downgrade() -> None:
    op.drop_table("address")
    op.drop_table("contact")


