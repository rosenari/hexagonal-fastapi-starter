import pytest
from uuid import uuid4

from app.domain.entities.user import User
from app.domain.value_objects import Email
from app.infrastructure.database.connection import DatabaseManager
from app.infrastructure.database.repositories.user_repository import UserRepository


class TestUserRepository:
    @pytest.fixture
    async def database_manager(self) -> DatabaseManager:
        db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
        await db_manager.connect()
        await db_manager.create_tables()
        return db_manager
    
    @pytest.fixture
    async def user_repository(self, database_manager: DatabaseManager) -> UserRepository:
        return UserRepository(database_manager)
    
    @pytest.mark.asyncio
    async def test_save_user(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Arrange
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        # Act
        async with database_manager.get_session() as session:
            saved_user = await user_repository.save(user, session)
        
        # Assert
        assert saved_user.id == user.id
        assert saved_user.email == user.email
        assert saved_user.hashed_password == user.hashed_password
        assert saved_user.is_active == user.is_active
        assert saved_user.created_at is not None
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_find_by_id_existing_user(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Arrange
        user_id = uuid4()
        user = User(
            id=user_id,
            email="findme@example.com",
            hashed_password="hashed_password_123"
        )
        
        # Save user first
        async with database_manager.get_session() as session:
            await user_repository.save(user, session)
        
        # Act
        async with database_manager.get_session() as session:
            found_user = await user_repository.find_by_id(user_id, session)
        
        # Assert
        assert found_user is not None
        assert found_user.id == user_id
        assert found_user.email == "findme@example.com"
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_find_by_id_non_existing_user(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Act
        async with database_manager.get_session() as session:
            found_user = await user_repository.find_by_id(uuid4(), session)
        
        # Assert
        assert found_user is None
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_find_by_email_existing_user(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Arrange
        email = Email("unique@example.com")
        user = User(
            id=uuid4(),
            email=email.value,
            hashed_password="hashed_password_123"
        )
        
        # Save user first
        async with database_manager.get_session() as session:
            await user_repository.save(user, session)
        
        # Act
        async with database_manager.get_session() as session:
            found_user = await user_repository.find_by_email(email, session)
        
        # Assert
        assert found_user is not None
        assert found_user.email == email.value
        assert found_user.id == user.id
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_find_by_email_non_existing_user(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Act
        email = Email("nonexistent@example.com")
        async with database_manager.get_session() as session:
            found_user = await user_repository.find_by_email(email, session)
        
        # Assert
        assert found_user is None
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_delete_existing_user(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Arrange
        user_id = uuid4()
        user = User(
            id=user_id,
            email="deleteme@example.com",
            hashed_password="hashed_password_123"
        )
        
        # Save user first
        async with database_manager.get_session() as session:
            await user_repository.save(user, session)
        
        # Act
        async with database_manager.get_session() as session:
            deleted = await user_repository.delete(user_id, session)
        
        # Assert
        assert deleted is True
        
        # Verify user is deleted
        async with database_manager.get_session() as session:
            found_user = await user_repository.find_by_id(user_id, session)
        assert found_user is None
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_delete_non_existing_user(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Act
        async with database_manager.get_session() as session:
            deleted = await user_repository.delete(uuid4(), session)
        
        # Assert
        assert deleted is False
        
        await database_manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_user_model_to_entity_conversion(
        self, user_repository: UserRepository, database_manager: DatabaseManager
    ) -> None:
        # Arrange
        user_id = uuid4()
        user = User(
            id=user_id,
            email="convert@example.com",
            hashed_password="hashed_password_123",
            is_active=False  # Test non-default value
        )
        
        # Act - Save and retrieve
        async with database_manager.get_session() as session:
            saved_user = await user_repository.save(user, session)
        
        async with database_manager.get_session() as session:
            retrieved_user = await user_repository.find_by_id(user_id, session)
        
        # Assert conversion is correct
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.email == "convert@example.com"
        assert retrieved_user.hashed_password == "hashed_password_123"
        assert retrieved_user.is_active is False
        assert retrieved_user.created_at is not None
        
        await database_manager.disconnect()