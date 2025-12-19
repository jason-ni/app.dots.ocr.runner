#!/usr/bin/env python3
"""
Comprehensive tests for enhanced markdown export functionality.

This test suite covers the new JSON response format with embedded and separated modes,
page/image range filtering, and all the new models and methods.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add the parent directory to the path so we can import the client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    DotsOCRRunnerClient, AsyncDotsOCRRunnerClient,
    MarkdownExportMode, MarkdownExportRequest, MarkdownExportResponse
)
from dotsocr_runner_client.exceptions import APIError


class TestMarkdownExportModels:
    """Test the new markdown export models."""
    
    def test_markdown_export_mode_enum(self):
        """Test MarkdownExportMode enum values."""
        assert MarkdownExportMode.EMBEDDED.value == "embedded"
        assert MarkdownExportMode.SEPARATED.value == "separated"
        
        # Test enum creation from string
        assert MarkdownExportMode("embedded") == MarkdownExportMode.EMBEDDED
        assert MarkdownExportMode("separated") == MarkdownExportMode.SEPARATED
    
    def test_markdown_export_request(self):
        """Test MarkdownExportRequest model."""
        # Test with required fields only
        request = MarkdownExportRequest(
            content_hash="abc123",
            document_type="pdf",
            file_name="test.pdf"
        )
        assert request.content_hash == "abc123"
        assert request.document_type == "pdf"
        assert request.file_name == "test.pdf"
        assert request.mode is None
        assert request.page_range is None
        assert request.image_range is None
        
        # Test with all fields
        request_full = MarkdownExportRequest(
            content_hash="def456",
            document_type="images",
            mode=MarkdownExportMode.SEPARATED,
            image_range="1-5,7"
        )
        assert request_full.mode == MarkdownExportMode.SEPARATED
        assert request_full.image_range == "1-5,7"
    
    def test_markdown_export_response(self):
        """Test MarkdownExportResponse model."""
        # Test embedded mode response
        response_embedded = MarkdownExportResponse(
            success=True,
            mode=MarkdownExportMode.EMBEDDED,
            text="# Document\n\nContent with ![image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==)",
            clips=None,
            image_names=None,
            content_type="text/markdown",
            generated_at="2024-01-01T12:00:00Z"
        )
        assert response_embedded.success is True
        assert response_embedded.mode == MarkdownExportMode.EMBEDDED
        assert response_embedded.clips is None
        assert response_embedded.image_names is None
        
        # Test separated mode response
        response_separated = MarkdownExportResponse(
            success=True,
            mode=MarkdownExportMode.SEPARATED,
            text="# Document\n\nContent with ![img1.png](img1.png) and ![img2.png](img2.png)",
            clips=["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "another_base64_string"],
            image_names=["img1.png", "img2.png"],
            content_type="application/json",
            generated_at="2024-01-01T12:00:00Z"
        )
        assert response_separated.success is True
        assert response_separated.mode == MarkdownExportMode.SEPARATED
        assert len(response_separated.clips) == 2
        assert len(response_separated.image_names) == 2
        assert response_separated.clips[0] == "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


class TestSyncMarkdownExport:
    """Test synchronous markdown export methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = DotsOCRRunnerClient("http://test:8080", "test-token")
    
    @patch('dotsocr_runner_client.client.requests.Session')
    def test_get_document_markdown_embedded_mode(self, mock_session_class):
        """Test get_document_markdown with embedded mode."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response for embedded mode
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "embedded",
            "text": "# Test Document\n\nContent with embedded image",
            "clips": None,
            "image_names": None,
            "content_type": "text/markdown",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Test the method
        result = self.client.get_document_markdown(
            content_hash="abc123",
            document_type="pdf",
            file_name="test.pdf",
            mode=MarkdownExportMode.EMBEDDED
        )
        
        # Verify results
        assert result.success is True
        assert result.mode == MarkdownExportMode.EMBEDDED
        assert "Content with embedded image" in result.text
        assert result.clips is None
        assert result.image_names is None
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "http://test:8080/api/v1/documents/export",
            json={
                "content_hash": "abc123",
                "type": "pdf",
                "file_name": "test.pdf",
                "mode": "embedded"
            },
            headers={"Authorization": "Bearer test-token"}
        )
    
    @patch('dotsocr_runner_client.client.requests.Session')
    def test_get_document_markdown_separated_mode(self, mock_session_class):
        """Test get_document_markdown with separated mode."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response for separated mode
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "separated",
            "text": "# Test Document\n\nContent with ![img1.png](img1.png)",
            "clips": ["base64_image_data_1", "base64_image_data_2"],
            "image_names": ["img1.png", "img2.png"],
            "content_type": "application/json",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Test the method
        result = self.client.get_document_markdown(
            content_hash="def456",
            document_type="images",
            mode=MarkdownExportMode.SEPARATED,
            image_range="1-5,7"
        )
        
        # Verify results
        assert result.success is True
        assert result.mode == MarkdownExportMode.SEPARATED
        assert "img1.png" in result.text
        assert len(result.clips) == 2
        assert len(result.image_names) == 2
        assert result.clips[0] == "base64_image_data_1"
        assert result.image_names[0] == "img1.png"
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "http://test:8080/api/v1/documents/export",
            json={
                "content_hash": "def456",
                "type": "images",
                "mode": "separated",
                "image_range": "1-5,7"
            },
            headers={"Authorization": "Bearer test-token"}
        )
    
    @patch('dotsocr_runner_client.client.requests.Session')
    def test_get_document_markdown_with_page_range(self, mock_session_class):
        """Test get_document_markdown with page range for PDF."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "embedded",
            "text": "# Pages 1-3\n\nContent from selected pages",
            "clips": None,
            "image_names": None,
            "content_type": "text/markdown",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Test the method with page range
        result = self.client.get_document_markdown(
            content_hash="abc123",
            document_type="pdf",
            file_name="test.pdf",
            page_range="1-3"
        )
        
        # Verify API call includes page range
        mock_session.post.assert_called_once_with(
            "http://test:8080/api/v1/documents/export",
            json={
                "content_hash": "abc123",
                "type": "pdf",
                "file_name": "test.pdf",
                "page_range": "1-3"
            },
            headers={"Authorization": "Bearer test-token"}
        )
    
    @patch('dotsocr_runner_client.client.requests.Session')
    def test_export_document_markdown_with_request_object(self, mock_session_class):
        """Test export_document_markdown with MarkdownExportRequest object."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "separated",
            "text": "# Document\n\nContent with images",
            "clips": ["image_data_1"],
            "image_names": ["img1.png"],
            "content_type": "application/json",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Create request object
        request = MarkdownExportRequest(
            content_hash="req123",
            document_type="pdf",
            file_name="request.pdf",
            mode=MarkdownExportMode.SEPARATED,
            page_range="1-5,7,9-10"
        )
        
        # Test the method
        result = self.client.export_document_markdown(request)
        
        # Verify results
        assert result.success is True
        assert result.mode == MarkdownExportMode.SEPARATED
        assert len(result.clips) == 1
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "http://test:8080/api/v1/documents/export",
            json={
                "content_hash": "req123",
                "type": "pdf",
                "file_name": "request.pdf",
                "mode": "separated",
                "page_range": "1-5,7,9-10"
            },
            headers={"Authorization": "Bearer test-token"}
        )
    
    def test_validation_errors(self):
        """Test validation errors for markdown export methods."""
        # Test invalid document type
        with pytest.raises(ValueError, match="document_type must be 'pdf' or 'images'"):
            self.client.get_document_markdown(
                content_hash="abc123",
                document_type="invalid"
            )
        
        # Test PDF without file name
        with pytest.raises(ValueError, match="file_name is required for PDF documents"):
            self.client.get_document_markdown(
                content_hash="abc123",
                document_type="pdf"
            )
        
        # Test invalid request object
        with pytest.raises(ValueError, match="document_type must be 'pdf' or 'images'"):
            request = MarkdownExportRequest(
                content_hash="abc123",
                document_type="invalid"
            )
            self.client.export_document_markdown(request)


class TestAsyncMarkdownExport:
    """Test asynchronous markdown export methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = AsyncDotsOCRRunnerClient("http://test:8080", "test-token")
    
    @patch('dotsocr_runner_client.async_client.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_async_get_document_markdown_embedded(self, mock_session_class):
        """Test async get_document_markdown with embedded mode."""
        mock_session = Mock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "embedded",
            "text": "# Async Document\n\nContent with embedded image",
            "clips": None,
            "image_names": None,
            "content_type": "text/markdown",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Test the method
        result = await self.client.get_document_markdown(
            content_hash="async123",
            document_type="pdf",
            file_name="async.pdf",
            mode=MarkdownExportMode.EMBEDDED
        )
        
        # Verify results
        assert result.success is True
        assert result.mode == MarkdownExportMode.EMBEDDED
        assert "Content with embedded image" in result.text
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "http://test:8080/api/v1/documents/export",
            json={
                "content_hash": "async123",
                "type": "pdf",
                "file_name": "async.pdf",
                "mode": "embedded"
            },
            headers={"Authorization": "Bearer test-token"}
        )
    
    @patch('dotsocr_runner_client.async_client.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_async_get_document_markdown_separated(self, mock_session_class):
        """Test async get_document_markdown with separated mode."""
        mock_session = Mock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "separated",
            "text": "# Async Document\n\nContent with ![img1.png](img1.png)",
            "clips": ["async_base64_1", "async_base64_2"],
            "image_names": ["img1.png", "img2.png"],
            "content_type": "application/json",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Test the method
        result = await self.client.get_document_markdown(
            content_hash="async456",
            document_type="images",
            mode=MarkdownExportMode.SEPARATED,
            image_range="1-3,5"
        )
        
        # Verify results
        assert result.success is True
        assert result.mode == MarkdownExportMode.SEPARATED
        assert len(result.clips) == 2
        assert len(result.image_names) == 2
        assert result.clips[0] == "async_base64_1"
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "http://test:8080/api/v1/documents/export",
            json={
                "content_hash": "async456",
                "type": "images",
                "mode": "separated",
                "image_range": "1-3,5"
            },
            headers={"Authorization": "Bearer test-token"}
        )
    
    @patch('dotsocr_runner_client.async_client.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_async_export_document_markdown_request_object(self, mock_session_class):
        """Test async export_document_markdown with request object."""
        mock_session = Mock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "embedded",
            "text": "# Request Document\n\nContent",
            "clips": None,
            "image_names": None,
            "content_type": "text/markdown",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Create request object
        request = MarkdownExportRequest(
            content_hash="request123",
            document_type="pdf",
            file_name="request.pdf",
            mode=MarkdownExportMode.EMBEDDED,
            page_range="2-4"
        )
        
        # Test the method
        result = await self.client.export_document_markdown(request)
        
        # Verify results
        assert result.success is True
        assert result.mode == MarkdownExportMode.EMBEDDED
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "http://test:8080/api/v1/documents/export",
            json={
                "content_hash": "request123",
                "type": "pdf",
                "file_name": "request.pdf",
                "mode": "embedded",
                "page_range": "2-4"
            },
            headers={"Authorization": "Bearer test-token"}
        )
    
    @pytest.mark.asyncio
    async def test_async_validation_errors(self):
        """Test validation errors for async markdown export methods."""
        # Test invalid document type
        with pytest.raises(ValueError, match="document_type must be 'pdf' or 'images'"):
            await self.client.get_document_markdown(
                content_hash="abc123",
                document_type="invalid"
            )
        
        # Test PDF without file name
        with pytest.raises(ValueError, match="file_name is required for PDF documents"):
            await self.client.get_document_markdown(
                content_hash="abc123",
                document_type="pdf"
            )


class TestErrorHandling:
    """Test error handling for markdown export methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = DotsOCRRunnerClient("http://test:8080", "test-token")
    
    @patch('dotsocr_runner_client.client.requests.Session')
    def test_api_error_handling(self, mock_session_class):
        """Test API error handling."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": {"message": "Document not found"}
        }
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_session.post.return_value = mock_response
        
        # Test error handling
        with pytest.raises(Exception):
            self.client.get_document_markdown(
                content_hash="nonexistent",
                document_type="pdf",
                file_name="test.pdf"
            )
    
    @patch('dotsocr_runner_client.client.requests.Session')
    def test_invalid_response_format(self, mock_session_class):
        """Test handling of invalid response format."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock invalid response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "invalid": "response"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Test error handling
        with pytest.raises(APIError, match="Invalid response format"):
            self.client.get_document_markdown(
                content_hash="abc123",
                document_type="pdf",
                file_name="test.pdf"
            )


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
