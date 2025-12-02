"""add roles table

Revision ID: add_roles_001
Revises: add_departments_001
Create Date: 2025-12-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

# revision identifiers, used by Alembic.
revision = 'add_roles_001'
down_revision = 'add_departments_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('color', sa.String(100), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('org_id', 'name', name='uq_roles_org_name'),
    )
    
    # Create indexes
    op.create_index('idx_roles_org_id', 'roles', ['org_id'])
    op.create_index('idx_roles_is_system', 'roles', ['is_system'])


def downgrade() -> None:
    op.drop_index('idx_roles_is_system', table_name='roles')
    op.drop_index('idx_roles_org_id', table_name='roles')
    op.drop_table('roles')

