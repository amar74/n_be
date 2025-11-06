"""add employee survey types to enum

Revision ID: survey_002
Revises: survey_001
Create Date: 2025-11-06 18:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'survey_002'
down_revision = 'survey_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add employee_feedback and employee_satisfaction to surveytype enum
    # PostgreSQL doesn't support IF NOT EXISTS for ALTER TYPE ADD VALUE
    # So we use a DO block to check first
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'employee_feedback' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'surveytype')
            ) THEN
                ALTER TYPE surveytype ADD VALUE 'employee_feedback';
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'employee_satisfaction' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'surveytype')
            ) THEN
                ALTER TYPE surveytype ADD VALUE 'employee_satisfaction';
            END IF;
        END $$;
    """)


def downgrade():
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type, which is complex
    # For now, we'll leave a comment that manual intervention is needed
    pass
    # To manually remove enum values:
    # 1. Create new enum without the values
    # 2. Alter table to use new enum
    # 3. Drop old enum
    # This is complex and risky, so we skip it in downgrade

