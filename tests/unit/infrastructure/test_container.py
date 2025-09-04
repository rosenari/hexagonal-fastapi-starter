import pytest
from unittest.mock import Mock, AsyncMock

from app.application.ports.user_repository import UserRepositoryPort
from app.application.use_cases.create_user import CreateUserUseCase
from app.domain.services.password_service import PasswordService
from app.infrastructure.container import (
    InfrastructureContainer,
    RepositoryContainer, 
    ServiceContainer,
    ApplicationContainer
)
from app.infrastructure.database.connection import DatabaseManager


class TestContainers:
    def test_infrastructure_container_creation(self) -> None:
        """Test that infrastructure container can be created."""
        container = InfrastructureContainer()
        assert container is not None
    
    def test_infrastructure_container_provides_database_manager(self) -> None:
        """Test that infrastructure container provides database manager."""
        container = InfrastructureContainer()
        
        # Provide database URL
        container.config.database_url.from_value("sqlite+aiosqlite:///:memory:")
        
        database_manager = container.database_manager()
        assert isinstance(database_manager, DatabaseManager)
        assert database_manager.database_url == "sqlite+aiosqlite:///:memory:"
    
    def test_infrastructure_container_provides_password_service(self) -> None:
        """Test that infrastructure container provides password service."""
        container = InfrastructureContainer()
        
        password_service = container.password_service()
        assert isinstance(password_service, PasswordService)
    
    def test_repository_container_creation(self) -> None:
        """Test that repository container can be created with dependencies."""
        repository_container = RepositoryContainer()
        
        # Mock infrastructure dependencies
        mock_db_manager = Mock(spec=DatabaseManager)
        repository_container.infrastructure.database_manager.override(mock_db_manager)
        
        user_repository = repository_container.user_repository()
        assert isinstance(user_repository, UserRepositoryPort)
    
    def test_service_container_creation(self) -> None:
        """Test that service container can be created with dependencies."""
        service_container = ServiceContainer()
        
        # Mock dependencies
        mock_user_repository = Mock(spec=UserRepositoryPort)
        mock_password_service = Mock(spec=PasswordService)
        
        service_container.repositories.user_repository.override(mock_user_repository)
        service_container.infrastructure.password_service.override(mock_password_service)
        
        create_user_use_case = service_container.create_user_use_case()
        assert isinstance(create_user_use_case, CreateUserUseCase)
    
    def test_application_container_wiring(self) -> None:
        """Test that application container can wire all dependencies."""
        container = ApplicationContainer()
        
        # Provide configuration
        container.config.database_url.from_value("sqlite+aiosqlite:///:memory:")
        
        # Test that all containers are accessible
        assert container.infrastructure is not None
        assert container.repositories is not None
        assert container.services is not None
        
        # Test that services can be created
        password_service = container.infrastructure.password_service()
        assert isinstance(password_service, PasswordService)
    
    def test_application_container_dependency_injection(self) -> None:
        """Test that dependencies are properly injected through containers."""
        container = ApplicationContainer()
        container.config.database_url.from_value("sqlite+aiosqlite:///:memory:")
        
        # Get service from container
        create_user_use_case = container.services.create_user_use_case()
        
        # Verify it's the right type
        assert isinstance(create_user_use_case, CreateUserUseCase)
        
        # Verify dependencies were injected
        assert hasattr(create_user_use_case, 'user_repository')
        assert hasattr(create_user_use_case, 'password_service')
    
    def test_container_singleton_behavior(self) -> None:
        """Test that singleton services return the same instance."""
        container = ApplicationContainer()
        container.config.database_url.from_value("sqlite+aiosqlite:///:memory:")
        
        # Get the same service twice
        service1 = container.infrastructure.password_service()
        service2 = container.infrastructure.password_service()
        
        # Should be the same instance (singleton)
        assert service1 is service2
    
    def test_container_factory_behavior(self) -> None:
        """Test that factory services return new instances."""
        container = ApplicationContainer()
        container.config.database_url.from_value("sqlite+aiosqlite:///:memory:")
        
        # Get the same service twice
        use_case1 = container.services.create_user_use_case()
        use_case2 = container.services.create_user_use_case()
        
        # Should be different instances (factory)
        assert use_case1 is not use_case2
        assert type(use_case1) == type(use_case2)
    
    def test_container_override_for_testing(self) -> None:
        """Test that container dependencies can be overridden for testing."""
        container = ApplicationContainer()
        
        # Create mock
        mock_user_repository = AsyncMock(spec=UserRepositoryPort)
        
        # Override the dependency
        container.repositories.user_repository.override(mock_user_repository)
        
        # Get service
        create_user_use_case = container.services.create_user_use_case()
        
        # Verify mock was injected
        assert create_user_use_case.user_repository is mock_user_repository