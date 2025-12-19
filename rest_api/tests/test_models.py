"""
Tests for data models.
"""

from dotsocr_runner_client.models import (
    UploadResponse,
    TaskStatusResponse,
    OCRResult,
    DeleteResponse,
    TasksListResponse,
    HealthResponse
)


class TestUploadResponse:
    """Test UploadResponse model."""
    
    def test_upload_response_creation(self):
        """Test creating UploadResponse."""
        response = UploadResponse(
            task_id="test-task-id",
            status="pending",
            file_type="pdf",
            filename="test.pdf",
            estimated_duration="30-60 seconds"
        )
        
        assert response.task_id == "test-task-id"
        assert response.status == "pending"
        assert response.file_type == "pdf"
        assert response.filename == "test.pdf"
        assert response.estimated_duration == "30-60 seconds"
    
    def test_upload_response_dataclass(self):
        """Test UploadResponse dataclass properties."""
        response = UploadResponse(
            task_id="test-task-id",
            status="pending",
            file_type="pdf",
            filename="test.pdf",
            estimated_duration="30-60 seconds"
        )
        
        # Test dataclass properties
        assert response.task_id == "test-task-id"
        assert response.status == "pending"
        assert response.file_type == "pdf"
        assert response.filename == "test.pdf"
        assert response.estimated_duration == "30-60 seconds"
        
        # Test __dict__ representation
        data = response.__dict__
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "pending"


class TestTaskStatusResponse:
    """Test TaskStatusResponse model."""
    
    def test_task_status_response_creation(self):
        """Test creating TaskStatusResponse."""
        response = TaskStatusResponse(
            task_id="test-task-id",
            status="running",
            progress=75.5,
            filename="test.pdf"
        )
        
        assert response.task_id == "test-task-id"
        assert response.status == "running"
        assert response.progress == 75.5
        assert response.filename == "test.pdf"
    
    def test_task_status_response_different_status(self):
        """Test TaskStatusResponse with different status."""
        response = TaskStatusResponse(
            task_id="test-task-id",
            status="pending",
            progress=0.0,
            filename="test.pdf"
        )
        
        assert response.status == "pending"
        assert response.progress == 0.0
        assert response.filename == "test.pdf"


class TestOCRResult:
    """Test OCRResult model."""
    
    def test_ocr_result_creation(self):
        """Test creating OCRResult."""
        result = OCRResult(
            task_id="test-task-id",
            status="completed",
            result={"content": "OCR text content", "type": "pdf"},
            metadata={"pages": 10, "processing_time": "45 seconds"}
        )
        
        assert result.task_id == "test-task-id"
        assert result.status == "completed"
        assert result.result["content"] == "OCR text content"
        assert result.result["type"] == "pdf"
        assert result.metadata["pages"] == 10
        assert result.metadata["processing_time"] == "45 seconds"


class TestDeleteResponse:
    """Test DeleteResponse model."""
    
    def test_delete_response_creation(self):
        """Test creating DeleteResponse."""
        response = DeleteResponse(
            task_id="test-task-id",
            status="deleted"
        )
        
        assert response.task_id == "test-task-id"
        assert response.status == "deleted"


class TestTasksListResponse:
    """Test TasksListResponse model."""
    
    def test_tasks_list_response_creation(self):
        """Test creating TasksListResponse."""
        tasks = [
            {
                "task_id": "task-1",
                "status": "completed",
                "filename": "doc1.pdf"
            },
            {
                "task_id": "task-2",
                "status": "running",
                "filename": "doc2.pdf"
            }
        ]
        
        response = TasksListResponse(
            tasks=tasks,
            total_count=2
        )
        
        assert len(response.tasks) == 2
        assert response.total_count == 2
        assert response.tasks[0]["task_id"] == "task-1"
        assert response.tasks[1]["status"] == "running"


class TestHealthResponse:
    """Test HealthResponse model."""
    
    def test_health_response_creation(self):
        """Test creating HealthResponse."""
        response = HealthResponse(
            status="healthy",
            timestamp="2023-01-01T00:00:00Z",
            version="1.0.0"
        )
        
        assert response.status == "healthy"
        assert response.timestamp == "2023-01-01T00:00:00Z"
        assert response.version == "1.0.0"
    
    def test_health_response_required_fields(self):
        """Test HealthResponse with all required fields."""
        response = HealthResponse(
            status="healthy",
            timestamp="2023-01-01T00:00:00Z",
            version="1.0.0"
        )
        
        assert response.status == "healthy"
        assert response.timestamp == "2023-01-01T00:00:00Z"
        assert response.version == "1.0.0"
