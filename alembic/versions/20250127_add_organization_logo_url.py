"""add organization logo_url field

Revision ID: add_organization_logo_url
Revises: add_proposals_module
Create Date: 2025-01-27

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_organization_logo_url"
down_revision: Union[str, None] = "add_roles_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add logo_url column to organizations table
    op.add_column('organizations', sa.Column('logo_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove logo_url column from organizations table
    op.drop_column('organizations', 'logo_url')

