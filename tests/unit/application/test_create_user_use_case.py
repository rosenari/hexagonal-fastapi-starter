import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from pydantic import ValidationError as PydanticValidationError

from app.application.use_cases.create_user import CreateUserUseCase
from app.application.dtos.user_dtos import CreateUserRequest, CreateUserResponse
from app.application.exceptions import UserAlreadyExistsError
from app.domain.entities.user import User
from app.domain.value_objects import Email, Password
from app.domain.services import PasswordService
from app.domain.exceptions import ValidationError


class TestCreateUserUseCase:
    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        return AsyncMock()
    
    @pytest.fixture
    def mock_password_service(self) -> Mock:
        mock = Mock(spec=PasswordService)
        mock.hash_password.return_value = "hashed_password_123"
        return mock
    
    @pytest.fixture
    def use_case(self, mock_user_repository: AsyncMock, mock_password_service: Mock) -> CreateUserUseCase:
        return CreateUserUseCase(
            user_repository=mock_user_repository,
            password_service=mock_password_service
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        use_case: CreateUserUseCase,
        mock_user_repository: AsyncMock,
        mock_password_service: Mock
    ) -> None:
        # Arrange
        request = CreateUserRequest(
            email="test@example.com",
            password="TestPassword123!"
        )
        
        user_id = uuid4()
        created_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        mock_user_repository.find_by_email.return_value = None  # User doesn't exist
        mock_user_repository.save.return_value = created_user
        
        # Act
        response = await use_case.execute(request)
        
        # Assert
        assert isinstance(response, CreateUserResponse)
        assert response.id == user_id
        assert response.email == "test@example.com"
        assert response.created_at == created_user.created_at
        
        # Verify interactions
        mock_user_repository.find_by_email.assert_called_once()
        mock_password_service.hash_password.assert_called_once()
        mock_user_repository.save.assert_called_once()
        
        # Verify password was hashed
        saved_user_args = mock_user_repository.save.call_args[0][0]
        assert saved_user_args.hashed_password == "hashed_password_123"
    
    @pytest.mark.asyncio
    async def test_create_user_email_already_exists(
        self,
        use_case: CreateUserUseCase,
        mock_user_repository: AsyncMock,
        mock_password_service: Mock
    ) -> None:
        # Arrange
        request = CreateUserRequest(
            email="existing@example.com",
            password="TestPassword123!"
        )
        
        existing_user = User(
            id=uuid4(),
            email="existing@example.com",
            hashed_password="existing_hash"
        )
        
        mock_user_repository.find_by_email.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError, match="User with email .* already exists"):
            await use_case.execute(request)
        
        # Verify password service was not called
        mock_password_service.hash_password.assert_not_called()
        mock_user_repository.save.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_email_format(
        self,
        use_case: CreateUserUseCase,
        mock_user_repository: AsyncMock,
        mock_password_service: Mock
    ) -> None:
        # Arrange
        request = CreateUserRequest(
            email="invalid-email",
            password="TestPassword123!"
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid email format"):
            await use_case.execute(request)
        
        # Verify no repository calls were made
        mock_user_repository.find_by_email.assert_not_called()
        mock_user_repository.save.assert_not_called()
    
    def test_create_user_invalid_password_pydantic_validation(self) -> None:
        # Test that Pydantic validates password length before the request reaches the use case
        with pytest.raises(PydanticValidationError):
            CreateUserRequest(
                email="test@example.com",
                password="weak"  # Too short - less than 8 characters
            )
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_password_value_object_validation(
        self,
        use_case: CreateUserUseCase,
        mock_user_repository: AsyncMock,
        mock_password_service: Mock
    ) -> None:
        # Arrange - password passes Pydantic validation but fails value object validation
        request = CreateUserRequest(
            email="test@example.com",
            password="weak1234"  # Missing uppercase, special character
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Password must contain at least one uppercase letter"):
            await use_case.execute(request)
        
        # Verify no repository calls were made
        mock_user_repository.find_by_email.assert_not_called()
        mock_user_repository.save.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_user_repository_error(
        self,
        use_case: CreateUserUseCase,
        mock_user_repository: AsyncMock,
        mock_password_service: Mock
    ) -> None:
        # Arrange
        request = CreateUserRequest(
            email="test@example.com",
            password="TestPassword123!"
        )
        
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.save.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(request)
        
        # Verify password service was called but save failed
        mock_password_service.hash_password.assert_called_once()
        mock_user_repository.save.assert_called_once()
    
    def test_create_user_request_validation(self) -> None:
        # Valid request
        request = CreateUserRequest(
            email="test@example.com",
            password="TestPassword123!"
        )
        assert request.email == "test@example.com"
        assert request.password == "TestPassword123!"
    
    def test_create_user_response_creation(self) -> None:
        from datetime import datetime, timezone
        user_id = uuid4()
        created_at = datetime.now(timezone.utc)
        response = CreateUserResponse(
            id=user_id,
            email="test@example.com",
            created_at=created_at
        )
        
        assert response.id == user_id
        assert response.email == "test@example.com"
        assert response.created_at == created_at