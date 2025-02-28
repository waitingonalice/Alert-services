from functools import wraps
from typing import Callable
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from .config import settings


class SQLBase(DeclarativeBase, MappedAsDataclass):
    """
    Base model for SQLAlchemy.
    """

    pass


DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_ASYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"
async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO,  # log all queries to the logger
    future=True,  # needed for backward compatibility
    pool_size=settings.DB_POOL_SIZE,  # number of connections in the pool
    max_overflow=settings.DB_MAX_OVERFLOW,  # number of extra connections allowed
    pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,  # recycle connection after this time interval
    pool_timeout=settings.DB_POOL_TIMEOUT_SECONDS,  # timeout when waiting to get a connection from the pool
    pool_pre_ping=settings.DB_POOL_PRE_PING,  # if connection is invalid, discard it from the pool
)

async_session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


def async_transaction(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            async with session.begin():
                try:
                    called = await func(*args, **kwargs, session=session)
                    await session.commit()
                    return called
                except SQLAlchemyError as e:
                    session.rollback()
                    raise e

    return wrapper
