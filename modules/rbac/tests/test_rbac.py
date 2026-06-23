from __future__ import annotations
import pytest
from datetime import timedelta


class TestModels:
    def test_role_enum_values(self):
        from modules.rbac.models import Role
        assert Role.ADMIN.value == "admin"
        assert Role.ANALYST.value == "analyst"
        assert Role.VIEWER.value == "viewer"
        assert Role.AGENT.value == "agent"

    def test_permission_enum_values(self):
        from modules.rbac.models import Permission
        assert Permission.READ_DATA.value == "read_data"
        assert Permission.MANAGE_USERS.value == "manage_users"

    def test_user_model(self):
        from modules.rbac.models import User, Role
        user = User(
            username="test",
            email="test@test.com",
            role=Role.VIEWER,
            hashed_password="hashed",
        )
        assert user.is_active is True
        assert user.role == Role.VIEWER


class TestAuth:
    def test_create_and_verify_token(self):
        from modules.rbac.auth import create_access_token, verify_token
        token = create_access_token({"sub": "testuser", "role": "analyst"})
        token_data = verify_token(token)
        assert token_data.username == "testuser"
        assert token_data.role.value == "analyst"

    def test_authenticate_admin(self):
        from modules.rbac.auth import authenticate_user
        user = authenticate_user("admin", "admin123")
        assert user is not None
        assert user.username == "admin"
        assert user.role.value == "admin"

    def test_authenticate_analyst(self):
        from modules.rbac.auth import authenticate_user
        user = authenticate_user("analyst", "analyst123")
        assert user is not None

    def test_authenticate_wrong_password(self):
        from modules.rbac.auth import authenticate_user
        user = authenticate_user("admin", "wrongpassword")
        assert user is None

    def test_authenticate_unknown_user(self):
        from modules.rbac.auth import authenticate_user
        user = authenticate_user("nobody", "password")
        assert user is None

    def test_token_with_custom_expiry(self):
        from modules.rbac.auth import create_access_token, verify_token
        token = create_access_token(
            {"sub": "testuser", "role": "viewer"},
            expires_delta=timedelta(hours=1),
        )
        token_data = verify_token(token)
        assert token_data.username == "testuser"


class TestPermissions:
    def test_admin_has_all_permissions(self):
        from modules.rbac.permissions import RBACManager
        from modules.rbac.models import User, Role, Permission
        manager = RBACManager()
        admin = User(username="admin", email="a@a.com", role=Role.ADMIN, hashed_password="x")
        for perm in Permission:
            assert manager.has_permission(admin, perm) is True

    def test_viewer_limited_permissions(self):
        from modules.rbac.permissions import RBACManager
        from modules.rbac.models import User, Role, Permission
        manager = RBACManager()
        viewer = User(username="viewer", email="v@v.com", role=Role.VIEWER, hashed_password="x")
        assert manager.has_permission(viewer, Permission.READ_DATA) is True
        assert manager.has_permission(viewer, Permission.VIEW_KPI) is True
        assert manager.has_permission(viewer, Permission.RUN_AGENT) is False
        assert manager.has_permission(viewer, Permission.MANAGE_USERS) is False

    def test_analyst_can_run_agents(self):
        from modules.rbac.permissions import RBACManager
        from modules.rbac.models import User, Role, Permission
        manager = RBACManager()
        analyst = User(username="analyst", email="an@an.com", role=Role.ANALYST, hashed_password="x")
        assert manager.has_permission(analyst, Permission.RUN_AGENT) is True
        assert manager.has_permission(analyst, Permission.MANAGE_USERS) is False
