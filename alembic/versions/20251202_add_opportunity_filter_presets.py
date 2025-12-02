"""Add opportunity filter presets table

Revision ID: 20251202_add_filter_presets
Revises: 20251202_add_notifications
Create Date: 2025-12-02 02:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251202_add_filter_presets'
down_revision: Union[str, None] = '20251202_add_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create opportunity_filter_presets table
    op.create_table(
        'opportunity_filter_presets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('filters', postgresql.JSONB(), nullable=False),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_filter_presets_org_user', 'opportunity_filter_presets', ['org_id', 'user_id', 'created_at'])
    op.create_index('ix_filter_presets_shared', 'opportunity_filter_presets', ['org_id', 'is_shared', 'created_at'])
    op.create_index('ix_opportunity_filter_presets_id', 'opportunity_filter_presets', ['id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_opportunity_filter_presets_id', table_name='opportunity_filter_presets')
    op.drop_index('ix_filter_presets_shared', table_name='opportunity_filter_presets')
    op.drop_index('ix_filter_presets_org_user', table_name='opportunity_filter_presets')
    
    # Drop table
    op.drop_table('opportunity_filter_presets')

