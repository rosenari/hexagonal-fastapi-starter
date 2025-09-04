"""Tests for User API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import create_app
from app.domain.entities.user import User
from app.application.dtos.user_dtos import CreateUserRequest, CreateUserResponse


class TestUserAPI:
    @pytest.fixture
    async def client(self) -> TestClient:
        from app.infrastructure.container import get_application_container
        import tempfile
        import os
        
        app = create_app()
        
        # Create a temporary database file for each test
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        # Setup for testing - manually wire and setup database
        container = get_application_container()
        
        # Override database URL to use temp database
        container.config.database_url.from_value(f"sqlite+aiosqlite:///{temp_db_path}")
        app.container = container
        
        # Wire dependencies
        container.wire(modules=["app.presentation.api.users"])
        
        # Connect to database
        await container.infrastructure.database_manager().connect()
        await container.infrastructure.database_manager().create_tables()
        
        client = TestClient(app)
        
        yield client
        
        # Cleanup
        container.unwire()
        await container.infrastructure.database_manager().disconnect()
        
        # Remove temporary database file
        try:
            os.unlink(temp_db_path)
        except OSError:
            pass
    
    @pytest.fixture
    def mock_create_user_use_case(self) -> AsyncMock:
        return AsyncMock()
    
    def test_create_user_success(self, client: TestClient) -> None:
        """Test successful user creation."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/api/users", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert "password" not in data  # Password should not be returned
        assert "created_at" in data
    
    def test_create_user_invalid_email(self, client: TestClient) -> None:
        """Test user creation with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/api/users", json=user_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_user_invalid_password(self, client: TestClient) -> None:
        """Test user creation with invalid password."""
        user_data = {
            "email": "test@example.com",
            "password": "123"  # Too short
        }
        
        response = client.post("/api/users", json=user_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_user_duplicate_email(self, client: TestClient) -> None:
        """Test user creation with duplicate email."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        # Create first user
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 201
        
        # Try to create duplicate
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"]
    
    def test_get_user_success(self, client: TestClient) -> None:
        """Test successful user retrieval."""
        # First create a user
        user_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        create_response = client.post("/api/users", json=user_data)
        assert create_response.status_code == 201
        created_user = create_response.json()
        
        # Then get the user
        response = client.get(f"/api/users/{created_user['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user["id"]
        assert data["email"] == user_data["email"]
        assert "password" not in data
        assert "created_at" in data
    
    def test_get_user_not_found(self, client: TestClient) -> None:
        """Test user retrieval for non-existent user."""
        import uuid
        non_existent_id = str(uuid.uuid4())
        
        response = client.get(f"/api/users/{non_existent_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_user_invalid_uuid(self, client: TestClient) -> None:
        """Test user retrieval with invalid UUID format."""
        response = client.get("/api/users/invalid-uuid")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_list_users_success(self, client: TestClient) -> None:
        """Test successful user listing."""
        # Create some users first
        users_data = [
            {"email": "user1@example.com", "password": "SecurePassword123!"},
            {"email": "user2@example.com", "password": "SecurePassword123!"},
        ]
        
        for user_data in users_data:
            response = client.post("/api/users", json=user_data)
            assert response.status_code == 201
        
        # List users
        response = client.get("/api/users")
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert len(data["users"]) >= 2
    
    def test_list_users_with_pagination(self, client: TestClient) -> None:
        """Test user listing with pagination parameters."""
        response = client.get("/api/users?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["offset"] == 0
        assert data["limit"] == 5
    
    def test_request_id_in_response_headers(self, client: TestClient) -> None:
        """Test that request ID is included in response headers."""
        response = client.get("/api/users")
        
        assert "X-Request-ID" in response.headers
        
        # Should be a valid UUID format
        import uuid
        uuid.UUID(response.headers["X-Request-ID"])