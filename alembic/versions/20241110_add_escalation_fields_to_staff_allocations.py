"""Add escalation fields to staff allocations

Revision ID: staff_alloc_escalation
Revises: create_staff_planning_tables
Create Date: 2025-11-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "staff_alloc_escalation"
down_revision = "create_staff_planning_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            ALTER TABLE staff_allocations
            ADD COLUMN IF NOT EXISTS initial_escalation_rate FLOAT
            """
        )
    )
    conn.execute(
        sa.text(
            """
            ALTER TABLE staff_allocations
            ADD COLUMN IF NOT EXISTS escalation_rate FLOAT
            """
        )
    )
    conn.execute(
        sa.text(
            """
            ALTER TABLE staff_allocations
            ADD COLUMN IF NOT EXISTS escalation_effective_month INTEGER
            """
        )
    )

    conn.execute(
        sa.text(
            """
            UPDATE staff_allocations sa
            SET initial_escalation_rate = COALESCE(sa.initial_escalation_rate, sp.annual_escalation_rate),
                escalation_effective_month = COALESCE(sa.escalation_effective_month, 1)
            FROM staff_plans sp
            WHERE sa.staff_plan_id = sp.id
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "ALTER TABLE staff_allocations DROP COLUMN IF EXISTS escalation_effective_month"
        )
    )
    conn.execute(
        sa.text("ALTER TABLE staff_allocations DROP COLUMN IF EXISTS escalation_rate")
    )
    conn.execute(
        sa.text(
            "ALTER TABLE staff_allocations DROP COLUMN IF EXISTS initial_escalation_rate"
        )
    )

