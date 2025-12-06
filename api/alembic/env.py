from __future__ import annotations

import os
from logging.config import fileConfig
import sys
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

# ------------ Load .env and configure DB URL ------------

# Path to your project root (where .env lives)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # this points one level above /alembic
sys.path.append(BASE_DIR)
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_SYNC_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set for Alembic")

# This is the Alembic Config object
config = context.config

# Override sqlalchemy.url in alembic.ini with the env var
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# ------------ Logging setup ------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------ Import models' metadata ------------

from db.base import Base  
from db import base_models  # noqa: F401  # imports User, etc.

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
