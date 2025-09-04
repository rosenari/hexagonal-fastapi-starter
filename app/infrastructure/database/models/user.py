"""User SQLAlchemy model."""

from uuid import UUID, uuid4
from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class UserModel(Base, TimestampMixin):
    """SQLAlchemy model for users table."""
    
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(
        Uuid(),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        default=True,
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, active={self.is_active})>"