import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel, create_engine, text

from alembic import context

from icon_stats.db import ASYNC_CONNECTION_STRING

# Imports
from icon_stats.models.cmc_cryptocurrency_quotes_latest import \
    CmcListingsLatestQuote  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", ASYNC_CONNECTION_STRING)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in ["stats"]
    else:
        return True


def do_run_migrations(connection):
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table='alembic_version',
        version_table_schema="stats",
        include_schemas=True,
        include_name=include_name,
    )

    # Make sure the schema exists
    connection.execute(text('CREATE SCHEMA IF NOT EXISTS stats'))

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = AsyncEngine(
        create_engine(
            ASYNC_CONNECTION_STRING,
            echo=True,
            future=True,
        ))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


asyncio.run(run_migrations_online())
