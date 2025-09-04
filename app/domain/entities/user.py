"""User domain entity."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID


class User:
    """User domain entity representing a user in the system."""
    
    def __init__(
        self,
        id: UUID,
        email: str,
        hashed_password: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at
    
    def activate(self) -> None:
        """Activate the user account."""
        if not self.is_active:
            self.is_active = True
            self._update_timestamp()
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        if self.is_active:
            self.is_active = False
            self._update_timestamp()
    
    def update_email(self, new_email: str) -> None:
        """Update the user's email address."""
        if self.email != new_email:
            self.email = new_email
            self._update_timestamp()
    
    def update_password(self, new_hashed_password: str) -> None:
        """Update the user's password hash."""
        if self.hashed_password != new_hashed_password:
            self.hashed_password = new_hashed_password
            self._update_timestamp()
    
    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)
    
    def __eq__(self, other: object) -> bool:
        """Two users are equal if they have the same ID."""
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on the user ID."""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"User(id={self.id}, email={self.email}, active={self.is_active})"
    
    def __repr__(self) -> str:
        """Detailed representation of the user."""
        return (
            f"User(id={self.id}, email={self.email}, "
            f"is_active={self.is_active}, created_at={self.created_at})"
        )