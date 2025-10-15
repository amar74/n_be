"""rename address/contact columns and update FKs

Revision ID: a9aa2b485524
Revises: 00e45db1a28a
Create Date: 2025-08-26 17:23:25.111671

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a9aa2b485524"
down_revision: Union[str, None] = "00e45db1a28a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "organizations_address_fkey",
        "organizations",
        type_="foreignkey",
        if_exists=True,
    )
    op.drop_constraint(
        "organizations_contact_fkey",
        "organizations",
        type_="foreignkey",
        if_exists=True,
    )

    op.alter_column("organizations", "address", new_column_name="address_id")
    op.alter_column("organizations", "contact", new_column_name="contact_id")

    op.create_foreign_key(
        "organizations_address_id_fkey",
        "organizations",
        "address",
        ["address_id"],
        ["id"],
    )
    op.create_foreign_key(
        "organizations_contact_id_fkey",
        "organizations",
        "contacts",
        ["contact_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "organizations_address_id_fkey",
        "organizations",
        type_="foreignkey",
        if_exists=True,
    )
    op.drop_constraint(
        "organizations_contact_id_fkey",
        "organizations",
        type_="foreignkey",
        if_exists=True,
    )

    op.alter_column("organizations", "address_id", new_column_name="address")
    op.alter_column("organizations", "contact_id", new_column_name="contact")

    op.create_foreign_key(
        "organizations_address_fkey",
        "organizations",
        "address",
        ["address"],
        ["id"],
    )
    op.create_foreign_key(
        "organizations_contact_fkey",
        "organizations",
        "contact",
        ["contact"],
        ["id"],
    )
