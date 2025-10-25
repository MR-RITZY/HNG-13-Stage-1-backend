from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from contextlib import asynccontextmanager

from src.log import info_log, error_log
from src.config import settings
from src import model

DB_URL = (
    f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)


async_engine = create_async_engine(DB_URL)

AsyncSessionMaker = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db():
    async with AsyncSessionMaker() as async_session:
        yield async_session


@asynccontextmanager
async def db_lifepan():
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(model.Base.metadata.create_all)
            info_log.info("Connected to Database")
            yield
    except Exception:
        error_log.error("Error Connecting to Database")
        raise
    finally:
        await async_engine.dispose()
        info_log.info("Disconnected from Database")
