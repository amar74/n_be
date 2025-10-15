"""add vendors table

Revision ID: add_vendors_table
Revises: 00e45db1a28a
Create Date: 2025-10-11 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'add_vendors_table'
down_revision: Union[str, None] = '00e45db1a28a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('vendors',
    sa.Column('id', UUID(as_uuid=True), nullable=False),
    sa.Column('vendor_name', sa.String(length=255), nullable=False),
    sa.Column('organisation', sa.String(length=255), nullable=False),
    sa.Column('website', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('contact_number', sa.String(length=20), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)
    op.create_index(op.f('ix_vendors_email'), 'vendors', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_vendors_email'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_id'), table_name='vendors')
    op.drop_table('vendors')
