from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from sqlalchemy import Column, Integer, MetaData, String, Table, Index, ForeignKey

target_metadata = MetaData()

# 必须与 app/db/database.py 中的 schema 保持一致
projects_table = Table(
    "projects",
    target_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False),
    Column("genre", String, nullable=False),
    Column("source_content", String, nullable=False),
    Column("chapter_count", Integer, nullable=False, default=0),
    Column("chapters_json", String, nullable=False, default="[]"),
    Column("current_yaml", String, nullable=False),
    Column("validation_json", String, nullable=False, default='{"valid": false, "errors": []}'),
    Column("generation_mode", String, nullable=False, default="mock"),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
    Index("idx_projects_updated_at", "updated_at"),
)

Table(
    "script_versions",
    target_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
    Column("version_name", String, nullable=False),
    Column("yaml", String, nullable=False),
    Column("validation_json", String, nullable=False, default='{"valid": false, "errors": []}'),
    Column("note", String, nullable=False, default=""),
    Column("created_at", String, nullable=False),
    Index("idx_script_versions_project_id", "project_id", "created_at"),
)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
