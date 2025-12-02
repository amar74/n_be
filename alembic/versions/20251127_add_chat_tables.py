"""Add chat session and message tables

Revision ID: chat_tables_20251127
Revises: opp_ingestion_20251113
Create Date: 2025-11-27 04:09:42.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision: str = "chat_tables_20251127"
down_revision: Union[str, None] = "bce703e64563"  # Points to merge_all_heads instead
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type using DO block to check if it exists first
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chat_session_status') THEN
                    CREATE TYPE chat_session_status AS ENUM ('active', 'archived', 'deleted');
                END IF;
            END;
            $$;
            """
        )
    )

    # Create enum type object without auto-creation (we already created it above)
    chat_session_status_enum = postgresql.ENUM(
        "active",
        "archived",
        "deleted",
        name="chat_session_status",
        create_type=False,
    )

    # Check if chat_sessions table exists before creating
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create chat_sessions table
    if "chat_sessions" not in existing_tables:
        op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("template_id", sa.Integer(), nullable=True, index=True),
        sa.Column("selected_topics", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("selected_prompts", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("module", sa.String(100), nullable=True, index=True),
        sa.Column("status", chat_session_status_enum, nullable=False, default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], name="fk_chat_sessions_org_id"),
        sa.ForeignKeyConstraint(["template_id"], ["ai_agentic_templates.id"], name="fk_chat_sessions_template_id"),
        )

    # Create chat_messages table
    if "chat_messages" not in existing_tables:
        op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("thinking_mode", sa.String(20), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE", name="fk_chat_messages_session_id"),
        )


def downgrade() -> None:
    # Drop tables
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    
    # Drop enum type
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chat_session_status') THEN
                    DROP TYPE chat_session_status;
                END IF;
            END;
            $$;
            """
        )
    )

