from __future__ import annotations
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class AuthException(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "AUTH_ERROR", 401)

class PermissionException(AppException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "PERMISSION_DENIED", 403)

class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", "NOT_FOUND", 404)

def handle_exception(exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.code, "message": exc.message})
    return JSONResponse(status_code=500, content={"error": "INTERNAL_ERROR", "message": str(exc)})
