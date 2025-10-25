"""create_opportunity_tabs_and_documents_tables

Revision ID: 583142f12364
Revises: survey_001
Create Date: 2025-10-24 17:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '583142f12364'
down_revision = 'survey_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create opportunity_overviews table
    op.create_table('opportunity_overviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_description', sa.Text(), nullable=True),
        sa.Column('project_scope', postgresql.JSON(), nullable=True),
        sa.Column('key_metrics', postgresql.JSON(), nullable=True),
        sa.Column('documents_summary', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_overviews_opportunity_id', 'opportunity_overviews', ['opportunity_id'], unique=False)

    # Create opportunity_stakeholders table
    op.create_table('opportunity_stakeholders',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('designation', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('contact_number', sa.String(length=50), nullable=True),
        sa.Column('influence_level', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_stakeholders_opportunity_id', 'opportunity_stakeholders', ['opportunity_id'], unique=False)

    # Create opportunity_documents table
    op.create_table('opportunity_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('document_url', sa.Text(), nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_documents_opportunity_id', 'opportunity_documents', ['opportunity_id'], unique=False)

    # Create other opportunity tab tables
    op.create_table('opportunity_drivers',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_drivers_opportunity_id', 'opportunity_drivers', ['opportunity_id'], unique=False)

    op.create_table('opportunity_competitors',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('threat_level', sa.String(length=50), nullable=False),
        sa.Column('strengths', postgresql.JSON(), nullable=False),
        sa.Column('weaknesses', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_competitors_opportunity_id', 'opportunity_competitors', ['opportunity_id'], unique=False)

    op.create_table('opportunity_strategies',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('strategy_text', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_strategies_opportunity_id', 'opportunity_strategies', ['opportunity_id'], unique=False)

    op.create_table('opportunity_delivery_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approach', sa.Text(), nullable=False),
        sa.Column('key_phases', postgresql.JSON(), nullable=False),
        sa.Column('identified_gaps', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_delivery_models_opportunity_id', 'opportunity_delivery_models', ['opportunity_id'], unique=False)

    op.create_table('opportunity_team_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('designation', sa.String(length=255), nullable=False),
        sa.Column('experience', sa.String(length=255), nullable=False),
        sa.Column('availability', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_team_members_opportunity_id', 'opportunity_team_members', ['opportunity_id'], unique=False)

    op.create_table('opportunity_references',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_name', sa.String(length=255), nullable=False),
        sa.Column('client', sa.String(length=255), nullable=False),
        sa.Column('year', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=255), nullable=False),
        sa.Column('total_amount', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_references_opportunity_id', 'opportunity_references', ['opportunity_id'], unique=False)

    op.create_table('opportunity_financials',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_project_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('budget_categories', postgresql.JSON(), nullable=False),
        sa.Column('contingency_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('profit_margin_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_financials_opportunity_id', 'opportunity_financials', ['opportunity_id'], unique=False)

    op.create_table('opportunity_risks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('risk_description', sa.Text(), nullable=False),
        sa.Column('impact_level', sa.String(length=50), nullable=False),
        sa.Column('probability', sa.String(length=50), nullable=False),
        sa.Column('mitigation_strategy', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_risks_opportunity_id', 'opportunity_risks', ['opportunity_id'], unique=False)

    op.create_table('opportunity_legal_checklists',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_opportunity_legal_checklists_opportunity_id', 'opportunity_legal_checklists', ['opportunity_id'], unique=False)


def downgrade():
    op.drop_table('opportunity_legal_checklists')
    op.drop_table('opportunity_risks')
    op.drop_table('opportunity_financials')
    op.drop_table('opportunity_references')
    op.drop_table('opportunity_team_members')
    op.drop_table('opportunity_delivery_models')
    op.drop_table('opportunity_strategies')
    op.drop_table('opportunity_competitors')
    op.drop_table('opportunity_drivers')
    op.drop_table('opportunity_documents')
    op.drop_table('opportunity_stakeholders')
    op.drop_table('opportunity_overviews')
