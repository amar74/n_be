"""create staff planning tables

Revision ID: create_staff_planning_tables
Revises: 
Create Date: 2025-10-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_staff_planning_tables'
down_revision = 'create_employees_001'  # Depends on employees table
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create staff_plans table
    op.create_table(
        'staff_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('project_name', sa.String(length=255), nullable=False),
        sa.Column('project_description', sa.Text(), nullable=True),
        sa.Column('project_start_date', sa.Date(), nullable=False),
        sa.Column('duration_months', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('overhead_rate', sa.Float(), nullable=False, server_default='25.0'),
        sa.Column('profit_margin', sa.Float(), nullable=False, server_default='15.0'),
        sa.Column('annual_escalation_rate', sa.Float(), nullable=False, server_default='3.0'),
        sa.Column('total_labor_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_overhead', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_profit', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_price', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('yearly_breakdown', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['opportunities.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_staff_plans_id', 'staff_plans', ['id'])
    op.create_index('ix_staff_plans_project_id', 'staff_plans', ['project_id'])
    op.create_index('ix_staff_plans_status', 'staff_plans', ['status'])
    
    # Create staff_allocations table
    op.create_table(
        'staff_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('staff_plan_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=True),
        sa.Column('start_month', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('end_month', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('hours_per_week', sa.Float(), nullable=False, server_default='40.0'),
        sa.Column('allocation_percentage', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('hourly_rate', sa.Float(), nullable=False),
        sa.Column('monthly_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='planned'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['staff_plan_id'], ['staff_plans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['employees.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_staff_allocations_id', 'staff_allocations', ['id'])
    op.create_index('ix_staff_allocations_staff_plan_id', 'staff_allocations', ['staff_plan_id'])
    op.create_index('ix_staff_allocations_resource_id', 'staff_allocations', ['resource_id'])
    
    # Create resource_utilization table
    op.create_table(
        'resource_utilization',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('total_allocated_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('utilization_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_overallocated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_underutilized', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('calculated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['resource_id'], ['employees.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_resource_utilization_id', 'resource_utilization', ['id'])
    op.create_index('ix_resource_utilization_resource_id', 'resource_utilization', ['resource_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_resource_utilization_resource_id', table_name='resource_utilization')
    op.drop_index('ix_resource_utilization_id', table_name='resource_utilization')
    op.drop_table('resource_utilization')
    
    op.drop_index('ix_staff_allocations_resource_id', table_name='staff_allocations')
    op.drop_index('ix_staff_allocations_staff_plan_id', table_name='staff_allocations')
    op.drop_index('ix_staff_allocations_id', table_name='staff_allocations')
    op.drop_table('staff_allocations')
    
    op.drop_index('ix_staff_plans_status', table_name='staff_plans')
    op.drop_index('ix_staff_plans_project_id', table_name='staff_plans')
    op.drop_index('ix_staff_plans_id', table_name='staff_plans')
    op.drop_table('staff_plans')

