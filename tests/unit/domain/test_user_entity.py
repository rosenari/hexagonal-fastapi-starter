import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities.user import User


class TestUserEntity:
    def test_create_user_with_valid_data(self) -> None:
        user_id = uuid4()
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        user = User(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        assert user.id == user_id
        assert user.email == email
        assert user.hashed_password == hashed_password
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
    
    def test_create_user_defaults(self) -> None:
        user_id = uuid4()
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        user = User(
            id=user_id,
            email=email,
            hashed_password=hashed_password
        )
        
        # Should default to active and set created_at
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        assert user.updated_at is None
    
    def test_user_activate(self) -> None:
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_password_123",
            is_active=False
        )
        
        user.activate()
        
        assert user.is_active is True
        assert isinstance(user.updated_at, datetime)
    
    def test_user_deactivate(self) -> None:
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        
        user.deactivate()
        
        assert user.is_active is False
        assert isinstance(user.updated_at, datetime)
    
    def test_update_email(self) -> None:
        user = User(
            id=uuid4(),
            email="old@example.com",
            hashed_password="hashed_password_123"
        )
        
        new_email = "new@example.com"
        user.update_email(new_email)
        
        assert user.email == new_email
        assert isinstance(user.updated_at, datetime)
    
    def test_update_password(self) -> None:
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="old_password_hash"
        )
        
        new_password_hash = "new_password_hash_123"
        user.update_password(new_password_hash)
        
        assert user.hashed_password == new_password_hash
        assert isinstance(user.updated_at, datetime)
    
    def test_user_equality(self) -> None:
        user_id = uuid4()
        user1 = User(
            id=user_id,
            email="test@example.com",
            hashed_password="password_hash"
        )
        user2 = User(
            id=user_id,
            email="different@example.com",  # Different email but same ID
            hashed_password="different_hash"
        )
        
        # Users are equal if they have the same ID
        assert user1 == user2
    
    def test_user_inequality(self) -> None:
        user1 = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="password_hash"
        )
        user2 = User(
            id=uuid4(),  # Different ID
            email="test@example.com",
            hashed_password="password_hash"
        )
        
        assert user1 != user2
    
    def test_user_string_representation(self) -> None:
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="password_hash"
        )
        
        str_repr = str(user)
        assert "User" in str_repr
        assert user.email in str_repr
        assert str(user.id) in str_repr