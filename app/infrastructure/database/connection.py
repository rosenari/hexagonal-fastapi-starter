"""Database connection and session management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.database.models.base import Base
from app.infrastructure.logging import get_logger


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self.logger = get_logger(self.__class__.__name__)
    
    async def connect(self) -> None:
        """Establish database connection."""
        if self.engine is not None:
            return
        
        self.logger.info(f"Connecting to database: {self.database_url}")
        
        # Create async engine
        self.engine = create_async_engine(
            self.database_url,
            echo=False,  # Set to True for SQL debugging
            future=True
        )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.logger.info("Database connection established")
    
    async def disconnect(self) -> None:
        """Close database connection."""
        if self.engine is None:
            return
        
        self.logger.info("Disconnecting from database")
        await self.engine.dispose()
        self.engine = None
        self.session_factory = None
        self.logger.info("Database connection closed")
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        if self.engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        self.logger.info("Creating database tables")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.logger.info("Database tables created")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session with automatic cleanup."""
        if self.session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
_database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _database_manager
    
    if _database_manager is None:
        from app.infrastructure.config import settings
        database_url = settings.database_url or "sqlite+aiosqlite:///./hexagonal_fastapi.db"
        _database_manager = DatabaseManager(database_url)
    
    return _database_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions in FastAPI."""
    db_manager = get_database_manager()
    async with db_manager.get_session() as session:
        yield session