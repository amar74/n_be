"""add_proposal_type_field

Revision ID: 20250115_add_proposal_type
Revises: 20251206_add_attendance_table
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250115_add_proposal_type'
down_revision: Union[str, None] = '20251206_add_attendance_table'  # Update this to the latest migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create proposal_type enum
    op.execute("""
        CREATE TYPE proposal_type AS ENUM ('proposal', 'brochure', 'interview', 'campaign');
    """)
    
    # Add proposal_type column with default value
    op.add_column('proposals', sa.Column('proposal_type', postgresql.ENUM('proposal', 'brochure', 'interview', 'campaign', name='proposal_type', create_type=False), nullable=False, server_default='proposal'))
    
    # Create index on proposal_type for better query performance
    op.create_index('ix_proposals_proposal_type', 'proposals', ['proposal_type'], unique=False)


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_proposals_proposal_type', table_name='proposals')
    
    # Drop column
    op.drop_column('proposals', 'proposal_type')
    
    # Drop enum type
    op.execute("DROP TYPE proposal_type;")

