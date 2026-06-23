from __future__ import annotations
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import verify_token
from .models import Permission, Role, TokenData, User
from .auth import DEMO_USERS

_bearer = HTTPBearer(auto_error=False)

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.RUN_AGENT,
        Permission.VIEW_KPI,
        Permission.MANAGE_USERS,
        Permission.INGEST_DOCUMENTS,
    },
    Role.ANALYST: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.RUN_AGENT,
        Permission.VIEW_KPI,
        Permission.INGEST_DOCUMENTS,
    },
    Role.VIEWER: {
        Permission.READ_DATA,
        Permission.VIEW_KPI,
    },
    Role.AGENT: {
        Permission.READ_DATA,
        Permission.RUN_AGENT,
    },
}


class RBACManager:
    """Manages role-based access control checks."""

    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission based on their role."""
        allowed = ROLE_PERMISSIONS.get(user.role, set())
        return permission in allowed


def require_permission(permission: Permission):
    """FastAPI dependency that enforces a required permission."""

    async def _check(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    ) -> TokenData:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        token_data = verify_token(credentials.credentials)
        # Look up user
        user = DEMO_USERS.get(token_data.username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        manager = RBACManager()
        if not manager.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required",
            )
        return token_data

    return _check
