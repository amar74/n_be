"""add user profile_picture_url field

Revision ID: add_user_profile_picture_url
Revises: add_organization_logo_url
Create Date: 2025-01-27

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_user_profile_picture_url"
down_revision: Union[str, None] = "add_organization_logo_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add profile_picture_url column to users table
    op.add_column('users', sa.Column('profile_picture_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove profile_picture_url column from users table
    op.drop_column('users', 'profile_picture_url')

