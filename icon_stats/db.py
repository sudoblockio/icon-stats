from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine

from icon_stats.config import config

SQLALCHEMY_DATABASE_URL_STUB = "://{user}:{password}@{server}:{port}/{db}".format(
    user=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
    server=config.POSTGRES_SERVER,
    port=config.POSTGRES_PORT,
    db=config.POSTGRES_DATABASE,
)

ASYNC_SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg" + SQLALCHEMY_DATABASE_URL_STUB
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2" + SQLALCHEMY_DATABASE_URL_STUB

logger.info(f"Connecting to server: {config.POSTGRES_SERVER} and {config.POSTGRES_DATABASE}")

async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL, echo=True, future=True)


# Run onetime if we want to init with a prebuilt table of attributes
async def init_db():
    async with async_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_factory = sessionmaker(bind=engine)
