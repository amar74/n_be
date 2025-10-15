"""rename user_roles table to user_permissions

Revision ID: c5d2c5061ca1
Revises: 090f6d18782e
Create Date: 2025-09-04 14:22:35.337088

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c5d2c5061ca1'
down_revision: Union[str, None] = '090f6d18782e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('user_roles', 'user_permissions')
    
    op.execute('ALTER INDEX ix_user_roles_userid RENAME TO ix_user_permissions_userid')


def downgrade() -> None:
    op.execute('ALTER INDEX ix_user_permissions_userid RENAME TO ix_user_roles_userid')
    
    op.rename_table('user_permissions', 'user_roles')


