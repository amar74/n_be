"""create_opportunities_table_v2

Revision ID: 3df021b7005c
Revises: 62a366661d81
Create Date: 2025-10-14 00:56:22.479472

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3df021b7005c'
down_revision: Union[str, None] = '62a366661d81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('opportunities',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('org_id', sa.UUID(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=False),
    sa.Column('project_name', sa.String(length=500), nullable=False),
    sa.Column('client_name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('stage', sa.Enum('lead', 'qualification', 'proposal_development', 'rfp_response', 'shortlisted', 'presentation', 'negotiation', 'won', 'lost', 'on_hold', name='opportunity_stage'), nullable=False),
    sa.Column('risk_level', sa.Enum('low_risk', 'medium_risk', 'high_risk', name='risk_level'), nullable=True),
    sa.Column('project_value', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('my_role', sa.String(length=255), nullable=True),
    sa.Column('team_size', sa.Integer(), nullable=True),
    sa.Column('expected_rfp_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('market_sector', sa.String(length=255), nullable=True),
    sa.Column('match_score', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opportunities_created_by'), 'opportunities', ['created_by'], unique=False)
    op.create_index(op.f('ix_opportunities_id'), 'opportunities', ['id'], unique=False)
    op.create_index(op.f('ix_opportunities_org_id'), 'opportunities', ['org_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_opportunities_org_id'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_id'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_created_by'), table_name='opportunities')
    op.drop_table('opportunities')


