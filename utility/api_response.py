"""HTTP exception method."""

from fastapi import HTTPException


def http_exception(message, status, headers=None) -> HTTPException:
    """Error message.py."""
    return HTTPException(
        status_code=status,
        detail=message,
        headers=headers
    )
