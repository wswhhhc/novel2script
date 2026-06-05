import sqlite3
from collections.abc import Iterator

from app.config.settings import settings


def get_connection() -> sqlite3.Connection:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def iter_connection() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def init_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
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
            );

            CREATE TABLE IF NOT EXISTS script_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                version_name TEXT NOT NULL,
                yaml TEXT NOT NULL,
                validation_json TEXT NOT NULL DEFAULT '{"valid": false, "errors": []}',
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_script_versions_project_id ON script_versions(project_id, created_at DESC);
            """
        )
