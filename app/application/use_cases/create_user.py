"""Create User use case."""

import logging
from uuid import uuid4

from app.application.dtos.user_dtos import CreateUserRequest, CreateUserResponse
from app.application.exceptions import UserAlreadyExistsError
from app.application.ports.user_repository import UserRepositoryPort
from app.domain.entities.user import User
from app.domain.services.password_service import PasswordService
from app.domain.value_objects import Email, Password
from app.infrastructure.logging import get_logger


class CreateUserUseCase:
    """Use case for creating a new user."""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_service: PasswordService
    ) -> None:
        self.user_repository = user_repository
        self.password_service = password_service
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """
        Execute the create user use case.
        
        Args:
            request: The create user request DTO
            
        Returns:
            CreateUserResponse with the created user information
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            ValidationError: If email or password validation fails
        """
        self.logger.info(f"Creating user with email: {request.email}")
        
        # Validate and create value objects (this will raise ValidationError if invalid)
        email = Email(request.email)
        password = Password(request.password)
        
        # Check if user already exists
        existing_user = await self.user_repository.find_by_email(email)
        if existing_user:
            self.logger.warning(f"Attempt to create user with existing email: {request.email}")
            raise UserAlreadyExistsError(f"User with email {request.email} already exists")
        
        # Hash the password
        hashed_password = self.password_service.hash_password(password)
        
        # Create user entity
        user = User(
            id=uuid4(),
            email=email.value,
            hashed_password=hashed_password
        )
        
        # Save user
        saved_user = await self.user_repository.save(user)
        
        self.logger.info(f"User created successfully: {saved_user.id}")
        
        # Return response DTO
        return CreateUserResponse(
            id=saved_user.id,
            email=saved_user.email,
            created_at=saved_user.created_at
        )