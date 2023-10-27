from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from typing import TypeVar

from icon_stats.config import config


def create_conn_str(
        user: str,
        password: str,
        server: str,
        port: str,
        database: str,
        prefix: str = "postgresql+asyncpg",
        **kwargs,
) -> str:
    return f"{prefix}://{user}:{password}@{server}:{port}/{database}"


# ASYNC_SQLALCHEMY_DATABASE_URL = create_conn_str(**config.db.stats.__dict__)
ASYNC_CONNECTION_STRING = create_conn_str(
    user="postgres",
    password="changeme",
    server="localhost",
    database="postgres",
    port="5432",
)


def create_db_connection_strings() -> dict[str, str]:
    connection_strings = {}

    for db, c in config.db.__dict__.items():
        connection_strings.update({db: create_conn_str(**c.__dict__)})

    return connection_strings


def create_session_factories() -> dict[str, async_sessionmaker]:
    output = {}

    for db_name, db_config in config.db.__dict__.items():
        connection_string = create_conn_str(**db_config.__dict__)
        engine = create_async_engine(
            connection_string,
            # connect_args={"options": f"-c search_path={db_config.schema_}"},
            echo=True,
            future=True,
        )
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        output.update({db_name: session_factory})

    return output


async def get_session_api() -> AsyncSession:
    """
    Fastapi expects a coroutine to be returned from a dependency function. `get_session`
     returns a contextmanager, so we use this instead for the api.
    """
    async with session_factories['stats']() as session:
        yield session


session_factories = create_session_factories()


@asynccontextmanager
async def get_session(db_name: str = 'stats'):
    if db_name not in session_factories:
        raise ValueError(
            f"No session factory registered for database key: {db_name}")

    async with session_factories[db_name]() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


# Generic sqlmodel table
TDbModel = TypeVar("TDbModel", bound=SQLModel)


async def upsert_model(db_name: str, model: TDbModel):
    async with get_session(db_name=db_name) as session:
        session.add(model)
        await session.commit()
