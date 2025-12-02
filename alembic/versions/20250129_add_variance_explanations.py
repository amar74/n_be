"""add variance explanation columns to finance lines

Revision ID: variance_explanations_20250129
Revises: budget_approvals_20250128
Create Date: 2025-01-29

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "variance_explanations_20250129"
down_revision: Union[str, None] = "budget_approvals_20250128"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add variance explanation columns to finance_revenue_lines
    op.add_column('finance_revenue_lines', sa.Column('variance_explanation', sa.Text(), nullable=True))
    op.add_column('finance_revenue_lines', sa.Column('root_cause', sa.Text(), nullable=True))
    op.add_column('finance_revenue_lines', sa.Column('action_plan', sa.Text(), nullable=True))
    
    # Add variance explanation columns to finance_expense_lines
    op.add_column('finance_expense_lines', sa.Column('variance_explanation', sa.Text(), nullable=True))
    op.add_column('finance_expense_lines', sa.Column('root_cause', sa.Text(), nullable=True))
    op.add_column('finance_expense_lines', sa.Column('action_plan', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove variance explanation columns from finance_revenue_lines
    op.drop_column('finance_revenue_lines', 'action_plan')
    op.drop_column('finance_revenue_lines', 'root_cause')
    op.drop_column('finance_revenue_lines', 'variance_explanation')
    
    # Remove variance explanation columns from finance_expense_lines
    op.drop_column('finance_expense_lines', 'action_plan')
    op.drop_column('finance_expense_lines', 'root_cause')
    op.drop_column('finance_expense_lines', 'variance_explanation')

