from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Role(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    AGENT = "agent"


class Permission(str, Enum):
    """Granular permissions for RBAC."""
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    RUN_AGENT = "run_agent"
    VIEW_KPI = "view_kpi"
    MANAGE_USERS = "manage_users"
    INGEST_DOCUMENTS = "ingest_documents"


class User(BaseModel):
    """User model with role-based access control."""
    username: str
    email: str
    role: Role
    hashed_password: str
    is_active: bool = True


class TokenData(BaseModel):
    """JWT token payload data."""
    username: str
    role: Role
    exp: Optional[int] = None
