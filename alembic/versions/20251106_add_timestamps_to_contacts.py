"""add timestamps to contacts

Revision ID: add_timestamps_contacts
Revises: 
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_timestamps_contacts'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col['name'] for col in inspector.get_columns('contacts')}

    if 'created_at' not in columns:
        op.add_column('contacts', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))
    if 'updated_at' not in columns:
        op.add_column('contacts', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col['name'] for col in inspector.get_columns('contacts')}

    if 'updated_at' in columns:
        op.drop_column('contacts', 'updated_at')
    if 'created_at' in columns:
        op.drop_column('contacts', 'created_at')

