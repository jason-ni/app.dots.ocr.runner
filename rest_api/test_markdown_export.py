#!/usr/bin/env python3
"""
Test script to verify markdown export functionality.

This script tests the markdown export methods without requiring a running server
by mocking the HTTP responses.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import the client
sys.path.insert(0, str(Path(__file__).parent))

from dotsocr_runner_client import DotsOCRRunnerClient, AsyncDotsOCRRunnerClient


def test_sync_markdown_export():
    """Test synchronous markdown export functionality."""
    print("Testing synchronous markdown export...")
    
    # Mock the HTTP session
    with patch('dotsocr_runner_client.client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response for markdown export
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "content": "# Test Document\n\nThis is a test markdown content."
        }
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        
        # Create client and test
        client = DotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            # Test the new get_document_markdown method
            markdown_content = client.get_document_markdown("test-doc-id")
            
            print(f"✓ Successfully retrieved markdown content")
            print(f"  Content: {markdown_content[:50]}...")
            
            # Verify the correct API call was made
            mock_session.get.assert_called_with(
                "http://test:8080/api/v1/documents/test-doc-id/export",
                params={"format": "markdown", "return_content": "1"},
                headers={"Authorization": "Bearer test-token"}
            )
            print("✓ Correct API endpoint called with proper parameters")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    return True


def test_sync_export_method_integration():
    """Test integration with existing export method."""
    print("\nTesting export method integration...")
    
    with patch('dotsocr_runner_client.client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response for markdown export
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "content": "# Exported Document\n\nContent from export method."
        }
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        
        client = DotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            # Test the existing export method with markdown format
            export_response = client.export_document("test-doc-id", "markdown")
            
            print(f"✓ Export method works with markdown format")
            print(f"  Content: {export_response.content[:50]}...")
            
            # Verify the correct API call was made
            mock_session.get.assert_called_with(
                "http://test:8080/api/v1/documents/test-doc-id/export",
                params={"format": "markdown", "return_content": "1"},
                headers={"Authorization": "Bearer test-token"}
            )
            print("✓ Export method uses correct parameters for markdown")
            
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
            "content": "# Async Test Document\n\nThis is async markdown content."
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        client = AsyncDotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            # Test the async get_document_markdown method
            markdown_content = await client.get_document_markdown("test-doc-id")
            
            print(f"✓ Successfully retrieved async markdown content")
            print(f"  Content: {markdown_content[:50]}...")
            
            # Verify the correct API call was made
            mock_session.get.assert_called_with(
                "http://test:8080/api/v1/documents/test-doc-id/export",
                params={"format": "markdown", "return_content": "1"},
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
        mock_session.get.return_value = mock_response
        
        client = DotsOCRRunnerClient("http://test:8080", "test-token")
        
        try:
            markdown_content = client.get_document_markdown("nonexistent-doc-id")
            print("✗ Should have raised an error")
            return False
        except Exception as e:
            print(f"✓ Correctly handled error: {e}")
            return True


def main():
    """Run all tests."""
    print("=== DotsOCR Markdown Export Tests ===\n")
    
    tests = [
        test_sync_markdown_export,
        test_sync_export_method_integration,
        test_error_handling,
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
        print("✓ All tests passed! Markdown export functionality is working correctly.")
        return True
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
