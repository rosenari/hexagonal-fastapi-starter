import uuid
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from app.infrastructure.middleware import RequestIDMiddleware


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