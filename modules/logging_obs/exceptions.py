from __future__ import annotations

from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception with HTTP status code."""

    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class AuthException(AppException):
    """Authentication failure exception."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, code="AUTH_ERROR", status_code=401)


class PermissionException(AppException):
    """Permission denied exception."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, code="PERMISSION_DENIED", status_code=403)


class NotFoundError(AppException):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="NOT_FOUND", status_code=404)


class ValidationError(AppException):
    """Input validation exception."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422)


def handle_exception(exc: Exception) -> JSONResponse:
    """Convert exceptions to JSON responses."""
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "message": exc.message},
        )
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": str(exc)},
    )
