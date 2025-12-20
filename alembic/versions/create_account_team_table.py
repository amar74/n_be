"""create account_team table

Revision ID: create_account_team_001
Revises: create_employees_001
Create Date: 2025-01-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

# revision identifiers, used by Alembic.
revision = 'create_account_team_001'
down_revision = 'create_employees_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table exists before creating
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'account_team' not in tables:
        # Create account_team table (many-to-many relationship)
        op.create_table(
            'account_team',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('account_id', UUID(as_uuid=True), sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('employee_id', UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role_in_account', sa.String(100), nullable=True),
        sa.Column('assigned_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_at', TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('removed_at', TIMESTAMP, nullable=True),
    )
    
        # Create composite index for unique account-employee combination (where not removed)
        op.create_index(
            'idx_account_team_unique',
            'account_team',
            ['account_id', 'employee_id'],
            unique=True,
            postgresql_where=sa.text('removed_at IS NULL')
        )


def downgrade() -> None:
    op.drop_index('idx_account_team_unique', table_name='account_team')
    op.drop_table('account_team')

