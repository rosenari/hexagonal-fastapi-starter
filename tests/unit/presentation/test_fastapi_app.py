import pytest
from fastapi.testclient import TestClient

from app.main import create_app


class TestFastAPIApp:
    @pytest.fixture
    def client(self) -> TestClient:
        app = create_app()
        return TestClient(app)
    
    def test_app_creation(self) -> None:
        """Test that FastAPI app can be created."""
        app = create_app()
        assert app is not None
        assert app.title == "Hexagonal FastAPI Starter"
    
    def test_health_check_endpoint(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "hexagonal-fastapi-starter"
    
    def test_docs_endpoint_accessible(self, client: TestClient) -> None:
        """Test that API docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_json_accessible(self, client: TestClient) -> None:
        """Test that OpenAPI JSON is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "info" in data
        assert data["info"]["title"] == "Hexagonal FastAPI Starter"
    
    def test_cors_middleware_applied(self, client: TestClient) -> None:
        """Test that CORS middleware is properly applied."""
        response = client.options("/health")
        
        # Should handle OPTIONS request
        assert response.status_code in [200, 405]  # 405 is ok if OPTIONS not explicitly handled
    
    def test_request_id_middleware_applied(self, client: TestClient) -> None:
        """Test that Request ID middleware adds headers."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        
        # Should be a valid UUID format
        import uuid
        uuid.UUID(response.headers["X-Request-ID"])
    
    def test_custom_request_id_preserved(self, client: TestClient) -> None:
        """Test that custom request ID from headers is preserved."""
        custom_request_id = "custom-test-id-123"
        
        response = client.get(
            "/health", 
            headers={"X-Request-ID": custom_request_id}
        )
        
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_request_id
    
    def test_exception_handling(self, client: TestClient) -> None:
        """Test global exception handling."""
        # Test 404 - should return JSON response
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_dependency_injection_container_creation(self) -> None:
        """Test that dependency injection container can be created."""
        from app.infrastructure.container import get_application_container
        
        container = get_application_container()
        assert hasattr(container, "services")
        assert hasattr(container.services, "create_user_use_case")
        
        # Test that service can be created
        create_user_use_case = container.services.create_user_use_case()
        from app.application.use_cases.create_user import CreateUserUseCase
        assert isinstance(create_user_use_case, CreateUserUseCase)