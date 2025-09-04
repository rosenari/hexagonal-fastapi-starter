"""User repository port (interface)."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.user import User
from app.domain.value_objects import Email


class UserRepositoryPort(ABC):
    """Port (interface) for User repository operations."""
    
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find a user by their ID."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by their ID (alias for find_by_id)."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find a user by their email address."""
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user entity."""
        pass
    
    @abstractmethod
    async def list_users(self, offset: int = 0, limit: int = 10) -> List[User]:
        """List users with pagination."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total number of users."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by their ID. Returns True if deleted, False if not found."""
        pass