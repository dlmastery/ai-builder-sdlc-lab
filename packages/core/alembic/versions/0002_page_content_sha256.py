"""pages.content_sha256 — the hash of the normalised page, so a re-export or re-scan of a page
already in the tenant is named as such in the queue (customer test, 2026-09-06, broken 6)

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-06 18:55:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pages", sa.Column("content_sha256", sa.String(length=64), nullable=True))
    op.create_index(
        "ix_pages_tenant_content", "pages", ["tenant_id", "content_sha256"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_pages_tenant_content", table_name="pages")
    op.drop_column("pages", "content_sha256")
