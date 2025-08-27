"""fix contact table name

Revision ID: 96a826ae5ed5
Revises: e7a38d7ff1cd
Create Date: 2025-08-26 14:22:34.178958

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '96a826ae5ed5'
down_revision: Union[str, None] = 'e7a38d7ff1cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.rename_table('contact', 'contacts')


def downgrade() -> None:
    op.rename_table('contacts', 'contact')

