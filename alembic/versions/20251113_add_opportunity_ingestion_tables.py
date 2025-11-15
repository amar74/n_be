"""Add opportunity ingestion tables and enums

Revision ID: opp_ingestion_20251113
Revises: proposals_module_20251112
Create Date: 2025-11-13 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "opp_ingestion_20251113"
down_revision: Union[str, None] = "proposals_module_20251112"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OP_SOURCE_FREQUENCY = sa.Enum(
    "daily",
    "weekly",
    "monthly",
    "manual",
    name="opportunity_source_frequency",
    create_type=False,
)
OP_SOURCE_STATUS = sa.Enum(
    "active",
    "paused",
    "archived",
    name="opportunity_source_status",
    create_type=False,
)
SCRAPE_STATUS = sa.Enum(
    "queued",
    "running",
    "success",
    "error",
    "skipped",
    name="opportunity_scrape_status",
    create_type=False,
)
TEMP_STATUS = sa.Enum(
    "pending_review",
    "approved",
    "rejected",
    "promoted",
    name="temp_opportunity_status",
    create_type=False,
)
AGENT_FREQUENCY = sa.Enum(
    "12h",
    "24h",
    "72h",
    "168h",
    name="opportunity_agent_frequency",
    create_type=False,
)
AGENT_STATUS = sa.Enum(
    "active",
    "paused",
    "disabled",
    name="opportunity_agent_status",
    create_type=False,
)
AGENT_RUN_STATUS = sa.Enum(
    "running",
    "succeeded",
    "failed",
    name="opportunity_agent_run_status",
    create_type=False,
)


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    def ensure_enum(name: str, values: list[str]) -> None:
        formatted_values = ", ".join(f"'{value}'" for value in values)
        op.execute(
            sa.text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{name}') THEN
                        CREATE TYPE {name} AS ENUM ({formatted_values});
                    END IF;
                END;
                $$;
                """
            )
        )

    ensure_enum("opportunity_source_frequency", ["daily", "weekly", "monthly", "manual"])
    ensure_enum("opportunity_source_status", ["active", "paused", "archived"])
    ensure_enum("opportunity_scrape_status", ["queued", "running", "success", "error", "skipped"])
    ensure_enum("temp_opportunity_status", ["pending_review", "approved", "rejected", "promoted"])
    ensure_enum("opportunity_agent_frequency", ["12h", "24h", "72h", "168h"])
    ensure_enum("opportunity_agent_status", ["active", "paused", "disabled"])
    ensure_enum("opportunity_agent_run_status", ["running", "succeeded", "failed"])

    if not inspector.has_table("opportunity_sources"):
        op.execute(
            """
            CREATE TABLE opportunity_sources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                url TEXT NOT NULL,
                category VARCHAR(255),
                frequency opportunity_source_frequency NOT NULL DEFAULT 'weekly',
                status opportunity_source_status NOT NULL DEFAULT 'active',
                tags JSONB,
                notes TEXT,
                last_run_at TIMESTAMPTZ,
                next_run_at TIMESTAMPTZ,
                last_success_at TIMESTAMPTZ,
                is_auto_discovery_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS ix_opportunity_sources_created_by ON opportunity_sources(created_by);
            CREATE INDEX IF NOT EXISTS ix_opportunity_sources_org_id ON opportunity_sources(org_id);
            """
        )

    if not inspector.has_table("opportunity_agents"):
        op.execute(
            """
            CREATE TABLE opportunity_agents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                source_id UUID REFERENCES opportunity_sources(id) ON DELETE SET NULL,
                created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                prompt TEXT NOT NULL,
                base_url TEXT NOT NULL,
                frequency opportunity_agent_frequency NOT NULL DEFAULT '24h',
                status opportunity_agent_status NOT NULL DEFAULT 'active',
                last_run_at TIMESTAMPTZ,
                next_run_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS ix_opportunity_agents_created_by ON opportunity_agents(created_by);
            CREATE INDEX IF NOT EXISTS ix_opportunity_agents_org_id ON opportunity_agents(org_id);
            CREATE INDEX IF NOT EXISTS ix_opportunity_agents_source_id ON opportunity_agents(source_id);
            """
        )

    if not inspector.has_table("opportunity_scrape_history"):
        op.execute(
            """
            CREATE TABLE opportunity_scrape_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                source_id UUID NOT NULL REFERENCES opportunity_sources(id) ON DELETE CASCADE,
                agent_id UUID REFERENCES opportunity_agents(id) ON DELETE SET NULL,
                url TEXT NOT NULL,
                url_hash VARCHAR(64) NOT NULL,
                status opportunity_scrape_status NOT NULL DEFAULT 'queued',
                error_message TEXT,
                raw_content TEXT,
                extracted_data JSONB,
                ai_summary TEXT,
                metadata JSONB,
                scraped_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                completed_at TIMESTAMPTZ
            );
            CREATE INDEX IF NOT EXISTS ix_opportunity_scrape_history_agent_id ON opportunity_scrape_history(agent_id);
            CREATE INDEX IF NOT EXISTS ix_opportunity_scrape_history_org_id ON opportunity_scrape_history(org_id);
            CREATE INDEX IF NOT EXISTS ix_opportunity_scrape_history_source_id ON opportunity_scrape_history(source_id);
            CREATE INDEX IF NOT EXISTS ix_opportunity_scrape_history_url_hash ON opportunity_scrape_history(url_hash);
            """
        )

    if not inspector.has_table("opportunity_agent_runs"):
        op.execute(
            """
            CREATE TABLE opportunity_agent_runs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL REFERENCES opportunity_agents(id) ON DELETE CASCADE,
                org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                status opportunity_agent_run_status NOT NULL DEFAULT 'running',
                started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                finished_at TIMESTAMPTZ,
                new_opportunities INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                metadata JSONB
            );
            CREATE INDEX IF NOT EXISTS ix_opportunity_agent_runs_agent_id ON opportunity_agent_runs(agent_id);
            CREATE INDEX IF NOT EXISTS ix_opportunity_agent_runs_org_id ON opportunity_agent_runs(org_id);
            """
        )

    if not inspector.has_table("opportunities_temp"):
        op.execute(
            """
            CREATE TABLE opportunities_temp (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                source_id UUID REFERENCES opportunity_sources(id) ON DELETE SET NULL,
                history_id UUID REFERENCES opportunity_scrape_history(id) ON DELETE SET NULL,
                reviewer_id UUID REFERENCES users(id) ON DELETE SET NULL,
                temp_identifier VARCHAR(64) UNIQUE NOT NULL,
                project_title VARCHAR(500) NOT NULL,
                client_name VARCHAR(255),
                location VARCHAR(255),
                budget_text VARCHAR(255),
                deadline TIMESTAMPTZ,
                documents JSONB,
                tags JSONB,
                ai_summary TEXT,
                ai_metadata JSONB,
                raw_payload JSONB NOT NULL,
                match_score INTEGER,
                risk_score INTEGER,
                strategic_fit_score INTEGER,
                status temp_opportunity_status NOT NULL DEFAULT 'pending_review',
                reviewer_notes TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS ix_opportunities_temp_org_id ON opportunities_temp(org_id);
            CREATE INDEX IF NOT EXISTS ix_opportunities_temp_source_id ON opportunities_temp(source_id);
            CREATE INDEX IF NOT EXISTS ix_opportunities_temp_history_id ON opportunities_temp(history_id);
            CREATE INDEX IF NOT EXISTS ix_opportunities_temp_reviewer_id ON opportunities_temp(reviewer_id);
            """
        )


def downgrade() -> None:
    conn = op.get_bind()

    op.drop_index(op.f("uq_opportunities_temp_temp_identifier"), table_name="opportunities_temp")
    op.drop_index(op.f("ix_opportunities_temp_reviewer_id"), table_name="opportunities_temp")
    op.drop_index(op.f("ix_opportunities_temp_history_id"), table_name="opportunities_temp")
    op.drop_index(op.f("ix_opportunities_temp_source_id"), table_name="opportunities_temp")
    op.drop_index(op.f("ix_opportunities_temp_org_id"), table_name="opportunities_temp")
    op.drop_table("opportunities_temp")

    op.drop_index(op.f("ix_opportunity_agent_runs_org_id"), table_name="opportunity_agent_runs")
    op.drop_index(op.f("ix_opportunity_agent_runs_agent_id"), table_name="opportunity_agent_runs")
    op.drop_table("opportunity_agent_runs")

    op.drop_index(op.f("ix_opportunity_scrape_history_url_hash"), table_name="opportunity_scrape_history")
    op.drop_index(op.f("ix_opportunity_scrape_history_source_id"), table_name="opportunity_scrape_history")
    op.drop_index(op.f("ix_opportunity_scrape_history_org_id"), table_name="opportunity_scrape_history")
    op.drop_index(op.f("ix_opportunity_scrape_history_agent_id"), table_name="opportunity_scrape_history")
    op.drop_table("opportunity_scrape_history")

    op.drop_index(op.f("ix_opportunity_agents_source_id"), table_name="opportunity_agents")
    op.drop_index(op.f("ix_opportunity_agents_org_id"), table_name="opportunity_agents")
    op.drop_index(op.f("ix_opportunity_agents_created_by"), table_name="opportunity_agents")
    op.drop_table("opportunity_agents")

    op.drop_index(op.f("ix_opportunity_sources_org_id"), table_name="opportunity_sources")
    op.drop_index(op.f("ix_opportunity_sources_created_by"), table_name="opportunity_sources")
    op.drop_table("opportunity_sources")

    for enum_type in [
        AGENT_RUN_STATUS,
        AGENT_STATUS,
        AGENT_FREQUENCY,
        TEMP_STATUS,
        SCRAPE_STATUS,
        OP_SOURCE_STATUS,
        OP_SOURCE_FREQUENCY,
    ]:
        enum_type.drop(conn, checkfirst=True)

