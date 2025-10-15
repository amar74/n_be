"""add custom_id fields to opportunities and organizations

Revision ID: add_custom_id_fields
Revises: 5745592a2d22
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_custom_id_fields'
down_revision = '5745592a2d22'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('opportunities', sa.Column('custom_id', sa.String(20), nullable=True))
    op.create_index('ix_opportunities_custom_id', 'opportunities', ['custom_id'], unique=True)
    
    op.add_column('organizations', sa.Column('custom_id', sa.String(20), nullable=True))
    op.create_index('ix_organizations_custom_id', 'organizations', ['custom_id'], unique=True)


def downgrade():
    op.drop_index('ix_organizations_custom_id', table_name='organizations')
    op.drop_column('organizations', 'custom_id')
    
    op.drop_index('ix_opportunities_custom_id', table_name='opportunities')
    op.drop_column('opportunities', 'custom_id')