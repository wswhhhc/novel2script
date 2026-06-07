"""base schema — 创建 projects 和 script_versions 表

Revision ID: 41ea2bd54fe7
Revises:
Create Date: 2026-06-07 11:12:02.952955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "41ea2bd54fe7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            source_content TEXT NOT NULL,
            chapter_count INTEGER NOT NULL DEFAULT 0,
            chapters_json TEXT NOT NULL DEFAULT '[]',
            current_yaml TEXT NOT NULL,
            validation_json TEXT NOT NULL DEFAULT '{"valid": false, "errors": []}',
            generation_mode TEXT NOT NULL DEFAULT 'mock',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS script_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            version_name TEXT NOT NULL,
            yaml TEXT NOT NULL,
            validation_json TEXT NOT NULL DEFAULT '{"valid": false, "errors": []}',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_script_versions_project_id "
        "ON script_versions(project_id, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS script_versions")
    op.execute("DROP TABLE IF EXISTS projects")
