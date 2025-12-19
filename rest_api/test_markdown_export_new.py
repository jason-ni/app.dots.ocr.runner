#!/usr/bin/env python3
"""
Test script to verify enhanced markdown export functionality.

This script tests the new markdown export methods with the enhanced API
that supports embedded and separated modes.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import the client
sys.path.insert(0, str(Path(__file__).parent))

from dotsocr_runner_client import DotsOCRRunnerClient, AsyncDotsOCRRunnerClient
from dotsocr_runner_client.models import MarkdownExportMode, MarkdownExportRequest


def test_sync_embedded_markdown_export():
    """Test synchronous embedded markdown export functionality."""
    print("Testing synchronous embedded markdown export...")
    
    # Mock the HTTP session
    with patch('dotsocr_runner_client.client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response for embedded markdown export
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "embedded",
            "text": "# Test Document\n\nThis is a test markdown content with ![img1.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==).",
            "content_type": "text/markdown",
            "generated_at": "2024-01-01T00:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Create client and test
        client = DotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            # Test the new get_document_markdown method with embedded mode
            markdown_response = client.get_document_markdown(
                content_hash="test-doc-id",
                document_type="pdf",
                file_name="test.pdf",
                mode=MarkdownExportMode.EMBEDDED
            )
            
            print(f"✓ Successfully retrieved embedded markdown content")
            print(f"  Mode: {markdown_response.mode}")
            print(f"  Content: {markdown_response.text[:50]}...")
            
            # Verify the correct API call was made
            mock_session.post.assert_called_with(
                "http://test:8080/api/v1/documents/export",
                json={
                    'content_hash': 'test-doc-id',
                    'type': 'pdf',
                    'file_name': 'test.pdf',
                    'mode': 'embedded'
                },
                headers={"Authorization": "Bearer test-token"}
            )
            print("✓ Correct API endpoint called with proper parameters")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    return True


def test_sync_separated_markdown_export():
    """Test synchronous separated markdown export functionality."""
    print("\nTesting synchronous separated markdown export...")
    
    with patch('dotsocr_runner_client.client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response for separated markdown export
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "separated",
            "text": "# Test Document\n\nThis is a test markdown content with ![img1.png](img1.png) and ![img2.png](img2.png).",
            "clips": [
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            ],
            "image_names": ["img1.png", "img2.png"],
            "content_type": "application/json",
            "generated_at": "2024-01-01T00:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        client = DotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            # Test the new get_document_markdown method with separated mode
            markdown_response = client.get_document_markdown(
                content_hash="test-doc-id",
                document_type="images",
                mode=MarkdownExportMode.SEPARATED,
                image_range="1-2"
            )
            
            print(f"✓ Successfully retrieved separated markdown content")
            print(f"  Mode: {markdown_response.mode}")
            print(f"  Text: {markdown_response.text[:50]}...")
            print(f"  Clips: {len(markdown_response.clips) if markdown_response.clips else 0} images")
            print(f"  Image names: {markdown_response.image_names}")
            
            # Verify the correct API call was made
            mock_session.post.assert_called_with(
                "http://test:8080/api/v1/documents/export",
                json={
                    'content_hash': 'test-doc-id',
                    'type': 'images',
                    'mode': 'separated',
                    'image_range': '1-2'
                },
                headers={"Authorization": "Bearer test-token"}
            )
            print("✓ Correct API endpoint called with proper parameters")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    return True


def test_export_request_object():
    """Test export using MarkdownExportRequest object."""
    print("\nTesting export using request object...")
    
    with patch('dotsocr_runner_client.client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "separated",
            "text": "# Request Object Test\n\nContent with ![img1.png](img1.png).",
            "clips": ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="],
            "image_names": ["img1.png"],
            "content_type": "application/json",
            "generated_at": "2024-01-01T00:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        client = DotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            # Create request object
            request = MarkdownExportRequest(
                content_hash="test-doc-id",
                document_type="pdf",
                file_name="test.pdf",
                mode=MarkdownExportMode.SEPARATED,
                page_range="1-5"
            )
            
            # Test export using request object
            markdown_response = client.export_document_markdown(request)
            
            print(f"✓ Successfully exported using request object")
            print(f"  Mode: {markdown_response.mode}")
            print(f"  Text: {markdown_response.text[:50]}...")
            
            # Verify the correct API call was made
            mock_session.post.assert_called_with(
                "http://test:8080/api/v1/documents/export",
                json={
                    'content_hash': 'test-doc-id',
                    'type': 'pdf',
                    'file_name': 'test.pdf',
                    'mode': 'separated',
                    'page_range': '1-5'
                },
                headers={"Authorization": "Bearer test-token"}
            )
            print("✓ Correct API endpoint called with request object")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    return True


async def test_async_markdown_export():
    """Test asynchronous markdown export functionality."""
    print("\nTesting asynchronous markdown export...")
    
    with patch('dotsocr_runner_client.async_client.aiohttp.ClientSession') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "success": True,
            "mode": "embedded",
            "text": "# Async Test Document\n\nThis is async markdown content.",
            "content_type": "text/markdown",
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
        # Mock the async context manager properly
        mock_request = Mock()
        mock_request.__aenter__.return_value = mock_response
        mock_session.post.return_value = mock_request
        
        client = AsyncDotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            # Test the async get_document_markdown method
            markdown_response = await client.get_document_markdown(
                content_hash="test-doc-id",
                document_type="images",
                mode=MarkdownExportMode.EMBEDDED
            )
            
            print(f"✓ Successfully retrieved async markdown content")
            print(f"  Mode: {markdown_response.mode}")
            print(f"  Content: {markdown_response.text[:50]}...")
            
            # Verify the correct API call was made
            mock_session.post.assert_called_with(
                "http://test:8080/api/v1/documents/export",
                json={
                    'content_hash': 'test-doc-id',
                    'type': 'images',
                    'mode': 'embedded'
                },
                headers={"Authorization": "Bearer test-token"}
            )
            print("✓ Async client uses correct API endpoint")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    return True


def test_error_handling():
    """Test error handling for markdown export."""
    print("\nTesting error handling...")
    
    with patch('dotsocr_runner_client.client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "success": False,
            "error": "Document not found"
        }
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_session.post.return_value = mock_response
        
        client = DotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            markdown_response = client.get_document_markdown(
                content_hash="nonexistent-doc-id",
                document_type="pdf",
                file_name="test.pdf"
            )
            print("✗ Should have raised an error")
            return False
        except Exception as e:
            print(f"✓ Correctly handled error: {e}")
            return True


def test_validation():
    """Test input validation."""
    print("\nTesting input validation...")
    
    client = DotsOCRRunnerClient("http://test:8080", "test-token")
    
    try:
        # Test invalid document type
        client.get_document_markdown(
            content_hash="test-doc-id",
            document_type="invalid"
        )
        print("✗ Should have raised ValueError for invalid document type")
        return False
    except ValueError as e:
        print(f"✓ Correctly validated document type: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    try:
        # Test PDF without file name
        client.get_document_markdown(
            content_hash="test-doc-id",
            document_type="pdf"
        )
        print("✗ Should have raised ValueError for missing file name")
        return False
    except ValueError as e:
        print(f"✓ Correctly validated PDF file name requirement: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=== Enhanced DotsOCR Markdown Export Tests ===\n")
    
    tests = [
        test_sync_embedded_markdown_export,
        test_sync_separated_markdown_export,
        test_export_request_object,
        test_error_handling,
        test_validation,
    ]
    
    # Run synchronous tests
    sync_results = []
    for test in tests:
        try:
            result = test()
            sync_results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            sync_results.append(False)
    
    # Run async tests
    print("\n" + "="*50)
    async_results = []
    try:
        import asyncio
        result = asyncio.run(test_async_markdown_export())
        async_results.append(result)
    except Exception as e:
        print(f"✗ Async test failed with exception: {e}")
        async_results.append(False)
    
    # Summary
    all_results = sync_results + async_results
    passed = sum(all_results)
    total = len(all_results)
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Enhanced markdown export functionality is working correctly.")
        return True
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
