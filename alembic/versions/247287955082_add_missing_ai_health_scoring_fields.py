"""Add missing AI health scoring fields

Revision ID: 247287955082
Revises: c76b76a3f66b
Create Date: 2025-10-13 04:47:03.639671

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '247287955082'
down_revision: Union[str, None] = 'c76b76a3f66b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f('ix_account_documents_account_id'), table_name='account_documents')
    op.drop_index(op.f('ix_account_documents_id'), table_name='account_documents')
    op.drop_table('account_documents')
    op.drop_index(op.f('ix_vendors_email'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_id'), table_name='vendors')
    op.drop_table('vendors')
    op.add_column('accounts', sa.Column('health_trend', sa.String(length=20), nullable=True))
    op.add_column('accounts', sa.Column('risk_level', sa.String(length=20), nullable=True))
    op.add_column('accounts', sa.Column('last_ai_analysis', sa.DateTime(), nullable=True))
    op.add_column('accounts', sa.Column('data_quality_score', sa.Numeric(), nullable=True))
    op.add_column('accounts', sa.Column('revenue_growth', sa.Numeric(), nullable=True))
    op.add_column('accounts', sa.Column('communication_frequency', sa.Numeric(), nullable=True))
    op.add_column('accounts', sa.Column('win_rate', sa.Numeric(), nullable=True))
    op.drop_index(op.f('ix_accounts_name_fts'), table_name='accounts', postgresql_using='gin')
    op.drop_index(op.f('ix_accounts_website_fts'), table_name='accounts', postgresql_using='gin')
    op.drop_index(op.f('ix_address_line1_fts'), table_name='address', postgresql_using='gin')
    op.drop_index(op.f('ix_contacts_email_fts'), table_name='contacts', postgresql_using='gin')


def downgrade() -> None:
    op.create_index(op.f('ix_contacts_email_fts'), 'contacts', [sa.literal_column("to_tsvector('english_unaccent'::regconfig, COALESCE(email, ''::character varying)::text)")], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_address_line1_fts'), 'address', [sa.literal_column("to_tsvector('english_unaccent'::regconfig, COALESCE(line1, ''::character varying)::text)")], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_accounts_website_fts'), 'accounts', [sa.literal_column("to_tsvector('english_unaccent'::regconfig, COALESCE(company_website, ''::character varying)::text)")], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_accounts_name_fts'), 'accounts', [sa.literal_column("to_tsvector('english_unaccent'::regconfig, COALESCE(client_name, ''::character varying)::text)")], unique=False, postgresql_using='gin')
    op.drop_column('accounts', 'win_rate')
    op.drop_column('accounts', 'communication_frequency')
    op.drop_column('accounts', 'revenue_growth')
    op.drop_column('accounts', 'data_quality_score')
    op.drop_column('accounts', 'last_ai_analysis')
    op.drop_column('accounts', 'risk_level')
    op.drop_column('accounts', 'health_trend')
    op.create_table('vendors',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('vendor_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('organisation', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('website', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('contact_number', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=50), server_default=sa.text("'pending'::character varying"), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('approved_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('vendors_pkey')),
    sa.UniqueConstraint('email', name=op.f('vendors_email_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)
    op.create_index(op.f('ix_vendors_email'), 'vendors', ['email'], unique=True)
    op.create_table('account_documents',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('account_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('category', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('file_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('file_path', sa.VARCHAR(length=512), autoincrement=False, nullable=True),
    sa.Column('file_size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('mime_type', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.account_id'], name=op.f('account_documents_account_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('account_documents_pkey'))
    )
    op.create_index(op.f('ix_account_documents_id'), 'account_documents', ['id'], unique=True)
    op.create_index(op.f('ix_account_documents_account_id'), 'account_documents', ['account_id'], unique=False)


