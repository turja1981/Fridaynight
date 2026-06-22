from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .models import Role, TokenData, User

_pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

ALGORITHM = "HS256"
DEFAULT_EXPIRE_HOURS = 24

# Demo users — passwords are bcrypt hashed at module load
DEMO_USERS: dict[str, User] = {
    "admin": User(
        username="admin",
        email="admin@enterprise.ai",
        role=Role.ADMIN,
        hashed_password=_pwd_context.hash("admin123"),
        is_active=True,
    ),
    "analyst": User(
        username="analyst",
        email="analyst@enterprise.ai",
        role=Role.ANALYST,
        hashed_password=_pwd_context.hash("analyst123"),
        is_active=True,
    ),
    "viewer": User(
        username="viewer",
        email="viewer@enterprise.ai",
        role=Role.VIEWER,
        hashed_password=_pwd_context.hash("viewer123"),
        is_active=True,
    ),
}


def _get_secret() -> str:
    return os.environ.get("JWT_SECRET", "dev-secret-change-in-prod")


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(hours=DEFAULT_EXPIRE_HOURS),
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    return jwt.encode(to_encode, _get_secret(), algorithm=ALGORITHM)


def verify_token(token: str) -> TokenData:
    """Verify JWT token and return TokenData."""
    payload = jwt.decode(token, _get_secret(), algorithms=[ALGORITHM])
    username: str = payload.get("sub", "")
    role_str: str = payload.get("role", Role.VIEWER.value)
    exp: int = payload.get("exp", 0)
    if not username:
        raise JWTError("Missing subject in token")
    return TokenData(username=username, role=Role(role_str), exp=exp)


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user credentials and return User if valid."""
    user = DEMO_USERS.get(username)
    if not user:
        return None
    if not _pwd_context.verify(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
