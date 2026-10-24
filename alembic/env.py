from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from backend.core.config import settings
from backend.storage.database import Base

# Import all models so SQLAlchemy registers every table
# with Base.metadata before Alembic compares the schema.
from backend.storage import models  # noqa: F401


# ============================================================
# ALEMBIC CONFIGURATION
# ============================================================

config = context.config


# Configure Python logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata used by Alembic autogenerate.
target_metadata = Base.metadata


# Use the same database URL as the application.
database_url = settings.database_url


# ============================================================
# OFFLINE MIGRATIONS
# ============================================================

def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    """

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# ONLINE MIGRATIONS
# ============================================================

def run_migrations_online() -> None:
    """
    Run migrations using a live database connection.
    """

    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    # Use the application's database configuration
    # instead of relying on the placeholder URL in alembic.ini.
    configuration["sqlalchemy.url"] = database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================
# ENTRY POINT
# ============================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()