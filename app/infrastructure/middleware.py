import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to each incoming request."""
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        # Check if request already has a request ID in headers
        request_id = request.headers.get("X-Request-ID")
        
        # Generate a new request ID if none exists
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Store request ID in request state for use in handlers and logging
        request.state.request_id = request_id
        
        # Process the request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("access")
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        # Record start time
        start_time = time.time()
        
        # Get request information
        method = request.method
        url = str(request.url)
        user_agent = request.headers.get("user-agent", "")
        
        # Get request ID from state (set by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", None)
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration in milliseconds
        duration = round((time.time() - start_time) * 1000, 2)
        
        # Log the access information
        log_extra = {
            "request_id": request_id,
            "method": method,
            "url": url,
            "status_code": response.status_code,
            "duration": duration,
            "user_agent": user_agent,
        }
        
        self.logger.info(
            f"{method} {url} - {response.status_code} - {duration}ms",
            extra=log_extra
        )
        
        return response