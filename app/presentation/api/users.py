"""User API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.application.dtos.user_dtos import CreateUserRequest, CreateUserResponse, GetUserResponse
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.get_user import GetUserUseCase
from app.application.use_cases.list_users import ListUsersUseCase
from app.infrastructure.container import ApplicationContainer
from app.application.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.exceptions import ValidationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users")


@router.post("/", status_code=201, response_model=CreateUserResponse)
@inject
async def create_user(
    request: CreateUserRequest,
    create_user_use_case: CreateUserUseCase = Depends(
        Provide[ApplicationContainer.services.create_user_use_case]
    ),
) -> CreateUserResponse:
    """Create a new user."""
    logger.info("Creating user", extra={"email": request.email})
    
    try:
        user = await create_user_use_case.execute(request)
        logger.info("User created successfully", extra={"user_id": str(user.id), "email": user.email})
        return user
    except UserAlreadyExistsError as e:
        logger.warning("User creation failed - email already exists", extra={"email": request.email})
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        logger.warning("User creation failed - validation error", extra={"email": request.email, "error": str(e)})
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error during user creation", extra={"email": request.email, "error": str(e)})
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", response_model=GetUserResponse)
@inject
async def get_user(
    user_id: UUID,
    get_user_use_case: GetUserUseCase = Depends(
        Provide[ApplicationContainer.services.get_user_use_case]
    ),
) -> GetUserResponse:
    """Get user by ID."""
    logger.info("Getting user", extra={"user_id": str(user_id)})
    
    try:
        user = await get_user_use_case.execute(user_id)
        logger.info("User retrieved successfully", extra={"user_id": str(user_id)})
        return user
    except UserNotFoundError as e:
        logger.warning("User not found", extra={"user_id": str(user_id)})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error during user retrieval", extra={"user_id": str(user_id), "error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=dict)
@inject
async def list_users(
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    list_users_use_case: ListUsersUseCase = Depends(
        Provide[ApplicationContainer.services.list_users_use_case]
    ),
) -> dict:
    """List users with pagination."""
    logger.info("Listing users", extra={"offset": offset, "limit": limit})
    
    try:
        result = await list_users_use_case.execute(offset=offset, limit=limit)
        logger.info("Users listed successfully", extra={"total": result["total"], "count": len(result["users"])})
        return {
            "users": result["users"],
            "total": result["total"],
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        logger.error("Unexpected error during user listing", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")