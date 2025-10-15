"""add cascade delete to users->organizations relation

Revision ID: 00e45db1a28a
Revises: 96a826ae5ed5
Create Date: 2025-08-26 17:08:18.173759

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '00e45db1a28a'
down_revision: Union[str, None] = '96a826ae5ed5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("users_org_id_fkey", "users", type_="foreignkey")

    op.create_foreign_key(
        "users_org_id_fkey",
        "users",
        "organizations",
        ["org_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("users_org_id_fkey", "users", type_="foreignkey")

    op.create_foreign_key(
        "users_org_id_fkey",
        "users",
        "organizations",
        ["org_id"],
        ["id"],
    )

