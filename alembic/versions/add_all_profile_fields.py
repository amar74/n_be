"""add_all_profile_fields

Revision ID: profile_fields_001  
Revises: d34039d97e31
Create Date: 2025-10-25 20:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'profile_fields_001'
down_revision: Union[str, None] = 'd34039d97e31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add bio field
    op.add_column('users', sa.Column('bio', sa.String(length=500), nullable=True))
    
    # Add address fields
    op.add_column('users', sa.Column('address', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('state', sa.String(length=2), nullable=True))
    op.add_column('users', sa.Column('zip_code', sa.String(length=10), nullable=True))
    
    # Add country field with default
    op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True, server_default='United States'))
    
    # Add preferences
    op.add_column('users', sa.Column('timezone', sa.String(length=50), nullable=True, server_default='America/New_York'))
    op.add_column('users', sa.Column('language', sa.String(length=10), nullable=True, server_default='en'))


def downgrade() -> None:
    # Remove all added columns
    op.drop_column('users', 'language')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'country')
    op.drop_column('users', 'zip_code')
    op.drop_column('users', 'state')
    op.drop_column('users', 'city')
    op.drop_column('users', 'address')
    op.drop_column('users', 'bio')
