import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

from app.models.cliente_model import Cliente
from app.models.proveedor_model import Proveedor
from app.models.pedido_model import Pedido
from database import Base

config = context.config

if config.config_file_name is not None:
  fileConfig(config.config_file_name)

# Load the database URL from environment variables. The app connects with the
# async asyncpg driver; migrations run over a plain sync connection, so strip
# the driver suffix here rather than complicating Alembic with async plumbing.
database_url = os.getenv("DATABASE_URL").replace("+asyncpg", "")

config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
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
