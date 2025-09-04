"""User-related Data Transfer Objects."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateUserRequest:
    """Request DTO for creating a new user."""
    email: str
    password: str


@dataclass(frozen=True)
class CreateUserResponse:
    """Response DTO for user creation."""
    user_id: UUID
    email: str
    is_active: bool