"""add workspace column to projects for multi-tenant isolation

Revision ID: 2e8f4a1c3b6d
Revises: 41ea2bd54fe7
Create Date: 2026-06-07 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "2e8f4a1c3b6d"
down_revision: Union[str, Sequence[str], None] = "41ea2bd54fe7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE projects
        ADD COLUMN workspace TEXT NOT NULL DEFAULT 'default'
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_projects_workspace ON projects(workspace)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_projects_ws_updated "
        "ON projects(workspace, updated_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_projects_ws_updated")
    op.execute("DROP INDEX IF EXISTS idx_projects_workspace")
    # SQLite does not support DROP COLUMN; ignore for rollback simplicity
