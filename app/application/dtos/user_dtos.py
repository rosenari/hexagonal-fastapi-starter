"""User-related Data Transfer Objects."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    """Request DTO for creating a new user."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class CreateUserResponse(BaseModel):
    """Response DTO for user creation."""
    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="User creation timestamp")


class GetUserResponse(BaseModel):
    """Response DTO for getting a user."""
    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="User creation timestamp")