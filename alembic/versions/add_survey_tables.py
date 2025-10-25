"""add survey tables

Revision ID: survey_001
Revises: (your_previous_revision)
Create Date: 2025-10-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'survey_001'
down_revision = '5e5bff545a73'  # Latest migration revision
branch_labels = None
depends_on = None


def upgrade():
    # Create survey_status enum
    survey_status_enum = postgresql.ENUM(
        'draft', 'active', 'paused', 'completed', 'archived',
        name='surveystatus'
    )
    survey_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create survey_type enum
    survey_type_enum = postgresql.ENUM(
        'account_feedback', 'customer_satisfaction', 'nps', 
        'opportunity_feedback', 'general',
        name='surveytype'
    )
    survey_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create surveys table
    op.create_table(
        'surveys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('survey_code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.String(2000), nullable=True),
        sa.Column('survey_type', survey_type_enum, nullable=False),
        sa.Column('status', survey_status_enum, nullable=False, server_default='draft'),
        sa.Column('questions', postgresql.JSON, nullable=True),
        sa.Column('settings', postgresql.JSON, nullable=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now(), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_surveys_id', 'surveys', ['id'])
    op.create_index('ix_surveys_org_id', 'surveys', ['org_id'])
    op.create_index('ix_surveys_status', 'surveys', ['status'])
    op.create_index('ix_surveys_created_at', 'surveys', ['created_at'])
    
    # Create survey_distributions table
    op.create_table(
        'survey_distributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), 
                 sa.ForeignKey('surveys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), 
                 sa.ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=True),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), 
                 sa.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=True),
        sa.Column('survey_link', sa.String(500), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('viewed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('is_sent', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for distributions
    op.create_index('ix_survey_distributions_id', 'survey_distributions', ['id'])
    op.create_index('ix_survey_distributions_survey_id', 'survey_distributions', ['survey_id'])
    op.create_index('ix_survey_distributions_account_id', 'survey_distributions', ['account_id'])
    op.create_index('ix_survey_distributions_contact_id', 'survey_distributions', ['contact_id'])
    op.create_index('ix_survey_distributions_is_completed', 'survey_distributions', ['is_completed'])
    
    # Create survey_responses table
    op.create_table(
        'survey_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('response_code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), 
                 sa.ForeignKey('surveys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('distribution_id', postgresql.UUID(as_uuid=True), 
                 sa.ForeignKey('survey_distributions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), 
                 sa.ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=True),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), 
                 sa.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=True),
        sa.Column('response_data', postgresql.JSON, nullable=False),
        sa.Column('finished', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('meta', postgresql.JSON, nullable=True),
        sa.Column('time_to_complete', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now(), nullable=True),
    )
    
    # Create indexes for responses
    op.create_index('ix_survey_responses_id', 'survey_responses', ['id'])
    op.create_index('ix_survey_responses_survey_id', 'survey_responses', ['survey_id'])
    op.create_index('ix_survey_responses_account_id', 'survey_responses', ['account_id'])
    op.create_index('ix_survey_responses_contact_id', 'survey_responses', ['contact_id'])
    op.create_index('ix_survey_responses_finished', 'survey_responses', ['finished'])
    op.create_index('ix_survey_responses_created_at', 'survey_responses', ['created_at'])


def downgrade():
    # Drop tables
    op.drop_table('survey_responses')
    op.drop_table('survey_distributions')
    op.drop_table('surveys')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS surveystatus CASCADE')
    op.execute('DROP TYPE IF EXISTS surveytype CASCADE')
