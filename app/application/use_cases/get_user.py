"""Get user use case."""

from uuid import UUID

from app.application.dtos.user_dtos import GetUserResponse
from app.application.ports.user_repository import UserRepositoryPort
from app.application.exceptions import UserNotFoundError

logger = logging.getLogger(__name__)


class GetUserUseCase:
    """Use case for getting a user by ID."""
    
    def __init__(self, user_repository: UserRepositoryPort) -> None:
        self._user_repository = user_repository
    
    async def execute(self, user_id: UUID) -> GetUserResponse:
        """Execute the get user use case."""
        logger.info("Getting user", extra={"user_id": str(user_id)})
        
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return GetUserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        )