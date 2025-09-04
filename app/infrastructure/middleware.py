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