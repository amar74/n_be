"""add attendance table

Revision ID: 20251206_add_attendance_table
Revises: add_user_profile_picture_url
Create Date: 2025-12-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '20251206_add_attendance_table'
down_revision = 'add_user_profile_picture_url'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create attendance table
    op.create_table(
        'attendance',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('employee_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('punch_in', sa.String(50), nullable=True),
        sa.Column('punch_out', sa.String(50), nullable=True),
        sa.Column('work_hours', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('employee_id', 'date', name='uq_attendance_employee_date'),
    )
    
    # Create indexes
    op.create_index('ix_attendance_id', 'attendance', ['id'])
    op.create_index('ix_attendance_employee_id', 'attendance', ['employee_id'])
    op.create_index('ix_attendance_user_id', 'attendance', ['user_id'])
    op.create_index('ix_attendance_date', 'attendance', ['date'])
    op.create_index('ix_attendance_employee_date', 'attendance', ['employee_id', 'date'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_attendance_employee_date', table_name='attendance')
    op.drop_index('ix_attendance_date', table_name='attendance')
    op.drop_index('ix_attendance_user_id', table_name='attendance')
    op.drop_index('ix_attendance_employee_id', table_name='attendance')
    op.drop_index('ix_attendance_id', table_name='attendance')
    op.drop_table('attendance')
