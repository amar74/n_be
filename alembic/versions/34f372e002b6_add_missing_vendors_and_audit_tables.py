"""add_missing_vendors_and_audit_tables

Revision ID: 34f372e002b6
Revises: 20250115_add_proposal_type
Create Date: 2025-12-20 21:22:36.867820

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = '34f372e002b6'
down_revision: Union[str, None] = '20250115_add_proposal_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if tables exist before creating (idempotent)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    # Create vendors table if it doesn't exist
    if 'vendors' not in tables:
        op.create_table('vendors',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_name', sa.String(length=255), nullable=False),
        sa.Column('organisation', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('contact_number', sa.String(length=20), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('payment_terms', sa.String(length=100), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendors_email'), 'vendors', ['email'], unique=True)
        op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)
    
    # Create account_audit_logs table if it doesn't exist
    if 'account_audit_logs' not in tables:
        op.create_table('account_audit_logs',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.account_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_account_audit_logs_account_id'), 'account_audit_logs', ['account_id'], unique=False)
        op.create_index(op.f('ix_account_audit_logs_action'), 'account_audit_logs', ['action'], unique=False)
        op.create_index(op.f('ix_account_audit_logs_created_at'), 'account_audit_logs', ['created_at'], unique=False)
        op.create_index(op.f('ix_account_audit_logs_id'), 'account_audit_logs', ['id'], unique=True)
        op.create_index(op.f('ix_account_audit_logs_user_id'), 'account_audit_logs', ['user_id'], unique=False)
    
    # Create vendor_qualifications table if it doesn't exist
    if 'vendor_qualifications' not in tables:
        from sqlalchemy.dialects.postgresql import JSONB
        op.create_table('vendor_qualifications',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_id', UUID(as_uuid=True), nullable=False),
        sa.Column('financial_stability', sa.String(length=50), nullable=True, comment='Financial stability rating: excellent, good, fair, poor'),
        sa.Column('credentials_verified', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='Whether vendor credentials have been verified'),
        sa.Column('certifications', JSONB(astext_type=sa.Text()), nullable=True, comment='List of certifications (e.g., ISO 9001, ISO 27001)'),
        sa.Column('qualification_score', sa.String(length=10), nullable=True, comment='Overall qualification score (0-100)'),
        sa.Column('risk_level', sa.String(length=20), nullable=True, comment='Risk level: low, medium, high'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional qualification notes'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Whether this is the current/active qualification (latest one)'),
        sa.Column('assessment_type', sa.String(length=50), nullable=True, comment='Type of assessment: manual, ai_auto, periodic_review, etc.'),
        sa.Column('assessed_by', UUID(as_uuid=True), nullable=True),
        sa.Column('last_assessed', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['assessed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendor_qualifications_assessed_by'), 'vendor_qualifications', ['assessed_by'], unique=False)
        op.create_index(op.f('ix_vendor_qualifications_id'), 'vendor_qualifications', ['id'], unique=False)
        op.create_index(op.f('ix_vendor_qualifications_is_active'), 'vendor_qualifications', ['is_active'], unique=False)
        op.create_index(op.f('ix_vendor_qualifications_vendor_id'), 'vendor_qualifications', ['vendor_id'], unique=False)
    
    # Add vendor_id foreign keys if vendors table exists and FKs don't exist
    if 'vendors' in tables:
        # Check and add FK to purchase_orders
        if 'purchase_orders' in tables:
            try:
                fks = [fk['name'] for fk in inspector.get_foreign_keys('purchase_orders')]
                if not any('vendor_id' in str(fk) for fk in fks):
                    op.create_foreign_key(None, 'purchase_orders', 'vendors', ['vendor_id'], ['id'])
            except Exception:
                pass  # FK might already exist
        
        # Check and add FK to rfq_responses
        if 'rfq_responses' in tables:
            try:
                fks = [fk['name'] for fk in inspector.get_foreign_keys('rfq_responses')]
                if not any('vendor_id' in str(fk) for fk in fks):
                    op.create_foreign_key(None, 'rfq_responses', 'vendors', ['vendor_id'], ['id'])
            except Exception:
                pass
        
        # Check and add FK to vendor_invoices
        if 'vendor_invoices' in tables:
            try:
                fks = [fk['name'] for fk in inspector.get_foreign_keys('vendor_invoices')]
                if not any('vendor_id' in str(fk) for fk in fks):
                    op.create_foreign_key(None, 'vendor_invoices', 'vendors', ['vendor_id'], ['id'])
            except Exception:
                pass


def downgrade() -> None:
    # Drop tables if they exist
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'vendor_qualifications' in tables:
        op.drop_index(op.f('ix_vendor_qualifications_vendor_id'), table_name='vendor_qualifications')
        op.drop_index(op.f('ix_vendor_qualifications_is_active'), table_name='vendor_qualifications')
        op.drop_index(op.f('ix_vendor_qualifications_id'), table_name='vendor_qualifications')
        op.drop_index(op.f('ix_vendor_qualifications_assessed_by'), table_name='vendor_qualifications')
        op.drop_table('vendor_qualifications')
    
    if 'account_audit_logs' in tables:
        op.drop_index(op.f('ix_account_audit_logs_user_id'), table_name='account_audit_logs')
        op.drop_index(op.f('ix_account_audit_logs_id'), table_name='account_audit_logs')
        op.drop_index(op.f('ix_account_audit_logs_created_at'), table_name='account_audit_logs')
        op.drop_index(op.f('ix_account_audit_logs_action'), table_name='account_audit_logs')
        op.drop_index(op.f('ix_account_audit_logs_account_id'), table_name='account_audit_logs')
        op.drop_table('account_audit_logs')
    
    if 'vendors' in tables:
        op.drop_index(op.f('ix_vendors_id'), table_name='vendors')
        op.drop_index(op.f('ix_vendors_email'), table_name='vendors')
        op.drop_table('vendors')

