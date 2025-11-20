"""Middleware for request processing, logging, and error handling."""
import time
import traceback
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse


async def logging_middleware(request: Request, call_next: Callable):
    """
    Log incoming requests and responses.

    Args:
        request: FastAPI request
        call_next: Next middleware or route handler

    Returns:
        Response
    """
    start_time = time.time()

    # Log request
    print(f"→ {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    print(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")

    return response


async def error_handling_middleware(request: Request, call_next: Callable):
    """
    Handle errors and exceptions globally.

    Args:
        request: FastAPI request
        call_next: Next middleware or route handler

    Returns:
        Response or error response
    """
    try:
        response = await call_next(request)
        return response

    except ValueError as e:
        # Client errors (400)
        print(f"❌ ValueError: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid request",
                "detail": str(e)
            }
        )

    except FileNotFoundError as e:
        # Not found errors (404)
        print(f"❌ FileNotFoundError: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Resource not found",
                "detail": str(e)
            }
        )

    except Exception as e:
        # Server errors (500)
        print(f"❌ Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later."
            }
        )


def validate_file_size(file_size: int, max_size_mb: int = 10) -> None:
    """
    Validate file size.

    Args:
        file_size: Size of file in bytes
        max_size_mb: Maximum allowed size in MB

    Raises:
        ValueError: If file is too large
    """
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise ValueError(f"File size exceeds maximum allowed size of {max_size_mb}MB")


def validate_file_extension(filename: str, allowed_extensions: list = None) -> None:
    """
    Validate file extension.

    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.txt', '.pdf', '.docx'])

    Raises:
        ValueError: If file extension is not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = ['.txt', '.pdf', '.docx', '.doc']

    from pathlib import Path
    file_extension = Path(filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise ValueError(
            f"File type '{file_extension}' is not supported. "
            f"Allowed types: {', '.join(allowed_extensions)}"
        )
