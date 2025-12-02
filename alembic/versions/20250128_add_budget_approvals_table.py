"""add budget approvals table

Revision ID: budget_approvals_20250128
Revises: f69e129dbc00
Create Date: 2025-01-28

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "budget_approvals_20250128"
down_revision: Union[str, None] = "f69e129dbc00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_enum_names = {enum["name"] for enum in inspector.get_enums()}
    existing_tables = inspector.get_table_names()

    # Create budget_approval_status enum if it doesn't exist
    budget_approval_status_enum = postgresql.ENUM(
        "pending",
        "approved",
        "rejected",
        "requested_changes",
        "not_started",
        name="budget_approval_status",
        create_type=False,
    )

    if "budget_approval_status" not in existing_enum_names:
        budget_approval_status_enum.create(bind, checkfirst=True)

    # Create budget_approvals table if it doesn't exist
    if "budget_approvals" not in existing_tables:
        op.create_table(
            "budget_approvals",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("budget_id", sa.Integer(), nullable=False),
            sa.Column("stage_id", sa.String(length=50), nullable=False),
            sa.Column("stage_name", sa.String(length=100), nullable=False),
            sa.Column("required_role", sa.String(length=100), nullable=True),
            sa.Column("sequence", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("status", budget_approval_status_enum, nullable=False, server_default="not_started"),
            sa.Column("approver_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("decision_at", sa.TIMESTAMP(), nullable=True),
            sa.Column("comments", sa.Text(), nullable=True),
            sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["budget_id"], ["finance_annual_budgets.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["approver_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

        # Create indexes
        op.create_index("ix_budget_approvals_budget_id", "budget_approvals", ["budget_id"], unique=False)
        op.create_index("ix_budget_approvals_approver_id", "budget_approvals", ["approver_id"], unique=False)
        op.create_index("ix_budget_approvals_stage_id", "budget_approvals", ["stage_id"], unique=False)
        op.create_index("ix_budget_approvals_sequence", "budget_approvals", ["sequence"], unique=False)


def downgrade() -> None:
    # Drop table and enum
    op.drop_index("ix_budget_approvals_sequence", table_name="budget_approvals", if_exists=True)
    op.drop_index("ix_budget_approvals_stage_id", table_name="budget_approvals", if_exists=True)
    op.drop_index("ix_budget_approvals_approver_id", table_name="budget_approvals", if_exists=True)
    op.drop_index("ix_budget_approvals_budget_id", table_name="budget_approvals", if_exists=True)
    op.drop_table("budget_approvals", if_exists=True)
    
    # Note: We don't drop the enum as it might be used elsewhere or cause issues
    # If needed, manually drop: DROP TYPE IF EXISTS budget_approval_status;

