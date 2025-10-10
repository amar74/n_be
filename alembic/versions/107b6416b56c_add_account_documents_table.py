"""add account_documents table

Revision ID: 107b6416b56c
Revises: da12f3a1f7b8
Create Date: 2025-10-10 18:49:12.176319

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '107b6416b56c'
down_revision: Union[str, None] = 'da12f3a1f7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create account_documents table
    op.create_table(
        'account_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.account_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_account_documents_id'), 'account_documents', ['id'], unique=True)
    op.create_index(op.f('ix_account_documents_account_id'), 'account_documents', ['account_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_account_documents_account_id'), table_name='account_documents')
    op.drop_index(op.f('ix_account_documents_id'), table_name='account_documents')
    op.drop_table('account_documents')
