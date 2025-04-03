import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.future import Connection

from src.core.db.declaration import meta
from src.core.db.utils import import_db_all_models
from src.core.settings import settings

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


import_db_all_models()
target_metadata = meta


async def run_migrations_offline() -> None:
    context.configure(
        url=str(settings.async_db_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection, target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(str(settings.async_db_url))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


loop = asyncio.get_event_loop()
if context.is_offline_mode():
    task = run_migrations_offline()
else:
    task = run_migrations_online()

loop.run_until_complete(task)
