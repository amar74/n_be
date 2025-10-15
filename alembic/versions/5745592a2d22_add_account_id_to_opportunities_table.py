"""add account_id to opportunities table

Revision ID: 5745592a2d22
Revises: 3df021b7005c
Create Date: 2025-10-14 02:30:28.133350

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5745592a2d22'
down_revision: Union[str, None] = '3df021b7005c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('account_documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
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
    op.create_index(op.f('ix_account_documents_account_id'), 'account_documents', ['account_id'], unique=False)
    op.create_index(op.f('ix_account_documents_id'), 'account_documents', ['id'], unique=True)
    op.add_column('opportunities', sa.Column('account_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_opportunities_account_id'), 'opportunities', ['account_id'], unique=False)
    op.create_foreign_key(None, 'opportunities', 'accounts', ['account_id'], ['account_id'])


def downgrade() -> None:
    op.drop_constraint(None, 'opportunities', type_='foreignkey')
    op.drop_index(op.f('ix_opportunities_account_id'), table_name='opportunities')
    op.drop_column('opportunities', 'account_id')
    op.drop_index(op.f('ix_account_documents_id'), table_name='account_documents')
    op.drop_index(op.f('ix_account_documents_account_id'), table_name='account_documents')
    op.drop_table('account_documents')


