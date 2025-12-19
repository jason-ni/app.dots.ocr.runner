"""
Custom exceptions for DotsOCR client.
"""


class DotsOCRRunnerClientError(Exception):
    """Base exception for DotsOCR client."""
    pass


class AuthenticationError(DotsOCRRunnerClientError):
    """Authentication failed."""
    pass


class FileNotFoundError(DotsOCRRunnerClientError):
    """File not found or invalid."""
    pass


class TaskNotFoundError(DotsOCRRunnerClientError):
    """Task not found."""
    pass


class APIError(DotsOCRRunnerClientError):
    """General API error."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class FileUploadError(DotsOCRRunnerClientError):
    """File upload failed."""
    pass


class InvalidFileTypeError(DotsOCRRunnerClientError):
    """Invalid file type provided."""
    pass


class FileTooLargeError(DotsOCRRunnerClientError):
    """File size exceeds limit."""
    pass


class TaskCreationError(DotsOCRRunnerClientError):
    """Failed to create task."""
    pass


class ConnectionError(DotsOCRRunnerClientError):
    """Connection to server failed."""
    pass


class TimeoutError(DotsOCRRunnerClientError):
    """Request timed out."""
    pass


class TaskNotCompletedError(DotsOCRRunnerClientError):
    """Task is not completed and cannot be deleted."""
    pass
