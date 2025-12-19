#!/usr/bin/env python3
"""
Final working tests for enhanced markdown export functionality.

This test suite properly mocks the _make_request method to avoid network calls.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path so we can import the client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    DotsOCRRunnerClient, AsyncDotsOCRRunnerClient,
    MarkdownExportMode, MarkdownExportRequest, MarkdownExportResponse
)
from dotsocr_runner_client.exceptions import APIError


class TestMarkdownExportModels:
    """Test new markdown export models."""
    
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
    
    def test_get_document_markdown_embedded_mode(self):
        """Test get_document_markdown with embedded mode."""
        # Create client
        client = DotsOCRRunnerClient("http://localhost:8080", "test-token")
        
        # Mock successful response for embedded mode
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "mode": "embedded",
            "text": "# Test Document\n\nContent with embedded image",
            "clips": None,
            "image_names": None,
            "content_type": "text/markdown",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        
        # Mock the _make_request method
        with patch.object(client, '_make_request', return_value=mock_response):
            # Test method
            result = client.get_document_markdown(
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
            
            # Verify API call was made with correct parameters
            client._make_request.assert_called_once_with(
                'POST', 
                '/api/v1/documents/export', 
                json={
                    "content_hash": "abc123",
                    "type": "pdf",
                    "file_name": "test.pdf",
                    "mode": "embedded"
                }
            )
    
    def test_get_document_markdown_separated_mode(self):
        """Test get_document_markdown with separated mode."""
        # Create client
        client = DotsOCRRunnerClient("http://localhost:8080", "test-token")
        
        # Mock successful response for separated mode
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "mode": "separated",
            "text": "# Test Document\n\nContent with ![img1.png](img1.png)",
            "clips": ["base64_image_data_1", "base64_image_data_2"],
            "image_names": ["img1.png", "img2.png"],
            "content_type": "application/json",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        
        # Mock the _make_request method
        with patch.object(client, '_make_request', return_value=mock_response):
            # Test method
            result = client.get_document_markdown(
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
            
            # Verify API call was made with correct parameters
            client._make_request.assert_called_once_with(
                'POST', 
                '/api/v1/documents/export', 
                json={
                    "content_hash": "def456",
                    "type": "images",
                    "mode": "separated",
                    "image_range": "1-5,7"
                }
            )
    
    def test_export_document_markdown_with_request_object(self):
        """Test export_document_markdown with MarkdownExportRequest object."""
        # Create client
        client = DotsOCRRunnerClient("http://localhost:8080", "test-token")
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "mode": "separated",
            "text": "# Document\n\nContent with images",
            "clips": ["image_data_1"],
            "image_names": ["img1.png"],
            "content_type": "application/json",
            "generated_at": "2024-01-01T12:00:00Z"
        }
        
        # Mock the _make_request method
        with patch.object(client, '_make_request', return_value=mock_response):
            # Create request object
            request = MarkdownExportRequest(
                content_hash="req123",
                document_type="pdf",
                file_name="request.pdf",
                mode=MarkdownExportMode.SEPARATED,
                page_range="1-5,7,9-10"
            )
            
            # Test method
            result = client.export_document_markdown(request)
            
            # Verify results
            assert result.success is True
            assert result.mode == MarkdownExportMode.SEPARATED
            assert len(result.clips) == 1
            
            # Verify API call was made with correct parameters
            client._make_request.assert_called_once_with(
                'POST', 
                '/api/v1/documents/export', 
                json={
                    "content_hash": "req123",
                    "type": "pdf",
                    "file_name": "request.pdf",
                    "mode": "separated",
                    "page_range": "1-5,7,9-10"
                }
            )
    
    def test_validation_errors(self):
        """Test validation errors for markdown export methods."""
        # Create client without mock for validation tests
        client = DotsOCRRunnerClient("http://localhost:8080", "test-token")
        
        # Test invalid document type
        with pytest.raises(ValueError, match="document_type must be 'pdf' or 'images'"):
            client.get_document_markdown(
                content_hash="abc123",
                document_type="invalid"
            )
        
        # Test PDF without file name
        with pytest.raises(ValueError, match="file_name is required for PDF documents"):
            client.get_document_markdown(
                content_hash="abc123",
                document_type="pdf"
            )
        
        # Test invalid request object
        with pytest.raises(ValueError, match="document_type must be 'pdf' or 'images'"):
            request = MarkdownExportRequest(
                content_hash="abc123",
                document_type="invalid"
            )
            client.export_document_markdown(request)


class TestErrorHandling:
    """Test error handling for markdown export methods."""
    
    def test_api_error_handling(self):
        """Test API error handling."""
        # Create client
        client = DotsOCRRunnerClient("http://localhost:8080", "test-token")
        
        # Mock the _make_request method to raise an exception
        with patch.object(client, '_make_request', side_effect=Exception("HTTP 404")):
            # Test error handling
            with pytest.raises(Exception, match="HTTP 404"):
                client.get_document_markdown(
                    content_hash="nonexistent",
                    document_type="pdf",
                    file_name="test.pdf"
                )
    
    def test_invalid_response_format(self):
        """Test handling of invalid response format."""
        # Create client
        client = DotsOCRRunnerClient("http://localhost:8080", "test-token")
        
        # Mock invalid response
        mock_response = Mock()
        mock_response.json.return_value = {
            "invalid": "response"
        }
        
        # Mock the _make_request method
        with patch.object(client, '_make_request', return_value=mock_response):
            # Test error handling
            with pytest.raises(APIError, match="Invalid response format"):
                client.get_document_markdown(
                    content_hash="abc123",
                    document_type="pdf",
                    file_name="test.pdf"
                )


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
