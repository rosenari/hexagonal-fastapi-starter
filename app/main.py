"""FastAPI application factory and configuration."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.container import get_application_container
from app.infrastructure.logging import setup_logging
from app.infrastructure.middleware import RequestIDMiddleware, AccessLoggingMiddleware
from app.presentation.api.health import router as health_router
from app.presentation.api.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    
    # Initialize container and resources
    container = get_application_container()
    app.container = container
    
    # Connect to database
    await container.infrastructure.database_manager().connect()
    await container.infrastructure.database_manager().create_tables()
    
    # Wire dependency injection
    container.wire(modules=[
        "app.presentation.api.users",
        "app.presentation.api.health",
    ])
    
    yield
    
    # Cleanup
    container.unwire()
    await container.infrastructure.database_manager().disconnect()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Hexagonal FastAPI Starter",
        description="A FastAPI application built with Hexagonal Architecture",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add middleware (order matters - last added = first executed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(AccessLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    # Add routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(users_router, tags=["Users"])
    
    # Global exception handlers can be added here
    # @app.exception_handler(Exception)
    # async def global_exception_handler(request: Request, exc: Exception):
    #     return JSONResponse(
    #         status_code=500,
    #         content={"detail": "Internal server error"}
    #     )
    
    return app


# Create app instance
app = create_app()