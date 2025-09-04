import pytest
from unittest.mock import patch, AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from app.infrastructure.database.connection import DatabaseManager
from app.infrastructure.database.models.user import UserModel


class TestDatabaseManager:
    @pytest.fixture
    def database_url(self) -> str:
        return "sqlite+aiosqlite:///:memory:"
    
    @pytest.fixture
    def database_manager(self, database_url: str) -> DatabaseManager:
        return DatabaseManager(database_url)
    
    def test_database_manager_initialization(
        self, database_manager: DatabaseManager
    ) -> None:
        assert database_manager.database_url == "sqlite+aiosqlite:///:memory:"
        assert database_manager.engine is None
        assert database_manager.session_factory is None
    
    @pytest.mark.asyncio
    async def test_database_connection_lifecycle(
        self, database_manager: DatabaseManager
    ) -> None:
        # Test connection
        await database_manager.connect()
        
        assert database_manager.engine is not None
        assert database_manager.session_factory is not None
        
        # Test session creation
        async with database_manager.get_session() as session:
            assert isinstance(session, AsyncSession)
        
        # Test disconnection
        await database_manager.disconnect()
        
        # Engine reference should be None after disconnect
        assert database_manager.engine is None
    
    @pytest.mark.asyncio
    async def test_create_tables(self, database_manager: DatabaseManager) -> None:
        await database_manager.connect()
        
        # Should not raise any exceptions
        await database_manager.create_tables()
        
        # Verify tables exist by checking metadata
        from app.infrastructure.database.models.base import Base
        
        # Get table names from metadata
        table_names = list(Base.metadata.tables.keys())
        assert "users" in table_names
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_session_context_manager(
        self, database_manager: DatabaseManager
    ) -> None:
        await database_manager.connect()
        
        session_obj = None
        async with database_manager.get_session() as session:
            session_obj = session
            assert isinstance(session, AsyncSession)
        
        # Session should be closed after context manager
        assert session_obj is not None
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_session_rollback_on_exception(
        self, database_manager: DatabaseManager
    ) -> None:
        await database_manager.connect()
        await database_manager.create_tables()
        
        with pytest.raises(ValueError, match="Test error"):
            async with database_manager.get_session() as session:
                # Simulate some database operation
                user = UserModel(
                    email="test@example.com",
                    hashed_password="hashed_password"
                )
                session.add(user)
                await session.flush()
                
                # Raise an exception to trigger rollback
                raise ValueError("Test error")
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_database_manager_not_connected_error(
        self, database_manager: DatabaseManager
    ) -> None:
        # Should raise error when trying to get session without connecting
        with pytest.raises(RuntimeError, match="Database not connected"):
            async with database_manager.get_session() as session:
                pass
    
    @pytest.mark.asyncio
    async def test_database_manager_singleton_behavior(self) -> None:
        # Test that get_database_manager returns the same instance
        from app.infrastructure.database.connection import get_database_manager
        
        manager1 = get_database_manager()
        manager2 = get_database_manager()
        
        assert manager1 is manager2