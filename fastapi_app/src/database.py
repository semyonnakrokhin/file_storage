from contextlib import AbstractContextManager, contextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Database:
    """Database class for managing asynchronous database operations using
    SQLAlchemy."""

    def __init__(self, db_url: str) -> None:
        """Initializes the Database instance with the provided database URL."""
        self._async_engine = create_async_engine(db_url)
        self._async_session_factory = async_sessionmaker(
            bind=self._async_engine, autoflush=False, expire_on_commit=False
        )

    async def delete_and_create_database(self) -> None:
        """Firstly delete and then create database tables based on SQLAlchemy
        Base metadata."""
        async with self._async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @property
    def get_session_factory(self):
        """Getter for the asynchronous session factory."""
        return self._async_session_factory

    @contextmanager
    def session_cm(self) -> AbstractContextManager[AsyncSession]:
        """Context manager for handling database sessions."""
        session: AsyncSession = self._async_session_factory()
        try:
            yield session
        except Exception:
            # logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
