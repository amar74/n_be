"""add proposals module tables

Revision ID: proposals_module_20251112
Revises: add_delivery_model_templates
Create Date: 2025-11-12

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "proposals_module_20251112"
down_revision: Union[str, None] = "add_delivery_model_templates"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_enum_names = {enum["name"] for enum in inspector.get_enums()}

    proposal_status_enum = postgresql.ENUM(
        "draft",
        "in_review",
        "approved",
        "submitted",
        "won",
        "lost",
        "archived",
        name="proposal_status",
        create_type=False,
    )
    proposal_source_enum = postgresql.ENUM("opportunity", "manual", name="proposal_source", create_type=False)
    proposal_section_status_enum = postgresql.ENUM(
        "draft", "in_review", "approved", name="proposal_section_status", create_type=False
    )
    proposal_document_category_enum = postgresql.ENUM(
        "rfp",
        "boq",
        "schedule",
        "technical",
        "commercial",
        "attachment",
        "generated",
        name="proposal_document_category",
        create_type=False,
    )
    proposal_approval_status_enum = postgresql.ENUM(
        "pending",
        "approved",
        "rejected",
        "skipped",
        name="proposal_approval_status",
        create_type=False,
    )

    if "proposal_status" not in existing_enum_names:
        proposal_status_enum.create(bind, checkfirst=True)
    if "proposal_source" not in existing_enum_names:
        proposal_source_enum.create(bind, checkfirst=True)
    if "proposal_section_status" not in existing_enum_names:
        proposal_section_status_enum.create(bind, checkfirst=True)
    if "proposal_document_category" not in existing_enum_names:
        proposal_document_category_enum.create(bind, checkfirst=True)
    if "proposal_approval_status" not in existing_enum_names:
        proposal_approval_status_enum.create(bind, checkfirst=True)

    if not inspector.has_table("proposals"):
        op.create_table(
            "proposals",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            sa.Column(
                "opportunity_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("opportunities.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "account_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("accounts.account_id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_by",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "owner_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("proposal_number", sa.String(length=50), nullable=False, unique=True),
            sa.Column("title", sa.String(length=500), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("status", proposal_status_enum, nullable=False, server_default="draft"),
            sa.Column("source", proposal_source_enum, nullable=False, server_default="opportunity"),
            sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("total_value", sa.Numeric(15, 2), nullable=True),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
            sa.Column("estimated_cost", sa.Numeric(15, 2), nullable=True),
            sa.Column("expected_margin", sa.Numeric(5, 2), nullable=True),
            sa.Column("fee_structure", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("submission_date", sa.Date(), nullable=True),
            sa.Column("client_response_date", sa.Date(), nullable=True),
            sa.Column("won_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("lost_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("ai_assistance_summary", sa.Text(), nullable=True),
            sa.Column("ai_content_percentage", sa.Integer(), nullable=True),
            sa.Column("ai_last_run_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("ai_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("finance_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("resource_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("client_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("approval_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("converted_to_project", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("conversion_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("tags", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index("ix_proposals_org_id", "proposals", ["org_id"], unique=False)
        op.create_index("ix_proposals_opportunity_id", "proposals", ["opportunity_id"], unique=False)
        op.create_index("ix_proposals_account_id", "proposals", ["account_id"], unique=False)
        op.create_index("ix_proposals_created_by", "proposals", ["created_by"], unique=False)
        op.create_index("ix_proposals_owner_id", "proposals", ["owner_id"], unique=False)

    if not inspector.has_table("proposal_sections"):
        op.create_table(
            "proposal_sections",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("proposal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False),
            sa.Column("section_type", sa.String(length=100), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("status", proposal_section_status_enum, nullable=False, server_default="draft"),
            sa.Column("page_count", sa.Integer(), nullable=True),
            sa.Column("ai_generated_percentage", sa.Integer(), nullable=True),
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("display_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index("ix_proposal_sections_proposal_id", "proposal_sections", ["proposal_id"], unique=False)
        op.create_index("ix_proposal_sections_section_type", "proposal_sections", ["section_type"], unique=False)

    if not inspector.has_table("proposal_documents"):
        op.create_table(
            "proposal_documents",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("proposal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("file_path", sa.String(length=1024), nullable=True),
            sa.Column("external_url", sa.String(length=1024), nullable=True),
            sa.Column("category", proposal_document_category_enum, nullable=False, server_default="attachment"),
            sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        )
        op.create_index("ix_proposal_documents_proposal_id", "proposal_documents", ["proposal_id"], unique=False)
        op.create_index("ix_proposal_documents_category", "proposal_documents", ["category"], unique=False)
        op.create_index("ix_proposal_documents_uploaded_by", "proposal_documents", ["uploaded_by"], unique=False)

    if not inspector.has_table("proposal_approvals"):
        op.create_table(
            "proposal_approvals",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("proposal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False),
            sa.Column("stage_name", sa.String(length=100), nullable=False),
            sa.Column("required_role", sa.String(length=100), nullable=True),
            sa.Column("sequence", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("status", proposal_approval_status_enum, nullable=False, server_default="pending"),
            sa.Column("approver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("decision_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("comments", sa.Text(), nullable=True),
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index("ix_proposal_approvals_proposal_id", "proposal_approvals", ["proposal_id"], unique=False)
        op.create_index("ix_proposal_approvals_sequence", "proposal_approvals", ["sequence"], unique=False)
        op.create_index("ix_proposal_approvals_approver_id", "proposal_approvals", ["approver_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_proposal_approvals_approver_id", table_name="proposal_approvals")
    op.drop_index("ix_proposal_approvals_sequence", table_name="proposal_approvals")
    op.drop_index("ix_proposal_approvals_proposal_id", table_name="proposal_approvals")
    op.drop_table("proposal_approvals")

    op.drop_index("ix_proposal_documents_uploaded_by", table_name="proposal_documents")
    op.drop_index("ix_proposal_documents_category", table_name="proposal_documents")
    op.drop_index("ix_proposal_documents_proposal_id", table_name="proposal_documents")
    op.drop_table("proposal_documents")

    op.drop_index("ix_proposal_sections_section_type", table_name="proposal_sections")
    op.drop_index("ix_proposal_sections_proposal_id", table_name="proposal_sections")
    op.drop_table("proposal_sections")

    op.drop_index("ix_proposals_owner_id", table_name="proposals")
    op.drop_index("ix_proposals_created_by", table_name="proposals")
    op.drop_index("ix_proposals_account_id", table_name="proposals")
    op.drop_index("ix_proposals_opportunity_id", table_name="proposals")
    op.drop_index("ix_proposals_org_id", table_name="proposals")
    op.drop_table("proposals")

    op.execute("DROP TYPE IF EXISTS proposal_approval_status")
    op.execute("DROP TYPE IF EXISTS proposal_document_category")
    op.execute("DROP TYPE IF EXISTS proposal_section_status")
    op.execute("DROP TYPE IF EXISTS proposal_source")
    op.execute("DROP TYPE IF EXISTS proposal_status")
