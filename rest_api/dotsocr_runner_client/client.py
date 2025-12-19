"""
Synchronous DotsOCR client implementation.
"""

import json
import time
import requests
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

from .models import (
    UploadResponse, TaskStatusResponse, OCRResult, DeleteResponse,
    HealthResponse, TaskInfo, TasksListResponse,
    # Document API models
    DocumentMetadata, DocumentListResponse, DocumentDetailsResponse,
    DeleteDocumentResponse, ExportResponse, PaginationInfo,
    DocumentContent, PageContent, ImageContent, DocumentSpecificMeta,
    DocumentType, ProcessingStatus, SortField, SortOrder, SearchScope, ExportFormat,
    MarkdownExportMode, MarkdownExportRequest, MarkdownExportResponse
)
from .exceptions import (
    DotsOCRRunnerClientError, AuthenticationError, TaskNotFoundError,
    APIError, FileUploadError, ConnectionError, TimeoutError,
    TaskNotCompletedError
)
from .utils import (
    validate_pdf_file, validate_image_files, extract_filename_from_path,
    create_progress_callback
)


class DotsOCRRunnerClient:
    """
    Synchronous client for DotsOCR REST API.
    
    Provides methods for uploading files, checking task status, retrieving results,
    and managing OCR tasks.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080", 
                 auth_token: str = None, timeout: float = 30.0):
        """
        Initialize the DotsOCR client.
        
        Args:
            base_url: Base URL of the DotsOCR server
            auth_token: Authentication token for API access
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'DotsOCR-Python-Client/1.0.0'
        })
        
        if self.auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}'
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response object
            
        Raises:
            ConnectionError: If connection fails
            TimeoutError: If request times out
            AuthenticationError: If authentication fails
            APIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            
            # Handle other HTTP errors
            if not response.ok:
                try:
                    error_data = response.json()
                    message = error_data.get('error', {}).get('message', response.text)
                except (ValueError, KeyError):
                    message = response.text
                
                raise APIError(
                    f"API request failed: {message}",
                    status_code=response.status_code
                )
            
            return response
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to server: {e}") from e
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out: {e}") from e
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}") from e
    
    def upload_pdf(self, pdf_path: str, dpi: Optional[int] = None) -> UploadResponse:
        """
        Upload PDF file for OCR processing.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Optional DPI for processing (default: 150 for PDFs, 72 for images)
            
        Returns:
            UploadResponse with task information
            
        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidFileTypeError: If file is not a valid PDF
            FileUploadError: If upload fails
        """
        # Validate file
        pdf_path_obj = validate_pdf_file(pdf_path)
        filename = extract_filename_from_path(pdf_path)
        
        try:
            with open(pdf_path_obj, 'rb') as f:
                files = {'file': (filename, f, 'application/pdf')}
                data = {}
                
                # Add DPI parameter if provided
                if dpi is not None:
                    if not (72 <= dpi <= 200):
                        raise ValueError("DPI must be between 72 and 200")
                    data['dpi'] = dpi
                
                response = self._make_request('POST', '/api/v1/ocr/pdf/upload', files=files, data=data)
                response_data = response.json()
                
                return UploadResponse(
                    task_id=response_data['task_id'],
                    status=response_data['status'],
                    file_type=response_data['file_type'],
                    filename=response_data['filename'],
                    estimated_duration=response_data['estimated_duration']
                )
                
        except IOError as e:
            raise FileUploadError(f"Failed to read PDF file: {e}") from e
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def upload_images(self, image_paths: List[str], dpi: Optional[int] = None) -> UploadResponse:
        """
        Upload multiple images for batch OCR processing.
        
        Args:
            image_paths: List of paths to image files
            dpi: Optional DPI for processing (default: 150 for PDFs, 72 for images)
            
        Returns:
            UploadResponse with task information
            
        Raises:
            FileNotFoundError: If any file doesn't exist
            InvalidFileTypeError: If any file is not a valid image
            FileUploadError: If upload fails
        """
        # Validate files
        image_path_objs = validate_image_files(image_paths)
        
        try:
            files = []
            for i, path_obj in enumerate(image_path_objs):
                filename = extract_filename_from_path(str(path_obj))
                mime_type = f"image/{path_obj.suffix.lower().lstrip('.')}"
                
                with open(path_obj, 'rb') as f:
                    file_data = f.read()
                
                files.append(('files', (filename, file_data, mime_type)))
            
            data = {}
            # Add DPI parameter if provided
            if dpi is not None:
                if not (72 <= dpi <= 200):
                    raise ValueError("DPI must be between 72 and 200")
                data['dpi'] = dpi
            
            response = self._make_request('POST', '/api/v1/ocr/images/upload', files=files, data=data)
            response_data = response.json()
            
            return UploadResponse(
                task_id=response_data['task_id'],
                status=response_data['status'],
                file_type=response_data['file_type'],
                filename=response_data['filename'],
                estimated_duration=response_data['estimated_duration']
            )
            
        except IOError as e:
            raise FileUploadError(f"Failed to read image files: {e}") from e
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def get_task_status(self, task_id: str) -> TaskStatusResponse:
        """
        Get current status of OCR task.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskStatusResponse with current status
            
        Raises:
            TaskNotFoundError: If task doesn't exist
            APIError: For other API errors
        """
        response = self._make_request('GET', f'/api/v1/ocr/status/{task_id}')
        data = response.json()
        
        try:
            return TaskStatusResponse(
                task_id=data['task_id'],
                status=data['status'],
                progress=data['progress'],
                filename=data.get('filename', '')
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def get_task_result(self, task_id: str) -> OCRResult:
        """
        Get OCR results when task is completed.
        
        Args:
            task_id: Task ID
            
        Returns:
            OCRResult with processed content
            
        Raises:
            TaskNotFoundError: If task doesn't exist
            APIError: For other API errors
        """
        response = self._make_request('GET', f'/api/v1/ocr/result/{task_id}')
        data = response.json()
        
        try:
            return OCRResult(
                task_id=data['task_id'],
                status=data['status'],
                result=data['result'],
                metadata=data['metadata']
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def wait_for_completion(self, task_id: str, poll_interval: float = 2.0,
                          progress_callback: Optional[Callable[[float, str], None]] = None) -> OCRResult:
        """
        Wait for task completion and return results.
        
        Args:
            task_id: Task ID
            poll_interval: Polling interval in seconds
            progress_callback: Optional callback for progress updates
            
        Returns:
            OCRResult with processed content
            
        Raises:
            TaskNotFoundError: If task doesn't exist
            TimeoutError: If task takes too long
            APIError: For other API errors
        """
        callback = create_progress_callback(progress_callback)
        
        while True:
            try:
                status = self.get_task_status(task_id)
                
                # Call progress callback if provided
                if callback:
                    callback(status.progress, status.status)
                
                # Check if task is completed
                if status.status == 'completed':
                    return self.get_task_result(task_id)
                elif status.status == 'failed':
                    raise APIError(f"Task failed with status: {status.status}")
                
                # Wait before next poll
                time.sleep(poll_interval)
                
            except TaskNotFoundError:
                raise
            except APIError as e:
                print(f"==== apierror: {e}")
                if "Task failed" in str(e):
                    raise
                # For other API errors, continue polling
                time.sleep(poll_interval)
    
    def delete_task(self, task_id: str) -> DeleteResponse:
        """
        Delete task and clean up resources.
        
        Args:
            task_id: Task ID
            
        Returns:
            DeleteResponse with deletion status
            
        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskNotCompletedError: If task is not completed
            APIError: For other API errors
        """
        # First check task status to ensure it's completed
        task_status = self.get_task_status(task_id)
        
        if task_status.status != 'completed':
            raise TaskNotCompletedError(
                f"Task '{task_id}' cannot be deleted. Only completed tasks can be deleted. "
                f"Current status: '{task_status.status}'"
            )
        
        response = self._make_request('DELETE', f'/api/v1/ocr/task/{task_id}')
        data = response.json()
        
        try:
            return DeleteResponse(
                task_id=task_id,
                status="deleted"
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def list_tasks(self) -> TasksListResponse:
        """
        List all tasks.
        
        Returns:
            TasksListResponse with task list
            
        Raises:
            APIError: For API errors
        """
        response = self._make_request('GET', '/api/v1/ocr/tasks')
        data = response.json()
        
        try:
            tasks = []
            for task_data in data['tasks']:
                task = TaskInfo(
                    task_id=task_data['task_id'],
                    task_type=task_data['task_type'],
                    status=task_data['status'],
                    filename=task_data['filename'],
                    created_at=task_data['created_at'],
                    updated_at=task_data.get('updated_at', task_data['created_at']),
                    progress=task_data['progress']
                )
                tasks.append(task)
            
            return TasksListResponse(
                tasks=tasks,
                total_count=data['total_count']
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def health_check(self) -> HealthResponse:
        """
        Check API health status.
        
        Returns:
            HealthResponse with server status
            
        Raises:
            APIError: For API errors
        """
        response = self._make_request('GET', '/api/v1/health')
        data = response.json()
        
        try:
            return HealthResponse(
                status=data['status'],
                timestamp=data['timestamp'],
                version=data['version']
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    # Document API Methods
    
    def list_documents(self, page: int = 1, page_size: int = 10, 
                      document_type: Optional[DocumentType] = None,
                      status: Optional[ProcessingStatus] = None,
                      date_start: Optional[str] = None,
                      date_end: Optional[str] = None,
                      sort_by: SortField = SortField.UPDATED_AT,
                      sort_order: SortOrder = SortOrder.DESC) -> DocumentListResponse:
        """
        List documents with pagination and filtering.
        
        Args:
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 10, max: 100)
            document_type: Filter by document type
            status: Filter by processing status
            date_start: Filter by creation date (ISO 8601 format)
            date_end: Filter by creation date (ISO 8601 format)
            sort_by: Sort field (default: updated_at)
            sort_order: Sort direction (default: desc)
            
        Returns:
            DocumentListResponse with document list and pagination info
            
        Raises:
            APIError: For API errors
        """
        params = {
            'page': page,
            'page_size': min(page_size, 100),  # Enforce max limit
            'sort_by': sort_by.value,
            'sort_order': sort_order.value
        }
        
        if document_type:
            params['type'] = document_type.value
        if status:
            params['status'] = status.value
        if date_start:
            params['date_start'] = date_start
        if date_end:
            params['date_end'] = date_end
        
        response = self._make_request('GET', '/api/v1/documents', params=params)
        data = response.json()
        
        try:
            documents = []
            for doc_data in data['documents']:
                # Parse metadata based on document type
                metadata = doc_data['metadata']
                doc_specific_meta = DocumentSpecificMeta(
                    page_count=metadata.get('page_count'),
                    completed_pages=metadata.get('completed_pages'),
                    file_size=metadata.get('file_size'),
                    image_count=metadata.get('image_count'),
                    completed_images=metadata.get('completed_images'),
                    completion_rate=metadata.get('completion_rate')
                )
                
                document = DocumentMetadata(
                    id=doc_data['id'],
                    type=doc_data['type'],
                    name=doc_data['name'],
                    status=doc_data['status'],
                    created_at=doc_data['created_at'],
                    updated_at=doc_data['updated_at'],
                    ocr_engine=doc_data['ocr_engine'],
                    metadata=doc_specific_meta
                )
                documents.append(document)
            
            pagination_data = data['pagination']
            pagination = PaginationInfo(
                page=pagination_data['page'],
                page_size=pagination_data['page_size'],
                total_count=pagination_data['total_count'],
                total_pages=pagination_data['total_pages']
            )
            
            return DocumentListResponse(
                documents=documents,
                pagination=pagination
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def search_documents(self, query: str, scope: SearchScope = SearchScope.FILENAMES,
                        page: int = 1, page_size: int = 10) -> DocumentListResponse:
        """
        Search documents across filenames and OCR content.
        
        Args:
            query: Search query string
            scope: Search scope (filenames, content, or both)
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 10, max: 100)
            
        Returns:
            DocumentListResponse with search results and pagination info
            
        Raises:
            APIError: For API errors
        """
        if len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters long")
        
        params = {
            'q': query.strip(),
            'scope': scope.value,
            'page': page,
            'page_size': min(page_size, 100)  # Enforce max limit
        }
        
        response = self._make_request('GET', '/api/v1/documents/search', params=params)
        data = response.json()
        
        try:
            documents = []
            for doc_data in data['documents']:
                # Parse metadata based on document type
                metadata = doc_data['metadata']
                doc_specific_meta = DocumentSpecificMeta(
                    page_count=metadata.get('page_count'),
                    completed_pages=metadata.get('completed_pages'),
                    file_size=metadata.get('file_size'),
                    image_count=metadata.get('image_count'),
                    completed_images=metadata.get('completed_images'),
                    completion_rate=metadata.get('completion_rate')
                )
                
                document = DocumentMetadata(
                    id=doc_data['id'],
                    type=doc_data['type'],
                    name=doc_data['name'],
                    status=doc_data['status'],
                    created_at=doc_data['created_at'],
                    updated_at=doc_data['updated_at'],
                    ocr_engine=doc_data['ocr_engine'],
                    metadata=doc_specific_meta
                )
                documents.append(document)
            
            pagination_data = data['pagination']
            pagination = PaginationInfo(
                page=pagination_data['page'],
                page_size=pagination_data['page_size'],
                total_count=pagination_data['total_count'],
                total_pages=pagination_data['total_pages']
            )
            
            return DocumentListResponse(
                documents=documents,
                pagination=pagination
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def get_document_details(self, document_id: str) -> DocumentDetailsResponse:
        """
        Get detailed information about a specific document.
        
        Args:
            document_id: Document content hash
            
        Returns:
            DocumentDetailsResponse with detailed document information
            
        Raises:
            APIError: For API errors
        """
        response = self._make_request('GET', f'/api/v1/documents/{document_id}')
        data = response.json()
        
        try:
            # Parse of flat response structure from the server
            metadata = data['metadata']
            
            # Handle the enum-based metadata structure
            if isinstance(metadata, dict) and 'Pdf' in metadata:
                pdf_meta = metadata['Pdf']
                doc_specific_meta = DocumentSpecificMeta(
                    page_count=pdf_meta.get('page_count'),
                    completed_pages=pdf_meta.get('completed_pages'),
                    file_size=pdf_meta.get('file_size'),
                    image_count=None,
                    completed_images=None,
                    completion_rate=pdf_meta.get('completion_rate')
                )
            elif isinstance(metadata, dict) and 'Images' in metadata:
                images_meta = metadata['Images']
                doc_specific_meta = DocumentSpecificMeta(
                    page_count=None,
                    completed_pages=None,
                    file_size=None,
                    image_count=images_meta.get('image_count'),
                    completed_images=images_meta.get('completed_images'),
                    completion_rate=images_meta.get('completion_rate')
                )
            else:
                # Fallback for flat metadata structure
                doc_specific_meta = DocumentSpecificMeta(
                    page_count=metadata.get('page_count'),
                    completed_pages=metadata.get('completed_pages'),
                    file_size=metadata.get('file_size'),
                    image_count=metadata.get('image_count'),
                    completed_images=metadata.get('completed_images'),
                    completion_rate=metadata.get('completion_rate')
                )
            
            base = DocumentMetadata(
                id=data['id'],
                type=data['type'],
                name=data['name'],
                status=data['status'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                ocr_engine=data['ocr_engine'],
                metadata=doc_specific_meta
            )
            
            # Parse content based on document type
            content_data = data.get('content', {})
            content = DocumentContent()
            
            if base.type == 'pdf' and isinstance(content_data, dict) and 'pages' in content_data:
                content.pages = []
                for page_data in content_data['pages']:
                    print(f"==== page {page_data}")
                    page = PageContent(
                        page_num=page_data['page_num'],
                        has_result=page_data['has_result'],
                        content=page_data.get('content')
                    )
                    content.pages.append(page)
            elif base.type == 'images' and isinstance(content_data, dict) and 'images' in content_data:
                content.images = []
                for image_data in content_data['images']:
                    image = ImageContent(
                        id=image_data['id'],
                        file_name=image_data['file_name'],
                        has_result=image_data['has_result'],
                        content=image_data.get('content')
                    )
                    content.images.append(image)
            
            return DocumentDetailsResponse(
                base=base,
                content=content
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def delete_document(self, document_id: str) -> DeleteDocumentResponse:
        """
        Delete a document and all associated data.
        
        Args:
            document_id: Document content hash
            
        Returns:
            DeleteDocumentResponse with deletion status
            
        Raises:
            APIError: For API errors
        """
        response = self._make_request('DELETE', f'/api/v1/documents/{document_id}')
        data = response.json()
        
        try:
            return DeleteDocumentResponse(
                id=data['id'],
                status=data['status'],
                message=data['message']
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def export_document(self, document_id: str, export_format: ExportFormat) -> ExportResponse:
        """
        Export document in specified format.
        
        Args:
            document_id: Document content hash
            export_format: Export format (json, csv, txt, markdown)
            
        Returns:
            ExportResponse with file content and metadata
            
        Raises:
            APIError: For API errors
        """
        params = {'format': export_format.value}
        response = self._make_request('GET', f'/api/v1/documents/{document_id}/export', params=params)
        
        # Get filename from Content-Disposition header if available
        filename = f"document.{export_format.value}"
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition and 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"')
        
        return ExportResponse(
            content=response.content,
            content_type=response.headers.get('Content-Type', 'application/octet-stream'),
            filename=filename
        )
    
    def get_document_markdown(self, content_hash: str, document_type: str, file_name: Optional[str] = None,
                           mode: Optional[MarkdownExportMode] = None, page_range: Optional[str] = None,
                           image_range: Optional[str] = None) -> MarkdownExportResponse:
        """
        Get document content as markdown with enhanced export options.
        
        Args:
            content_hash: Document content hash
            document_type: Document type ('pdf' or 'images')
            file_name: File name (required for PDF documents)
            mode: Export mode (embedded or separated, default: embedded)
            page_range: For PDF: page range like "1-5,7,9-10"
            image_range: For images: image range like "1-5,7,9-10"
            
        Returns:
            MarkdownExportResponse with text and optional clips
            
        Raises:
            APIError: For API errors
        """
        # Validate document type
        if document_type not in ['pdf', 'images']:
            raise ValueError("document_type must be 'pdf' or 'images'")
        
        # For PDF documents, file_name is required
        if document_type == 'pdf' and not file_name:
            raise ValueError("file_name is required for PDF documents")
        
        # Prepare request body
        request_data = {
            'content_hash': content_hash,
            'type': document_type
        }
        
        if file_name:
            request_data['file_name'] = file_name
        
        if mode:
            request_data['mode'] = mode.value if hasattr(mode, 'value') else mode
        
        if page_range:
            request_data['page_range'] = page_range
            
        if image_range:
            request_data['image_range'] = image_range
        
        response = self._make_request('POST', '/api/v1/documents/export', json=request_data)
        data = response.json()
        print(f"====== {data}")
        
        try:
            # Convert mode string to enum
            mode_enum = None
            if 'mode' in data:
                if isinstance(data['mode'], str):
                    mode_enum = MarkdownExportMode(data['mode'])
                else:
                    mode_enum = data['mode']
            
            return MarkdownExportResponse(
                success=data['success'],
                mode=mode_enum,
                text=data['text'],
                clips=data.get('clips'),
                image_names=data.get('image_names'),
                content_type=data['content_type'],
                generated_at=data['generated_at']
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def export_document_markdown(self, request: MarkdownExportRequest) -> MarkdownExportResponse:
        """
        Export document to markdown using a request object.
        
        Args:
            request: MarkdownExportRequest with all parameters
            
        Returns:
            MarkdownExportResponse with text and optional clips
            
        Raises:
            APIError: For API errors
        """
        # Validate request
        if not request.content_hash:
            raise ValueError("content_hash is required")
        
        if request.document_type not in ['pdf', 'images']:
            raise ValueError("document_type must be 'pdf' or 'images'")
        
        # For PDF documents, file_name is required
        if request.document_type == 'pdf' and not request.file_name:
            raise ValueError("file_name is required for PDF documents")
        
        # Prepare request body
        request_data = {
            'content_hash': request.content_hash,
            'type': request.document_type
        }
        
        if request.file_name:
            request_data['file_name'] = request.file_name
        
        if request.mode:
            request_data['mode'] = request.mode.value if hasattr(request.mode, 'value') else request.mode
        
        if request.page_range:
            request_data['page_range'] = request.page_range
            
        if request.image_range:
            request_data['image_range'] = request.image_range
        
        response = self._make_request('POST', '/api/v1/documents/export', json=request_data)
        data = response.json()
        
        try:
            # Convert mode string to enum
            mode_enum = None
            if 'mode' in data:
                if isinstance(data['mode'], str):
                    mode_enum = MarkdownExportMode(data['mode'])
                else:
                    mode_enum = data['mode']
            
            return MarkdownExportResponse(
                success=data['success'],
                mode=mode_enum,
                text=data['text'],
                clips=data.get('clips'),
                image_names=data.get('image_names'),
                content_type=data['content_type'],
                generated_at=data['generated_at']
            )
        except (KeyError, ValueError) as e:
            raise APIError(f"Invalid response format: {e}") from e
    
    def close(self):
        """Close session and clean up resources."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
