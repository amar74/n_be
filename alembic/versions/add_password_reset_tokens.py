"""add password reset tokens table

Revision ID: add_password_reset_tokens
Revises: 
Create Date: 2025-10-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_password_reset_tokens'
down_revision = None  # Update this with your latest migration ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table exists before creating
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'password_reset_tokens' not in tables:
        # Create password_reset_tokens table
        op.create_table(
            'password_reset_tokens',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('otp', sa.String(length=6), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('used_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index('idx_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
        op.create_index('idx_password_reset_tokens_otp', 'password_reset_tokens', ['otp'])
        op.create_index('idx_password_reset_tokens_email', 'password_reset_tokens', ['email'])
        op.create_index('idx_password_reset_tokens_expires_at', 'password_reset_tokens', ['expires_at'])
        op.create_index('idx_password_reset_tokens_is_used', 'password_reset_tokens', ['is_used'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_password_reset_tokens_is_used', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_tokens_expires_at', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_tokens_email', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_tokens_otp', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_tokens_user_id', table_name='password_reset_tokens')
    
    # Drop table
    op.drop_table('password_reset_tokens')
