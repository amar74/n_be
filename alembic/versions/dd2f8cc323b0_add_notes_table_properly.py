"""add notes table properly

Revision ID: dd2f8cc323b0
Revises: e0f52551bb55
Create Date: 2025-09-05 01:57:22.633256

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'dd2f8cc323b0'
down_revision: Union[str, None] = 'e0f52551bb55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('notes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('meeting_title', sa.String(length=255), nullable=False),
    sa.Column('meeting_datetime', sa.DateTime(), nullable=False),
    sa.Column('meeting_notes', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('org_id', sa.UUID(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_id'), 'notes', ['id'], unique=True)
    op.create_index(op.f('ix_notes_meeting_title'), 'notes', ['meeting_title'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notes_meeting_title'), table_name='notes')
    op.drop_index(op.f('ix_notes_id'), table_name='notes')
    op.drop_table('notes')


