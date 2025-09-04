"""User repository implementation using SQLAlchemy."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.user_repository import UserRepositoryPort
from app.domain.entities.user import User
from app.domain.value_objects import Email
from app.infrastructure.database.connection import DatabaseManager
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.logging import get_logger


class UserRepository(UserRepositoryPort):
    """SQLAlchemy implementation of User repository."""
    
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager
        self.logger = get_logger(self.__class__.__name__)
    
    async def find_by_id(self, user_id: UUID, session: Optional[AsyncSession] = None) -> Optional[User]:
        """Find a user by their ID."""
        if session is None:
            async with self.database_manager.get_session() as session:
                return await self._find_by_id_impl(user_id, session)
        else:
            return await self._find_by_id_impl(user_id, session)
    
    async def _find_by_id_impl(self, user_id: UUID, session: AsyncSession) -> Optional[User]:
        self.logger.info(f"Finding user by ID: {user_id}")
        
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model is None:
            self.logger.info(f"User not found with ID: {user_id}")
            return None
        
        self.logger.info(f"Found user: {user_id}")
        return self._model_to_entity(user_model)
    
    async def find_by_email(self, email: Email, session: Optional[AsyncSession] = None) -> Optional[User]:
        """Find a user by their email address."""
        if session is None:
            async with self.database_manager.get_session() as session:
                return await self._find_by_email_impl(email, session)
        else:
            return await self._find_by_email_impl(email, session)
    
    async def _find_by_email_impl(self, email: Email, session: AsyncSession) -> Optional[User]:
        self.logger.info(f"Finding user by email: {email.value}")
        
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model is None:
            self.logger.info(f"User not found with email: {email.value}")
            return None
        
        self.logger.info(f"Found user with email: {email.value}")
        return self._model_to_entity(user_model)
    
    async def save(self, user: User, session: Optional[AsyncSession] = None) -> User:
        """Save a user entity."""
        if session is None:
            async with self.database_manager.get_session() as session:
                return await self._save_impl(user, session)
        else:
            return await self._save_impl(user, session)
    
    async def _save_impl(self, user: User, session: AsyncSession) -> User:
        self.logger.info(f"Saving user: {user.id}")
        
        # Check if user exists
        existing_model = await session.get(UserModel, user.id)
        
        if existing_model:
            # Update existing user
            existing_model.email = user.email
            existing_model.hashed_password = user.hashed_password
            existing_model.is_active = user.is_active
            existing_model.updated_at = user.updated_at
            user_model = existing_model
        else:
            # Create new user
            user_model = self._entity_to_model(user)
            session.add(user_model)
        
        await session.flush()  # Ensure the model is persisted and has all attributes
        
        self.logger.info(f"User saved: {user.id}")
        return self._model_to_entity(user_model)
    
    async def delete(self, user_id: UUID, session: Optional[AsyncSession] = None) -> bool:
        """Delete a user by their ID. Returns True if deleted, False if not found."""
        if session is None:
            async with self.database_manager.get_session() as session:
                return await self._delete_impl(user_id, session)
        else:
            return await self._delete_impl(user_id, session)
    
    async def _delete_impl(self, user_id: UUID, session: AsyncSession) -> bool:
        self.logger.info(f"Deleting user: {user_id}")
        
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        
        deleted = result.rowcount > 0
        if deleted:
            self.logger.info(f"User deleted: {user_id}")
        else:
            self.logger.info(f"User not found for deletion: {user_id}")
        
        return deleted
    
    def _entity_to_model(self, user: User) -> UserModel:
        """Convert User entity to UserModel."""
        return UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def _model_to_entity(self, user_model: UserModel) -> User:
        """Convert UserModel to User entity."""
        return User(
            id=user_model.id,
            email=user_model.email,
            hashed_password=user_model.hashed_password,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )