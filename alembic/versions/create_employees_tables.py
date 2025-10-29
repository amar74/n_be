"""create employees and resumes tables

Revision ID: create_employees_001
Revises: 
Create Date: 2025-01-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TIMESTAMP

# revision identifiers, used by Alembic.
revision = 'create_employees_001'
down_revision = None  # Update this with your latest migration ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create employees table
    op.create_table(
        'employees',
        sa.Column('id', UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=True, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True, index=True),
        sa.Column('employee_number', sa.String(20), nullable=False, unique=True, index=True),
        
        # Basic Information
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('phone', sa.String(20), nullable=True),
        
        # Job Information
        sa.Column('job_title', sa.String(255), nullable=True),
        sa.Column('role', sa.String(100), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),
        
        # Financial
        sa.Column('bill_rate', sa.DECIMAL(10, 2), nullable=True),
        
        # Status and Onboarding
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', index=True),
        sa.Column('invite_token', sa.String(255), nullable=True, unique=True),
        sa.Column('invite_sent_at', TIMESTAMP, nullable=True),
        sa.Column('onboarding_complete', sa.Boolean, nullable=False, server_default='false'),
        
        # Experience and Skills (AI enriched)
        sa.Column('experience', sa.String(100), nullable=True),
        sa.Column('skills', ARRAY(sa.String), nullable=True),
        sa.Column('ai_suggested_role', sa.String(100), nullable=True),
        sa.Column('ai_suggested_skills', ARRAY(sa.String), nullable=True),
        
        # Review Notes
        sa.Column('review_notes', sa.Text, nullable=True),
        
        # Audit fields
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
    )

    # Create resumes table
    op.create_table(
        'resumes',
        sa.Column('id', UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('employee_id', UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False, index=True),
        
        # File Information
        sa.Column('file_url', sa.Text, nullable=False),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        
        # AI Parsed Data
        sa.Column('ai_parsed_json', JSONB, nullable=True),
        sa.Column('skills', ARRAY(sa.String), nullable=True),
        sa.Column('experience_summary', sa.Text, nullable=True),
        sa.Column('certifications', ARRAY(sa.String), nullable=True),
        
        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='uploaded'),
        sa.Column('parse_error', sa.Text, nullable=True),
        
        # Audit
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('parsed_at', TIMESTAMP, nullable=True),
    )

    # Create indexes for performance
    op.create_index('idx_employees_company_status', 'employees', ['company_id', 'status'])
    op.create_index('idx_employees_email', 'employees', ['email'])
    op.create_index('idx_resumes_employee', 'resumes', ['employee_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_resumes_employee', table_name='resumes')
    op.drop_index('idx_employees_email', table_name='employees')
    op.drop_index('idx_employees_company_status', table_name='employees')
    
    # Drop tables
    op.drop_table('resumes')
    op.drop_table('employees')

