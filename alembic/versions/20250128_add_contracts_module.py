from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "contracts_module_20250128"
down_revision: Union[str, None] = "add_user_profile_picture_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_enum_names = {enum["name"] for enum in inspector.get_enums()}
    existing_tables = inspector.get_table_names()

    contract_status_enum = postgresql.ENUM(
        "awaiting-review",
        "in-legal-review",
        "exceptions-approved",
        "negotiating",
        "executed",
        "archived",
        name="contract_status",
        create_type=False,
    )
    risk_level_enum = postgresql.ENUM(
        "low",
        "medium",
        "high",
        name="contract_risk_level",
        create_type=False,
    )
    clause_risk_level_enum = postgresql.ENUM(
        "preferred",
        "acceptable",
        "fallback",
        name="clause_risk_level",
        create_type=False,
    )

    if "contract_status" not in existing_enum_names:
        contract_status_enum.create(bind, checkfirst=True)
    if "contract_risk_level" not in existing_enum_names:
        risk_level_enum.create(bind, checkfirst=True)
    if "clause_risk_level" not in existing_enum_names:
        clause_risk_level_enum.create(bind, checkfirst=True)

    if "contracts" not in existing_tables:
        op.create_table(
            "contracts",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("contract_id", sa.String(length=50), nullable=True, unique=True),
            sa.Column(
                "account_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("accounts.account_id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "opportunity_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("opportunities.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "proposal_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("proposals.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column(
                "created_by",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "assigned_reviewer",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("client_name", sa.String(length=255), nullable=False),
            sa.Column("project_name", sa.String(length=500), nullable=False),
            sa.Column("document_type", sa.String(length=255), nullable=False),
            sa.Column("version", sa.String(length=20), nullable=True),
            sa.Column("status", contract_status_enum, nullable=False),
            sa.Column("risk_level", risk_level_enum, nullable=False),
            sa.Column("contract_value", sa.Numeric(15, 2), nullable=True),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
            sa.Column("start_date", sa.Date(), nullable=True),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.Column("upload_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("execution_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_modified", sa.DateTime(timezone=True), nullable=True),
            sa.Column("file_name", sa.String(length=500), nullable=True),
            sa.Column("file_size", sa.String(length=50), nullable=True),
            sa.Column("file_url", sa.String(length=1024), nullable=True),
            sa.Column("red_clauses", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("amber_clauses", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("green_clauses", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("total_clauses", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("terms_and_conditions", sa.Text(), nullable=True),
            sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index("ix_contracts_org_id", "contracts", ["org_id"], unique=False)
        op.create_index("ix_contracts_contract_id", "contracts", ["contract_id"], unique=False)
        op.create_index("ix_contracts_account_id", "contracts", ["account_id"], unique=False)
        op.create_index("ix_contracts_opportunity_id", "contracts", ["opportunity_id"], unique=False)
        op.create_index("ix_contracts_proposal_id", "contracts", ["proposal_id"], unique=False)
        op.create_index("ix_contracts_project_id", "contracts", ["project_id"], unique=False)
        op.create_index("ix_contracts_status", "contracts", ["status"], unique=False)
        op.create_index("ix_contracts_risk_level", "contracts", ["risk_level"], unique=False)
        op.create_index("ix_contracts_created_by", "contracts", ["created_by"], unique=False)
        op.create_index("ix_contracts_assigned_reviewer", "contracts", ["assigned_reviewer"], unique=False)

    if "clause_library" not in existing_tables:
        op.create_table(
            "clause_library",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("category", sa.String(length=100), nullable=False),
            sa.Column("clause_text", sa.Text(), nullable=False),
            sa.Column("acceptable_alternatives", postgresql.ARRAY(sa.Text()), nullable=True),
            sa.Column("fallback_positions", postgresql.ARRAY(sa.Text()), nullable=True),
            sa.Column("risk_level", clause_risk_level_enum, nullable=False),
            sa.Column(
                "created_by",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index("ix_clause_library_org_id", "clause_library", ["org_id"], unique=False)
        op.create_index("ix_clause_library_category", "clause_library", ["category"], unique=False)

    if "clause_categories" not in existing_tables:
        op.create_table(
            "clause_categories",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "created_by",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index("ix_clause_categories_org_id", "clause_categories", ["org_id"], unique=False)
        op.create_index("ix_clause_categories_name", "clause_categories", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_clause_categories_name", table_name="clause_categories")
    op.drop_index("ix_clause_categories_org_id", table_name="clause_categories")
    op.drop_table("clause_categories")
    
    op.drop_index("ix_clause_library_category", table_name="clause_library")
    op.drop_index("ix_clause_library_org_id", table_name="clause_library")
    op.drop_table("clause_library")
    
    op.drop_index("ix_contracts_assigned_reviewer", table_name="contracts")
    op.drop_index("ix_contracts_created_by", table_name="contracts")
    op.drop_index("ix_contracts_risk_level", table_name="contracts")
    op.drop_index("ix_contracts_status", table_name="contracts")
    op.drop_index("ix_contracts_project_id", table_name="contracts")
    op.drop_index("ix_contracts_proposal_id", table_name="contracts")
    op.drop_index("ix_contracts_opportunity_id", table_name="contracts")
    op.drop_index("ix_contracts_account_id", table_name="contracts")
    op.drop_index("ix_contracts_contract_id", table_name="contracts")
    op.drop_index("ix_contracts_org_id", table_name="contracts")
    op.drop_table("contracts")
    
    op.execute("DROP TYPE IF EXISTS clause_risk_level")
    op.execute("DROP TYPE IF EXISTS risk_level")
    op.execute("DROP TYPE IF EXISTS contract_status")

