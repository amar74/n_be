"""add accounts full-text search indexes and extensions

Revision ID: da12f3a1f7b8
Revises: e11c426a9f1d
Create Date: 2025-09-12 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = 'da12f3a1f7b8'
down_revision: Union[str, None] = 'e11c426a9f1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable useful extensions (no-op if already present)
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Create a text search configuration that applies unaccent before stemming
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_catalog.pg_ts_config WHERE cfgname = 'english_unaccent'
          ) THEN
            CREATE TEXT SEARCH CONFIGURATION public.english_unaccent ( COPY = pg_catalog.english );
            ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
              ALTER MAPPING FOR hword, hword_part, word WITH unaccent, english_stem;
          END IF;
        END$$;
        """
    )

    # Per-field FTS GIN indexes using english_unaccent
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_accounts_name_fts ON accounts USING gin (to_tsvector('public.english_unaccent', coalesce(client_name,'')))"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_accounts_website_fts ON accounts USING gin (to_tsvector('public.english_unaccent', coalesce(company_website,'')))"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_contacts_email_fts ON contacts USING gin (to_tsvector('public.english_unaccent', coalesce(email,'')))"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_address_line1_fts ON address USING gin (to_tsvector('public.english_unaccent', coalesce(line1,'')))"
    )


def downgrade() -> None:
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS ix_accounts_name_fts")
    op.execute("DROP INDEX IF EXISTS ix_accounts_website_fts")
    op.execute("DROP INDEX IF EXISTS ix_contacts_email_fts")
    op.execute("DROP INDEX IF EXISTS ix_address_line1_fts")

    # Drop the custom text search configuration
    op.execute("DROP TEXT SEARCH CONFIGURATION IF EXISTS public.english_unaccent")

    # Optionally drop extensions (safe if unused). Comment out if you prefer to keep them.
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS unaccent")


