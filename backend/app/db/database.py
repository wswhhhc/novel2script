import sqlite3
from collections.abc import Iterator
from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

from app.config.settings import settings


def _get_alembic_config() -> AlembicConfig:
    """获取 Alembic 配置对象，指向 backend/alembic.ini。"""
    # __file__ = backend/app/db/database.py → 向上 2 级到 backend/
    backend_root = Path(__file__).resolve().parents[2]
    alembic_ini = backend_root / "alembic.ini"
    alembic_cfg = AlembicConfig(str(alembic_ini))
    # 使用 settings 中的数据库路径覆盖 alembic.ini 中的 URL
    db_url = f"sqlite:///{settings.database_path.resolve()}"
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    return alembic_cfg


def run_migrations() -> None:
    """启动时自动执行待处理的数据库迁移。"""
    alembic_cfg = _get_alembic_config()
    alembic_command.upgrade(alembic_cfg, "head")


def init_database() -> None:
    """初始化数据库：创建目录并执行迁移。"""
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    run_migrations()


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
