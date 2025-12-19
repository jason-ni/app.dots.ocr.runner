"""
Data models and response types for DotsOCR client.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FileType(Enum):
    """File type enumeration."""
    PDF = "pdf"
    BATCH_IMAGES = "batch_images"


@dataclass
class UploadResponse:
    """Response from file upload endpoint."""
    task_id: str
    status: str
    file_type: str
    filename: str
    estimated_duration: str


@dataclass
class TaskStatusResponse:
    """Response from task status endpoint."""
    task_id: str
    status: str
    progress: float
    filename: str


@dataclass
class PDFPageResult:
    """Result for a single PDF page."""
    page_num: int
    has_result: bool
    content: str


@dataclass
class PDFResult:
    """Detailed result for PDF OCR task."""
    type: str
    page_count: int
    file_name: str
    dpi: int
    pages: List[PDFPageResult]


@dataclass
class ImageResult:
    """Result for a single image in batch."""
    id: int
    file_name: str
    state: str
    width: int
    height: int
    has_result: bool
    content: str


@dataclass
class BatchImagesResult:
    """Detailed result for batch images OCR task."""
    type: str
    image_count: int
    content_hash: str
    images: List[ImageResult]


@dataclass
class TaskMetadata:
    """Metadata for OCR task."""
    task_id: str
    task_type: str
    status: str
    created_at: str
    updated_at: str
    processing_time_seconds: int
    processing_time: str
    file_name: Optional[str] = None
    content_hash: Optional[str] = None
    page_count: Optional[int] = None
    image_count: Optional[int] = None


@dataclass
class OCRResult:
    """OCR result from completed task."""
    task_id: str
    status: str
    result: Dict[str, Any]
    metadata: Dict[str, Any]
    
    @property
    def pdf_result(self) -> Optional[PDFResult]:
        """Get PDF-specific result if available."""
        if self.result.get('type') == 'pdf':
            return PDFResult(
                type=self.result['type'],
                page_count=self.result['page_count'],
                file_name=self.result['file_name'],
                dpi=self.result['dpi'],
                pages=[PDFPageResult(**page) for page in self.result['pages']]
            )
        return None
    
    @property
    def batch_images_result(self) -> Optional[BatchImagesResult]:
        """Get batch images-specific result if available."""
        if self.result.get('type') == 'batch_images':
            return BatchImagesResult(
                type=self.result['type'],
                image_count=self.result['image_count'],
                content_hash=self.result['content_hash'],
                images=[ImageResult(**image) for image in self.result['images']]
            )
        return None
    
    @property
    def task_metadata(self) -> TaskMetadata:
        """Get structured task metadata."""
        return TaskMetadata(**self.metadata)
    
    def get_all_text(self) -> str:
        """Extract all text content from result."""
        if self.pdf_result:
            return '\n\n'.join(page.content for page in self.pdf_result.pages if page.has_result)
        elif self.batch_images_result:
            return '\n\n'.join(image.content for image in self.batch_images_result.images if image.has_result)
        return ""
    
    def get_text_by_page(self, page_num: int) -> Optional[str]:
        """Get text content for a specific PDF page."""
        if self.pdf_result:
            for page in self.pdf_result.pages:
                if page.page_num == page_num and page.has_result:
                    return page.content
        return None
    
    def get_text_by_image(self, image_id: int) -> Optional[str]:
        """Get text content for a specific image by ID."""
        if self.batch_images_result:
            for image in self.batch_images_result.images:
                if image.id == image_id and image.has_result:
                    return image.content
        return None


@dataclass
class DeleteResponse:
    """Response from task deletion endpoint."""
    task_id: str
    status: str


@dataclass
class HealthResponse:
    """Response from health check endpoint."""
    status: str
    timestamp: str
    version: str


@dataclass
class TaskInfo:
    """Basic task information from list endpoint."""
    task_id: str
    task_type: str
    status: str
    filename: str
    created_at: str
    updated_at: str
    progress: float


@dataclass
class TasksListResponse:
    """Response from tasks list endpoint."""
    tasks: List[TaskInfo]
    total_count: int


# Document API Models

class DocumentType(Enum):
    """Document type enumeration."""
    PDF = "pdf"
    IMAGES = "images"


class ProcessingStatus(Enum):
    """Processing status enumeration."""
    INIT = "init"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class SortField(Enum):
    """Sort field enumeration."""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    NAME = "name"
    STATUS = "status"


class SortOrder(Enum):
    """Sort order enumeration."""
    ASC = "asc"
    DESC = "desc"


class SearchScope(Enum):
    """Search scope enumeration."""
    FILENAMES = "filenames"
    CONTENT = "content"
    BOTH = "both"


class ExportFormat(Enum):
    """Export format enumeration."""
    JSON = "json"
    CSV = "csv"
    TXT = "txt"
    MARKDOWN = "markdown"


class MarkdownExportMode(Enum):
    """Markdown export mode enumeration."""
    EMBEDDED = "embedded"
    SEPARATED = "separated"


@dataclass
class MarkdownExportRequest:
    """Request for markdown export."""
    content_hash: str
    document_type: str  # "pdf" or "images"
    file_name: Optional[str] = None  # Required for PDF, optional for images
    mode: Optional[str] = None  # "embedded" (default) or "separated"
    page_range: Optional[str] = None  # For PDF: "1-5,7,9-10"
    image_range: Optional[str] = None  # For images: "1-5,7,9-10"


@dataclass
class MarkdownExportResponse:
    """Response from markdown export endpoint."""
    success: bool
    mode: str
    text: str
    content_type: str
    generated_at: str
    clips: Optional[List[str]] = None  # Base64 image data
    image_names: Optional[List[str]] = None  # Corresponding image names


@dataclass
class DocumentSpecificMeta:
    """Type-specific document metadata."""
    # PDF specific
    page_count: Optional[int] = None
    completed_pages: Optional[int] = None
    file_size: Optional[int] = None
    # Images specific
    image_count: Optional[int] = None
    completed_images: Optional[int] = None
    # Common
    completion_rate: Optional[float] = None


@dataclass
class DocumentMetadata:
    """Document metadata."""
    id: str
    type: str
    name: str
    status: str
    created_at: str
    updated_at: str
    ocr_engine: str
    metadata: DocumentSpecificMeta


@dataclass
class PaginationInfo:
    """Pagination information."""
    page: int
    page_size: int
    total_count: int
    total_pages: int


@dataclass
class DocumentListResponse:
    """Response from document list endpoint."""
    documents: List[DocumentMetadata]
    pagination: PaginationInfo


@dataclass
class PageContent:
    """Content for a single PDF page."""
    page_num: int
    has_result: bool
    content: Optional[str] = None


@dataclass
class ImageContent:
    """Content for a single image in batch."""
    id: int
    file_name: str
    has_result: bool
    content: Optional[str] = None


@dataclass
class DocumentContent:
    """Document content (pages or images)."""
    # PDF specific
    pages: Optional[List[PageContent]] = None
    # Images specific
    images: Optional[List[ImageContent]] = None


@dataclass
class DocumentDetailsResponse:
    """Response from document details endpoint."""
    base: DocumentMetadata
    content: DocumentContent


@dataclass
class DeleteDocumentResponse:
    """Response from document deletion endpoint."""
    id: str
    status: str
    message: str


@dataclass
class ExportResponse:
    """Response from document export endpoint."""
    content: bytes
    content_type: str
    filename: str
