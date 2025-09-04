import json
import logging
import uuid
from io import StringIO
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from app.infrastructure.middleware import RequestIDMiddleware, AccessLoggingMiddleware


class TestRequestIDMiddleware:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        async def test_endpoint(request: Request) -> dict:
            return {"request_id": getattr(request.state, "request_id", None)}
        
        return app
    
    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        return TestClient(app)
    
    def test_middleware_adds_request_id_to_state(self, client: TestClient) -> None:
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["request_id"] is not None
        
        # Should be a valid UUID
        uuid.UUID(data["request_id"])
    
    def test_middleware_adds_request_id_header(self, client: TestClient) -> None:
        response = client.get("/test")
        
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        
        # Should be a valid UUID
        uuid.UUID(request_id)
    
    def test_middleware_preserves_existing_request_id(self, client: TestClient) -> None:
        existing_request_id = str(uuid.uuid4())
        
        response = client.get("/test", headers={"X-Request-ID": existing_request_id})
        
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == existing_request_id
        
        data = response.json()
        assert data["request_id"] == existing_request_id
    
    def test_middleware_generates_new_id_for_each_request(
        self, client: TestClient
    ) -> None:
        response1 = client.get("/test")
        response2 = client.get("/test")
        
        request_id1 = response1.headers["X-Request-ID"]
        request_id2 = response2.headers["X-Request-ID"]
        
        assert request_id1 != request_id2
    
    @pytest.mark.asyncio
    async def test_middleware_call_next_with_request_state(self) -> None:
        middleware = RequestIDMiddleware(AsyncMock())
        request = Mock(spec=Request)
        request.headers = {}
        request.state = Mock()
        
        call_next = AsyncMock(return_value=Response())
        
        await middleware.dispatch(request, call_next)
        
        # Should have set request_id on request.state
        assert hasattr(request.state, "request_id")
        assert request.state.request_id is not None
        
        # Should be a valid UUID
        uuid.UUID(request.state.request_id)
        
        # Should have called next middleware
        call_next.assert_called_once_with(request)


class TestAccessLoggingMiddleware:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()
        app.add_middleware(AccessLoggingMiddleware)
        app.add_middleware(RequestIDMiddleware)  # Add RequestID middleware for context
        
        @app.get("/test")
        async def test_endpoint() -> dict:
            return {"message": "success"}
        
        @app.post("/test")
        async def test_post_endpoint(request: Request) -> dict:
            return {"message": "created"}
        
        return app
    
    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        return TestClient(app)
    
    def test_middleware_logs_request_and_response(self, client: TestClient) -> None:
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        # Set up JSON formatter for access logger
        from app.infrastructure.logging import CustomJsonFormatter
        formatter = CustomJsonFormatter()
        handler.setFormatter(formatter)
        
        access_logger = logging.getLogger("access")
        access_logger.handlers.clear()
        access_logger.addHandler(handler)
        access_logger.setLevel(logging.INFO)
        
        response = client.get("/test")
        
        assert response.status_code == 200
        
        log_output = log_stream.getvalue().strip()
        log_lines = log_output.split('\n')
        
        # Should have at least one log entry
        assert len(log_lines) >= 1
        
        # Parse the first log entry
        log_data = json.loads(log_lines[0])
        
        assert log_data["level"] == "INFO"
        assert log_data["name"] == "access"
        assert "request_id" in log_data
        assert log_data["method"] == "GET"
        assert log_data["url"] == "http://testserver/test"
        assert log_data["status_code"] == 200
        assert "duration" in log_data
        assert "user_agent" in log_data
    
    def test_middleware_logs_different_methods(self, client: TestClient) -> None:
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        from app.infrastructure.logging import CustomJsonFormatter
        formatter = CustomJsonFormatter()
        handler.setFormatter(formatter)
        
        access_logger = logging.getLogger("access")
        access_logger.handlers.clear()
        access_logger.addHandler(handler)
        access_logger.setLevel(logging.INFO)
        
        # Test POST request
        response = client.post("/test", json={"data": "test"})
        
        assert response.status_code == 200
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["method"] == "POST"
        assert log_data["url"] == "http://testserver/test"
    
    def test_middleware_includes_request_id_in_logs(self, client: TestClient) -> None:
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        from app.infrastructure.logging import CustomJsonFormatter
        formatter = CustomJsonFormatter()
        handler.setFormatter(formatter)
        
        access_logger = logging.getLogger("access")
        access_logger.handlers.clear()
        access_logger.addHandler(handler)
        access_logger.setLevel(logging.INFO)
        
        # Make request with custom request ID
        custom_request_id = str(uuid.uuid4())
        response = client.get("/test", headers={"X-Request-ID": custom_request_id})
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["request_id"] == custom_request_id
    
    def test_middleware_measures_duration(self, client: TestClient) -> None:
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        from app.infrastructure.logging import CustomJsonFormatter
        formatter = CustomJsonFormatter()
        handler.setFormatter(formatter)
        
        access_logger = logging.getLogger("access")
        access_logger.handlers.clear()
        access_logger.addHandler(handler)
        access_logger.setLevel(logging.INFO)
        
        response = client.get("/test")
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert "duration" in log_data
        # Duration should be a positive number (in milliseconds)
        assert isinstance(log_data["duration"], (int, float))
        assert log_data["duration"] >= 0