"""Dependency injection containers using dependency-injector."""

from dependency_injector import containers, providers

from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.get_user import GetUserUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.domain.services.password_service import PasswordService
from app.infrastructure.database.connection import DatabaseManager
from app.infrastructure.database.repositories.user_repository import UserRepository


class InfrastructureContainer(containers.DeclarativeContainer):
    """Infrastructure layer dependency container."""
    
    # Configuration
    config = providers.Configuration()
    
    # Database manager as singleton
    database_manager = providers.Singleton(
        DatabaseManager,
        database_url=config.database_url
    )
    
    # Password service as singleton (stateless)
    password_service = providers.Singleton(
        PasswordService
    )


class RepositoryContainer(containers.DeclarativeContainer):
    """Repository layer dependency container."""
    
    # Infrastructure dependencies
    infrastructure = providers.DependenciesContainer()
    
    # User repository factory (new instance per request)
    user_repository = providers.Factory(
        UserRepository,
        database_manager=infrastructure.database_manager
    )


class ServiceContainer(containers.DeclarativeContainer):
    """Service/Use case layer dependency container."""
    
    # Dependencies from other containers
    infrastructure = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    
    # Use cases as factories (new instance per request)
    create_user_use_case :CreateUserUseCase = providers.Factory(
        CreateUserUseCase,
        user_repository=repositories.user_repository,
        password_service=infrastructure.password_service
    )
    
    get_user_use_case: GetUserUseCase = providers.Factory(
        GetUserUseCase,
        user_repository=repositories.user_repository
    )
    
    list_users_use_case: ListUsersUseCase = providers.Factory(
        ListUsersUseCase,
        user_repository=repositories.user_repository
    )


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application dependency container."""
    
    # Configuration
    config = providers.Configuration()
    
    # Infrastructure container
    infrastructure: InfrastructureContainer = providers.Container(
        InfrastructureContainer,
        config=config
    )
    
    # Repository container with infrastructure injection
    repositories: RepositoryContainer = providers.Container(
        RepositoryContainer,
        infrastructure=infrastructure
    )
    
    # Service container with infrastructure and repository injection
    services: ServiceContainer = providers.Container(
        ServiceContainer,
        infrastructure=infrastructure,
        repositories=repositories
    )


def get_application_container() -> ApplicationContainer:
    """Get the configured application container."""
    container = ApplicationContainer()
    
    # Load configuration from settings
    from app.infrastructure.config import settings
    
    container.config.database_url.from_value(
        settings.database_url or "sqlite+aiosqlite:///./hexagonal_fastapi.db"
    )
    
    return container