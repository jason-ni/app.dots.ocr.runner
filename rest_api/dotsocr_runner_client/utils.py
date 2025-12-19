"""
Utility functions for DotsOCR client.
"""

import os
import mimetypes
from typing import List, Optional
from pathlib import Path


def validate_file_exists(file_path: str) -> Path:
    """
    Validate that a file exists and return Path object.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Path object for the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise FileNotFoundError(f"Path is not a file: {file_path}")
    return path


def validate_pdf_file(file_path: str) -> Path:
    """
    Validate that a file is a PDF file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Path object for the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidFileTypeError: If file is not a PDF
    """
    path = validate_file_exists(file_path)
    
    # Check file extension
    if path.suffix.lower() != '.pdf':
        from .exceptions import InvalidFileTypeError
        raise InvalidFileTypeError(f"File is not a PDF: {file_path}")
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type != 'application/pdf':
        from .exceptions import InvalidFileTypeError
        raise InvalidFileTypeError(f"File MIME type is not PDF: {file_path}")
    
    # Check PDF magic number
    try:
        with open(path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                from .exceptions import InvalidFileTypeError
                raise InvalidFileTypeError(f"File does not have PDF header: {file_path}")
    except Exception as e:
        from .exceptions import FileNotFoundError
        raise FileNotFoundError(f"Could not read file: {file_path}") from e
    
    return path


def validate_image_files(file_paths: List[str]) -> List[Path]:
    """
    Validate that all files are valid image files.
    
    Args:
        file_paths: List of file paths
        
    Returns:
        List of Path objects for valid files
        
    Raises:
        FileNotFoundError: If any file doesn't exist
        InvalidFileTypeError: If any file is not a valid image
    """
    valid_paths = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    valid_mime_types = {'image/jpeg', 'image/png', 'image/webp'}
    
    for file_path in file_paths:
        path = validate_file_exists(file_path)
        
        # Check file extension
        if path.suffix.lower() not in valid_extensions:
            from .exceptions import InvalidFileTypeError
            raise InvalidFileTypeError(f"File is not a valid image type: {file_path}")
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type not in valid_mime_types:
            from .exceptions import InvalidFileTypeError
            raise InvalidFileTypeError(f"File MIME type is not a valid image: {file_path}")
        
        # Check image magic numbers
        try:
            with open(path, 'rb') as f:
                header = f.read(12)
                if not is_valid_image_header(header):
                    from .exceptions import InvalidFileTypeError
                    raise InvalidFileTypeError(f"File does not have valid image header: {file_path}")
        except Exception as e:
            from .exceptions import FileNotFoundError
            raise FileNotFoundError(f"Could not read file: {file_path}") from e
        
        valid_paths.append(path)
    
    return valid_paths


def is_valid_image_header(header: bytes) -> bool:
    """
    Check if header bytes indicate a valid image format.
    
    Args:
        header: First bytes of the file
        
    Returns:
        True if valid image format, False otherwise
    """
    if len(header) < 4:
        return False
    
    # JPEG
    if header[:2] == b'\xFF\xD8':
        return True
    
    # PNG
    if len(header) >= 8 and header[:8] == b'\x89PNG\r\n\x1A\n':
        return True
    
    # WebP
    if len(header) >= 12 and header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return True
    
    return False


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    path = Path(file_path)
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def extract_filename_from_path(file_path: str) -> str:
    """
    Extract and sanitize filename from file path.
    
    Args:
        file_path: File path
        
    Returns:
        Sanitized filename
    """
    return sanitize_filename(file_path)


def create_progress_callback(callback: Optional[callable] = None):
    """
    Create a progress callback function.
    
    Args:
        callback: Optional callback function
        
    Returns:
        Progress callback function or None
    """
    if callback is None:
        return None
    
    def progress_wrapper(progress: float, message: str = ""):
        try:
            callback(progress, message)
        except Exception:
            # Don't let callback errors break the main flow
            pass
    
    return progress_wrapper
