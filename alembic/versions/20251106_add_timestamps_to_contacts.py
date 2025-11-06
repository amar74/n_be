"""add timestamps to contacts

Revision ID: add_timestamps_contacts
Revises: 
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_timestamps_contacts'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and updated_at columns to contacts table
    op.add_column('contacts', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.add_column('contacts', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove timestamp columns
    op.drop_column('contacts', 'updated_at')
    op.drop_column('contacts', 'created_at')

