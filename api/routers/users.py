# Endpoints: CRUD for UserAccount + business actions (unlock, deactivate)

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from src.models import Role, AccountStatus
from services.user_service import (
    UserService, UserAlreadyExistsError,
    UserNotFoundError, InvalidOperationError
)

router = APIRouter(prefix="/api/users", tags=["Users"])
service: UserService = None  # Injected in main.py


# ─── Pydantic Schemas ──────────────────────────────────────────────────────────

class CreateUserRequest(BaseModel):
    email: str = Field(..., example="alice@corp.com", description="Corporate email address")
    role: Role = Field(..., example="HR_MANAGER", description="User role")

class UpdateRoleRequest(BaseModel):
    role: Role = Field(..., example="FINANCE_OFFICER", description="New role to assign")

class UserResponse(BaseModel):
    user_id: str
    email: str
    role: str
    status: str
    failed_login_attempts: int

    @classmethod
    def from_model(cls, user):
        return cls(
            user_id=user.user_id,
            email=user.email,
            role=user.role.value,
            status=user.status.value,
            failed_login_attempts=user.failed_login_attempts
        )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Returns a list of all registered user accounts."
)
def get_all_users():
    users = service.get_all_users()
    return [UserResponse.from_model(u) for u in users]


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user account with the given email and role. Email must be unique."
)
def create_user(request: CreateUserRequest):
    try:
        user = service.create_user(request.email, request.role)
        return UserResponse.from_model(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns a single user account by its unique ID."
)
def get_user(user_id: str):
    try:
        user = service.get_user(user_id)
        return UserResponse.from_model(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Update user role",
    description="Updates the role of an existing user. Cannot update a DELETED account."
)
def update_role(user_id: str, request: UpdateRoleRequest):
    try:
        user = service.update_role(user_id, request.role)
        return UserResponse.from_model(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user",
    description="Deactivates a user account. The user loses access immediately."
)
def deactivate_user(user_id: str):
    try:
        user = service.deactivate_user(user_id)
        return UserResponse.from_model(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{user_id}/unlock",
    response_model=UserResponse,
    summary="Unlock user account",
    description="Unlocks a locked user account and resets failed login counter."
)
def unlock_user(user_id: str):
    try:
        user = service.unlock_user(user_id)
        return UserResponse.from_model(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Permanently deletes a user account."
)
def delete_user(user_id: str):
    try:
        service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/count/total",
    summary="Count users",
    description="Returns the total number of registered user accounts."
)
def count_users():
    return {"count": service.count_users()}
