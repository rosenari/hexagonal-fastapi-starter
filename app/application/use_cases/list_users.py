"""List users use case."""

from typing import List, Dict, Any

from app.application.dtos.user_dtos import GetUserResponse
from app.application.ports.user_repository import UserRepositoryPort

logger = logging.getLogger(__name__)


class ListUsersUseCase:
    """Use case for listing users with pagination."""
    
    def __init__(self, user_repository: UserRepositoryPort) -> None:
        self._user_repository = user_repository
    
    async def execute(self, offset: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Execute the list users use case."""
        logger.info("Listing users", extra={"offset": offset, "limit": limit})
        
        users = await self._user_repository.list_users(offset=offset, limit=limit)
        total = await self._user_repository.count()
        
        user_responses = [
            GetUserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at
            )
            for user in users
        ]
        
        return {
            "users": user_responses,
            "total": total
        }