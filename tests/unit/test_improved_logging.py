import json
import logging
import uuid
from io import StringIO

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infrastructure.logging import setup_logging, get_logger, CustomJsonFormatter, RequestIDFilter
from app.infrastructure.middleware import RequestIDMiddleware


def setup_test_logger(name: str, log_stream: StringIO) -> logging.Logger:
    """Helper to set up a logger with JSON formatter and request ID filter."""
    logger = get_logger(name)
    
    handler = logging.StreamHandler(log_stream)
    formatter = CustomJsonFormatter()
    request_id_filter = RequestIDFilter()
    
    handler.setFormatter(formatter)
    handler.addFilter(request_id_filter)
    
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger


class TestImprovedLogging:
    def test_request_id_context_propagation(self) -> None:
        """Test that request_id is propagated to all logs via context variable."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        log_stream = StringIO()
        logger = setup_test_logger("test_service", log_stream)
        
        @app.get("/test")
        async def test_endpoint() -> dict:
            # This should automatically include request_id from context
            logger.info("Processing request in service")
            return {"status": "success"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        # Should have request_id from context
        assert "request_id" in log_data
        assert log_data["request_id"] != "N/A"
        
        # Should be a valid UUID
        uuid.UUID(log_data["request_id"])
        
        # Should be same as response header
        assert log_data["request_id"] == response.headers["X-Request-ID"]
    
    def test_request_id_in_nested_service_calls(self) -> None:
        """Test that request_id propagates through nested service calls."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        log_stream = StringIO()
        user_service_logger = setup_test_logger("user_service", log_stream)
        auth_service_logger = setup_test_logger("auth_service", log_stream)
        
        @app.post("/users")
        async def create_user() -> dict:
            user_service_logger.info("Creating user in user service")
            
            # Simulate nested service call
            auth_service_logger.info("Generating auth token in auth service")
            
            return {"user_id": 123}
        
        client = TestClient(app)
        response = client.post("/users")
        
        assert response.status_code == 200
        
        log_output = log_stream.getvalue().strip()
        log_lines = log_output.split('\n')
        
        assert len(log_lines) >= 2
        
        # Both logs should have the same request_id
        log1_data = json.loads(log_lines[0])
        log2_data = json.loads(log_lines[1])
        
        assert log1_data["request_id"] == log2_data["request_id"]
        assert log1_data["request_id"] == response.headers["X-Request-ID"]
    
    def test_request_id_fallback_outside_request_context(self) -> None:
        """Test that logs outside request context get N/A for request_id."""
        log_stream = StringIO()
        logger = setup_test_logger("background_service", log_stream)
        
        # This should work even outside request context
        logger.info("Background task running")
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["request_id"] == "N/A"
    
    def test_error_logs_include_request_id(self) -> None:
        """Test that error logs also include request_id."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        log_stream = StringIO()
        logger = setup_test_logger("error_service", log_stream)
        logger.setLevel(logging.ERROR)  # Only capture ERROR logs
        
        @app.get("/error")
        async def error_endpoint() -> dict:
            try:
                raise ValueError("Test error")
            except ValueError as e:
                logger.error(f"An error occurred: {e}")
                return {"error": "handled"}
        
        client = TestClient(app)
        response = client.get("/error")
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["level"] == "ERROR"
        assert "request_id" in log_data
        assert log_data["request_id"] == response.headers["X-Request-ID"]
    
    def test_custom_request_id_preservation(self) -> None:
        """Test that custom request_id from headers is preserved."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        log_stream = StringIO()
        logger = setup_test_logger("test_service", log_stream)
        
        @app.get("/test")
        async def test_endpoint() -> dict:
            logger.info("Processing with custom request ID")
            return {"status": "ok"}
        
        custom_request_id = str(uuid.uuid4())
        client = TestClient(app)
        response = client.get("/test", headers={"X-Request-ID": custom_request_id})
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["request_id"] == custom_request_id
        assert response.headers["X-Request-ID"] == custom_request_id