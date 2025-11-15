"""add delivery model templates

Revision ID: add_delivery_model_templates
Revises: add_timestamps_contacts
Create Date: 2025-11-11

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'add_delivery_model_templates'
down_revision: Union[str, None] = 'add_timestamps_contacts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table('delivery_model_templates'):
        op.create_table(
            'delivery_model_templates',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('approach', sa.Text(), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('phases', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='delivery_model_templates_created_by_fkey', ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], name='delivery_model_templates_org_id_fkey', ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id', name='delivery_model_templates_pkey')
        )
        op.create_index('ix_delivery_model_templates_org_id', 'delivery_model_templates', ['org_id'], unique=False)
        op.create_index('ix_delivery_model_templates_created_by', 'delivery_model_templates', ['created_by'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table('delivery_model_templates'):
        op.drop_index('ix_delivery_model_templates_created_by', table_name='delivery_model_templates')
        op.drop_index('ix_delivery_model_templates_org_id', table_name='delivery_model_templates')
        op.drop_table('delivery_model_templates')

