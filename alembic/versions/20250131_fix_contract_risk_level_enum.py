"""fix_contract_risk_level_enum

Revision ID: fix_contract_risk_level_20250131
Revises: contracts_module_20250128
Create Date: 2025-01-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "fix_contract_risk_level_20250131"
down_revision: Union[str, None] = "8a42655a3477"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Fix the contracts.risk_level column to use contract_risk_level enum instead of risk_level enum.
    This migration handles the case where the column was created with the wrong enum type.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_enum_names = {enum["name"] for enum in inspector.get_enums()}
    
    # Step 1: Ensure contract_risk_level enum exists
    if "contract_risk_level" not in existing_enum_names:
        op.execute("""
            CREATE TYPE contract_risk_level AS ENUM ('low', 'medium', 'high')
        """)
        print("Created contract_risk_level enum")
    
    # Step 2: Check current enum type of contracts.risk_level column
    result = bind.execute(sa.text("""
        SELECT column_name, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'contracts' AND column_name = 'risk_level'
    """))
    col_info = result.fetchone() if result.rowcount > 0 else None
    
    if col_info:
        current_enum = col_info[1]
        print(f"Current enum type for contracts.risk_level: {current_enum}")
        
        if current_enum != 'contract_risk_level':
            # Step 3: Convert the column to use contract_risk_level enum
            # This handles conversion from both risk_level enum (low_risk, medium_risk, high_risk)
            # and direct string values (low, medium, high)
            op.execute("""
                ALTER TABLE contracts 
                ALTER COLUMN risk_level TYPE contract_risk_level 
                USING CASE 
                    WHEN risk_level::text = 'low_risk' THEN 'low'::contract_risk_level
                    WHEN risk_level::text = 'medium_risk' THEN 'medium'::contract_risk_level
                    WHEN risk_level::text = 'high_risk' THEN 'high'::contract_risk_level
                    WHEN risk_level::text = 'low' THEN 'low'::contract_risk_level
                    WHEN risk_level::text = 'medium' THEN 'medium'::contract_risk_level
                    WHEN risk_level::text = 'high' THEN 'high'::contract_risk_level
                    ELSE 'medium'::contract_risk_level
                END
            """)
            
            print("Updated contracts.risk_level to use contract_risk_level enum")
        else:
            print("contracts.risk_level already uses contract_risk_level enum")
    else:
        print("contracts table or risk_level column not found")


def downgrade() -> None:
    """
    Revert the risk_level column back to using risk_level enum (if needed).
    Note: This is a destructive operation and may not be fully reversible.
    """
    # This downgrade is complex and may not be needed
    # For now, we'll leave it as a placeholder
    pass

