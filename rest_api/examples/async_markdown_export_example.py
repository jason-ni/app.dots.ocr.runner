#!/usr/bin/env python3
"""
Async examples demonstrating the enhanced markdown export functionality.

This example shows how to use both embedded and separated export modes
with the async client for exporting OCR results as markdown.
"""

import sys
import os
import asyncio
import traceback
from pathlib import Path

# Add parent directory to the path so we can import the client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    AsyncDotsOCRRunnerClient,
    MarkdownExportMode, MarkdownExportRequest,
    setup_logging,
    APIError,
    AuthenticationError,
    ConnectionError
)

# Set up logging
setup_logging("INFO")

# Get configuration from environment variables
def get_config():
    """Get configuration from environment variables with defaults."""
    server_url = os.getenv("DOTSOCR_SERVER_URL", "http://127.0.0.1:8080")
    auth_token = os.getenv("DOTSOCR_AUTH_TOKEN")
    
    if not auth_token:
        print("Warning: DOTSOCR_AUTH_TOKEN environment variable not set.")
        print("Please set it using: export DOTSOCR_AUTH_TOKEN='your-secret-token'")
        auth_token = "your-secret-token"  # Fallback for testing
    
    return server_url, auth_token


async def example_async_embedded_export():
    """Example: Async export markdown with embedded base64 images (original behavior)."""
    print("=== Async Embedded Export Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize async client
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # First, list available documents
            print("Fetching available documents...")
            documents_response = await client.list_documents(page_size=10)
            
            if not documents_response.documents:
                print("ℹ No documents found on the server. Please upload some documents first.")
                return
            
            # Use's first available document for this example
            document = documents_response.documents[0]
            print(f"✓ Found document: {document.name} (ID: {document.id}, Type: {document.type})")
            
            # Export with embedded images (default mode)
            response = await client.get_document_markdown(
                content_hash=document.id,
                document_type=document.type,
                file_name=document.name if document.type == "pdf" else None,
                mode=MarkdownExportMode.EMBEDDED  # or omit for default
            )
            
            print(f"✓ Async embedded export successful!")
            print(f"Mode: {response.mode.value}")
            print(f"Content type: {response.content_type}")
            print(f"Generated at: {response.generated_at}")
            print(f"Text length: {len(response.text)} characters")
            
            # Show a preview of the markdown (first 200 characters)
            preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
            print(f"Preview: {preview}")
            
            # In embedded mode, images are included as base64 data URLs
            if "data:image" in response.text:
                print("✓ Images are embedded as base64 data URLs")
            else:
                print("ℹ No images found in the document")
                
        except Exception as e:
            print(f"✗ Async error: {e}")


async def example_async_separated_export():
    """Example: Async export markdown with separated images (new feature)."""
    print("\n=== Async Separated Export Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize async client
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # First, list available documents
            print("Fetching available documents...")
            documents_response = await client.list_documents(page_size=10)
            
            if not documents_response.documents:
                print("ℹ No documents found on the server. Please upload some documents first.")
                return
            
            # Use's first available document for this example
            document = documents_response.documents[0]
            print(f"✓ Found document: {document.name} (ID: {document.id}, Type: {document.type})")
            
            # Export with separated images
            response = await client.get_document_markdown(
                content_hash=document.id,
                document_type=document.type,
                file_name=document.name if document.type == "pdf" else None,
                mode=MarkdownExportMode.SEPARATED
            )
            
            print(f"✓ Async separated export successful!")
            print(f"Mode: {response.mode.value}")
            print(f"Content type: {response.content_type}")
            print(f"Generated at: {response.generated_at}")
            print(f"Text length: {len(response.text)} characters")
            
            # Show a preview of markdown
            preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
            print(f"Preview: {preview}")
            
            # In separated mode, images are provided separately
            if response.clips and response.image_names:
                print(f"✓ Found {len(response.clips)} separated images:")
                for i, (clip, name) in enumerate(zip(response.clips, response.image_names)):
                    print(f"  Image {i+1}: {name} ({len(clip)} characters of base64 data)")
                
                # Save images asynchronously
                print("\n--- Saving Images Asynchronously ---")
                import base64
                save_tasks = []
                
                for i, (clip, name) in enumerate(zip(response.clips, response.image_names)):
                    # Extract base64 data
                    if clip.startswith('data:image'):
                        base64_data = clip.split(',')[1]
                    else:
                        base64_data = clip
                    
                    # Create async save task
                    async def save_image(data, filename):
                        try:
                            image_data = base64.b64decode(data)
                            with open(f"async_exported_{filename}", 'wb') as f:
                                f.write(image_data)
                            return f"✓ Saved {filename}"
                        except Exception as e:
                            return f"✗ Failed to save {filename}: {e}"
                    
                    save_tasks.append(save_image(base64_data, name))
                
                # Wait for all saves to complete
                results = await asyncio.gather(*save_tasks)
                for result in results:
                    print(result)
            else:
                print("ℹ No images found in the document")
                
        except Exception as e:
            print(f"✗ Async error: {e}")


async def example_async_request_object():
    """Example: Async export using MarkdownExportRequest object."""
    print("\n=== Async Request Object Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize async client
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # First, list available documents
            print("Fetching available documents...")
            documents_response = await client.list_documents(page_size=10)
            
            if not documents_response.documents:
                print("ℹ No documents found on the server. Please upload some documents first.")
                return
            
            # Use's first available document for this example
            document = documents_response.documents[0]
            print(f"✓ Found document: {document.name} (ID: {document.id}, Type: {document.type})")
            
            # Create a detailed request object
            request = MarkdownExportRequest(
                content_hash=document.id,
                document_type=document.type,
                file_name=document.name if document.type == "pdf" else None,
                mode=MarkdownExportMode.SEPARATED,
                page_range="1-3" if document.type == "pdf" else None  # Export specific pages for PDF
            )
            
            # Export using the request object asynchronously
            response = await client.export_document_markdown(request)
            
            print(f"✓ Async export with request object successful!")
            print(f"Mode: {response.mode.value}")
            if request.page_range:
                print(f"Page range: {request.page_range}")
            print(f"Text length: {len(response.text)} characters")
            
            if response.clips:
                print(f"✓ Exported {len(response.clips)} images from specified pages")
                
        except Exception as e:
            print(f"✗ Async error: {e}")


async def example_async_concurrent_exports():
    """Example: Concurrent exports of multiple documents."""
    print("\n=== Async Concurrent Exports Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize async client
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # Create multiple export tasks
            export_tasks = []
            
            # Task 1: Embedded export
            task1 = client.get_document_markdown(
                content_hash="doc1_hash",
                document_type="pdf",
                file_name="document1.pdf",
                mode=MarkdownExportMode.EMBEDDED
            )
            export_tasks.append(("Document 1 (Embedded)", task1))
            
            # Task 2: Separated export
            task2 = client.get_document_markdown(
                content_hash="doc2_hash",
                document_type="pdf",
                file_name="document2.pdf",
                mode=MarkdownExportMode.SEPARATED
            )
            export_tasks.append(("Document 2 (Separated)", task2))
            
            # Task 3: Image batch export
            task3 = client.get_document_markdown(
                content_hash="batch_hash",
                document_type="images",
                mode=MarkdownExportMode.SEPARATED,
                image_range="1-3,5"
            )
            export_tasks.append(("Image Batch", task3))
            
            # Execute all tasks concurrently
            print(f"Starting {len(export_tasks)} concurrent export tasks...")
            results = await asyncio.gather(*[task for _, task in export_tasks], return_exceptions=True)
            
            # Process results
            for i, (name, _) in enumerate(export_tasks):
                result = results[i]
                if isinstance(result, Exception):
                    print(f"✗ {name}: {result}")
                else:
                    print(f"✓ {name}: {len(result.text)} chars, {len(result.clips or [])} images")
                    
        except Exception as e:
            print(f"✗ Concurrent export error: {e}")


async def example_async_batch_processing():
    """Example: Process multiple documents with progress tracking."""
    print("\n=== Async Batch Processing Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize async client
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # List of documents to process
            documents = [
                {"content_hash": "doc1_hash", "document_type": "pdf", "file_name": "doc1.pdf"},
                {"content_hash": "doc2_hash", "document_type": "pdf", "file_name": "doc2.pdf"},
                {"content_hash": "doc3_hash", "document_type": "images"},
            ]
            
            print(f"Processing {len(documents)} documents...")
            
            # Process documents with progress tracking
            for i, doc in enumerate(documents, 1):
                print(f"\nProcessing document {i}/{len(documents)}: {doc['content_hash']}")
                
                try:
                    # Export in separated mode
                    response = await client.get_document_markdown(
                        content_hash=doc["content_hash"],
                        document_type=doc["document_type"],
                        file_name=doc.get("file_name"),
                        mode=MarkdownExportMode.SEPARATED
                    )
                    
                    print(f"  ✓ Exported: {len(response.text)} chars, {len(response.clips or [])} images")
                    
                    # Save images if any
                    if response.clips:
                        import base64
                        for j, (clip, name) in enumerate(zip(response.clips, response.image_names or [])):
                            if clip.startswith('data:image'):
                                base64_data = clip.split(',')[1]
                            else:
                                base64_data = clip
                            
                            image_data = base64.b64decode(base64_data)
                            filename = f"batch_{i}_{name}"
                            with open(filename, 'wb') as f:
                                f.write(image_data)
                            print(f"    ✓ Saved: {filename}")
                
                except Exception as e:
                    print(f"  ✗ Failed: {e}")
            
            print(f"\n✓ Batch processing completed!")
                    
        except Exception as e:
            print(f"✗ Batch processing error: {e}")


async def example_async_error_handling():
    """Example: Async error handling and retry logic."""
    print("\n=== Async Error Handling Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize async client
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # Try to export a non-existent document
            print("Attempting to export non-existent document...")
            response = await client.get_document_markdown(
                content_hash="nonexistent_hash",
                document_type="pdf",
                file_name="nonexistent.pdf",
                mode=MarkdownExportMode.SEPARATED
            )
            print("✓ Unexpected success!")
            
        except Exception as e:
            print(f"✓ Expected error caught: {e}")
            
            # Implement retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"\nRetry attempt {attempt + 1}/{max_retries}...")
                    # Try with a different document
                    response = await client.get_document_markdown(
                        content_hash="valid_hash",
                        document_type="pdf",
                        file_name="valid.pdf",
                        mode=MarkdownExportMode.EMBEDDED
                    )
                    print("✓ Retry successful!")
                    break
                except Exception as retry_error:
                    print(f"✗ Retry {attempt + 1} failed: {retry_error}")
                    if attempt == max_retries - 1:
                        print("✗ All retry attempts failed")


async def example_async_basic_functionality():
    """Example: Test basic async functionality without server."""
    print("=== Async Basic Functionality Test ===")
    
    try:
        # Test that we can import and create async models
        from dotsocr_runner_client import AsyncDotsOCRRunnerClient, MarkdownExportMode
        
        # Test async client creation (without connecting)
        client = AsyncDotsOCRRunnerClient("http://test:8080", "test-token")
        print(f"✓ Created async client: {client.base_url}")
        
        # Test enum values
        print(f"✓ MarkdownExportMode.EMBEDDED: {MarkdownExportMode.EMBEDDED.value}")
        print(f"✓ MarkdownExportMode.SEPARATED: {MarkdownExportMode.SEPARATED.value}")
        
        # Test context manager creation (without actually connecting)
        async with AsyncDotsOCRRunnerClient("http://test:8080", "test-token") as client:
            print(f"✓ Async client context manager works: {client.base_url}")
        
        print("✓ All async basic functionality tests passed!")
        
    except Exception as e:
        print(f"✗ Async basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all async examples."""
    print("DotsOCR Enhanced Async Markdown Export Examples")
    print("=" * 55)
    
    
    # Run examples that work with real documents
    try:
        await example_async_embedded_export()
        await example_async_separated_export()
        await example_async_request_object()
    except KeyboardInterrupt:
        print("\n✗ Examples interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error running examples: {e}")
        print("Make sure the server is running and you have valid authentication token")
    


if __name__ == "__main__":
    asyncio.run(main())
