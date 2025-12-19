"""
DotsOCRRunner Python Client Library

A comprehensive Python client for the DotsOCR REST API, supporting both synchronous
and asynchronous operations.

Basic Usage:
    from dotsocr_runner_client import DotsOCRRunnerClient
    
    # Synchronous usage
    with DotsOCRRunnerClient("http://localhost:8080", "your-token") as client:
        # Upload PDF
        upload_response = client.upload_pdf("document.pdf")
        
        # Wait for completion
        result = client.wait_for_completion(upload_response.task_id)
        
        # Extract text from PDF result
        if result.result.get('type') == 'pdf':
            pages = result.result.get('pages', [])
            for page in pages:
                if page.get('has_result'):
                    content = page.get('content', '')
                    print(f"Page {page.get('page_num')}: {content}")

Async Usage:
    from dotsocr_runner_client import AsyncDotsOCRRunnerClient
    
    async def process_document():
        async with AsyncDotsOCRRunnerClient("http://localhost:8080", "your-token") as client:
            # Upload images
            upload_response = await client.upload_images(["img1.jpg", "img2.png"])
            
            # Wait for completion
            result = await client.wait_for_completion(upload_response.task_id)
            
            # Extract text from batch images result
            if result.result.get('type') == 'batch_images':
                images = result.result.get('images', [])
                for image in images:
                    if image.get('has_result'):
                        content = image.get('content', '')
                        print(f"Image {image.get('id')}: {content}")
"""

__version__ = "1.0.0"
__author__ = "DotsOCR Team"
__email__ = "support@dotsocr.com"

# Import main classes and functions
from .client import DotsOCRRunnerClient
from .async_client import AsyncDotsOCRRunnerClient, create_async_client

# Import models
from .models import (
    UploadResponse,
    TaskStatusResponse,
    OCRResult,
    DeleteResponse,
    HealthResponse,
    TaskInfo,
    TasksListResponse,
    TaskStatus,
    FileType,
    # Document API models
    DocumentMetadata,
    DocumentListResponse,
    DocumentDetailsResponse,
    DeleteDocumentResponse,
    ExportResponse,
    PaginationInfo,
    DocumentContent,
    PageContent,
    ImageContent,
    DocumentSpecificMeta,
    DocumentType,
    ProcessingStatus,
    SortField,
    SortOrder,
    SearchScope,
    ExportFormat,
    MarkdownExportMode,
    MarkdownExportRequest,
    MarkdownExportResponse
)

# Import exceptions
from .exceptions import (
    DotsOCRRunnerClientError,
    AuthenticationError,
    FileNotFoundError,
    TaskNotFoundError,
    APIError,
    FileUploadError,
    InvalidFileTypeError,
    FileTooLargeError,
    TaskCreationError,
    ConnectionError,
    TimeoutError,
    TaskNotCompletedError
)

# Import utilities
from .utils import (
    validate_file_exists,
    validate_pdf_file,
    validate_image_files,
    get_file_size_mb,
    format_file_size,
    sanitize_filename,
    extract_filename_from_path,
    create_progress_callback
)

# Define what gets imported with "from dotsocr_runner_client import *"
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Main classes
    "DotsOCRRunnerClient",
    "AsyncDotsOCRRunnerClient",
    "create_async_client",
    
    # Models
    "UploadResponse",
    "TaskStatusResponse",
    "OCRResult",
    "DeleteResponse",
    "HealthResponse",
    "TaskInfo",
    "TasksListResponse",
    "TaskStatus",
    "FileType",
    # Document API models
    "DocumentMetadata",
    "DocumentListResponse",
    "DocumentDetailsResponse",
    "DeleteDocumentResponse",
    "ExportResponse",
    "PaginationInfo",
    "DocumentContent",
    "PageContent",
    "ImageContent",
    "DocumentSpecificMeta",
    "DocumentType",
    "ProcessingStatus",
    "SortField",
    "SortOrder",
    "SearchScope",
    "ExportFormat",
    "MarkdownExportMode",
    "MarkdownExportRequest",
    "MarkdownExportResponse",
    
    # Exceptions
    "DotsOCRRunnerClientError",
    "AuthenticationError",
    "FileNotFoundError",
    "TaskNotFoundError",
    "APIError",
    "FileUploadError",
    "InvalidFileTypeError",
    "FileTooLargeError",
    "TaskCreationError",
    "ConnectionError",
    "TimeoutError",
    "TaskNotCompletedError",
    
    # Utilities
    "validate_file_exists",
    "validate_pdf_file",
    "validate_image_files",
    "get_file_size_mb",
    "format_file_size",
    "sanitize_filename",
    "extract_filename_from_path",
    "create_progress_callback"
]

# Set up logging
import logging

# Create logger for this module
logger = logging.getLogger(__name__)

# Add null handler to prevent "No handler found" warnings
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

# Convenience function for quick setup
def setup_logging(level: str = "INFO"):
    """
    Set up logging for DotsOCR client.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
