"""Document upload storage using file system."""
import uuid
from pathlib import Path
from typing import Optional


# Storage directory for uploads
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "storage" / "uploads"


def _ensure_upload_dir():
    """Ensure upload directory exists."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file_content: bytes, filename: str) -> str:
    """
    Save an uploaded file.

    Args:
        file_content: File content as bytes
        filename: Original filename

    Returns:
        file_id: Unique identifier for the uploaded file
    """
    _ensure_upload_dir()

    # Generate unique ID
    file_id = str(uuid.uuid4())

    # Extract file extension
    file_extension = Path(filename).suffix
    file_path = UPLOAD_DIR / f"{file_id}{file_extension}"

    # Save file
    file_path.write_bytes(file_content)

    return file_id


def get_upload(file_id: str) -> Optional[bytes]:
    """
    Retrieve an uploaded file.

    Args:
        file_id: File identifier (may include extension)

    Returns:
        File content as bytes or None if not found
    """
    # Try with the file_id as is first
    file_path = UPLOAD_DIR / file_id

    if file_path.exists() and file_path.is_file():
        return file_path.read_bytes()

    # Try to find file with any extension
    for path in UPLOAD_DIR.glob(f"{file_id}.*"):
        if path.is_file():
            return path.read_bytes()

    return None


def delete_upload(file_id: str) -> bool:
    """
    Delete an uploaded file.

    Args:
        file_id: File identifier

    Returns:
        True if successful, False otherwise
    """
    # Try to find and delete the file
    file_path = UPLOAD_DIR / file_id

    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
            return True
        except OSError:
            return False

    # Try to find file with any extension
    for path in UPLOAD_DIR.glob(f"{file_id}.*"):
        if path.is_file():
            try:
                path.unlink()
                return True
            except OSError:
                return False

    return False


def cleanup_old_uploads(max_age_hours: int = 24):
    """
    Clean up old uploaded files.

    Args:
        max_age_hours: Maximum age of files to keep in hours
    """
    import time

    _ensure_upload_dir()

    current_time = time.time()
    max_age_seconds = max_age_hours * 3600

    for file_path in UPLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue

        file_age = current_time - file_path.stat().st_mtime

        if file_age > max_age_seconds:
            try:
                file_path.unlink()
                print(f"Deleted old upload: {file_path.name}")
            except OSError as e:
                print(f"Error deleting {file_path.name}: {e}")
