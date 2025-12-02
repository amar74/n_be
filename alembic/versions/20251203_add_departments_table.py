"""add departments table

Revision ID: add_departments_001
Revises: 20251202_add_notifications_table
Create Date: 2025-12-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'add_departments_001'
down_revision = '20251202_add_filter_presets'  # Point to latest head
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create departments table
    op.create_table(
        'departments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('manager_id', UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('org_id', 'name', name='uq_departments_org_name'),
    )
    
    # Create indexes
    op.create_index('idx_departments_org_id', 'departments', ['org_id'])
    op.create_index('idx_departments_manager_id', 'departments', ['manager_id'])
    op.create_index('idx_departments_is_active', 'departments', ['is_active'])


def downgrade() -> None:
    op.drop_index('idx_departments_is_active', table_name='departments')
    op.drop_index('idx_departments_manager_id', table_name='departments')
    op.drop_index('idx_departments_org_id', table_name='departments')
    op.drop_table('departments')

