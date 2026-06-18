from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from modules.rbac.auth import authenticate_user, create_access_token, verify_token
from modules.rbac.auth import DEMO_USERS

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    """Login request body."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    """Authenticate user and return JWT access token."""
    user = authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": user.username, "role": user.role.value})
    return LoginResponse(
        access_token=token,
        role=user.role.value,
        username=user.username,
    )


@router.post("/me")
async def get_me(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> dict:
    """Return current user information from JWT token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token_data = verify_token(credentials.credentials)
    user = DEMO_USERS.get(token_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }
