from fastapi import HTTPException
from typing import Dict, Any, Optional

class MegapolisHTTPException(HTTPException):
    """Custom HTTP exception for Megapolis API with structured error responses."""

    def __init__(
        self,
        status_code: int,
        message: str = None,
        details: str = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize PipecatHTTPException.

        Args:
            status_code: HTTP status code.
            message: Error message. If not provided, uses default for status code.
            details: Additional error details.
            metadata: Optional metadata dictionary for additional error context.
        """
        self.status_code = status_code
        self.message = message or self._get_default_message(status_code)
        self.details = details or {}
        self.metadata = metadata or {}

        content = {
            "error": {
                "code": status_code,
                "message": self.message,
                "details": details,
            }
        }

        if metadata:
            content["error"]["metadata"] = metadata

        super().__init__(status_code=status_code, detail=content)

    @staticmethod
    def _get_default_message(status_code: int) -> str:
        """Get default message based on status code."""
        return {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
        }.get(status_code, "Unknown Error")

