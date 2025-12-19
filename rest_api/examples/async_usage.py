#!/usr/bin/env python3
"""
Async usage examples for DotsOCR Python client.

This example demonstrates:
1. Async PDF OCR processing
2. Async task management operations
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add parent directory to the path so we can import dotsocr_runner_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    AsyncDotsOCRRunnerClient,
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
        print("Or pass the token directly to the examples.")
        auth_token = "your-secret-token"  # Fallback for testing
    
    return server_url, auth_token

async def example_1_async_pdf_ocr():
    """Example 1: Async PDF OCR processing."""
    print("=" * 50)
    print("Async Example 1: PDF OCR Processing")
    print("=" * 50)
    
    server_url, auth_token = get_config()
    pdf_path = "../../test_assets/test1.pdf"
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print(f"Processing PDF: {pdf_path}")
            
            # Upload PDF with default DPI (150 for PDFs)
            upload_response = await client.upload_pdf(pdf_path)
            print(f"Task ID: {upload_response.task_id}")
            print(f"Status: {upload_response.status}")
            print(f"Used default DPI: 150 (PDF default)")
            
            # Wait for completion with progress callback
            def progress_callback(progress, message):
                print(f"Progress: {progress:.1f}% - {message}")
            
            result = await client.wait_for_completion(
                upload_response.task_id,
                progress_callback=progress_callback
            )
            
            print(f"\nOCR completed successfully!")
            
            # Handle different result structures
            if result.result.get('type') == 'pdf':
                pages = result.result.get('pages', [])
                if pages:
                    # Get content from first page
                    first_page_content = pages[0].get('content', '')
                    print(f"Content preview (Page 1): {first_page_content[:200]}...")
                    print(f"Total pages: {result.result.get('page_count', 0)}")
                else:
                    print("No pages found in result")
            elif result.result.get('type') == 'batch_images':
                images = result.result.get('images', [])
                if images:
                    # Get content from first image
                    first_image_content = images[0].get('content', '')
                    print(f"Content preview (Image 1): {first_image_content[:200]}...")
                    print(f"Total images: {result.result.get('image_count', 0)}")
                else:
                    print("No images found in result")
            else:
                # Fallback for unknown structure
                print(f"Result: {result.result}")
            
    except Exception as e:
        print(f"Error: {e}")





async def example_2_async_custom_dpi():
    """Example 2: Async custom DPI usage."""
    print("\n" + "=" * 50)
    print("Async Example 2: Custom DPI Usage")
    print("=" * 50)
    
    server_url, auth_token = get_config()
    pdf_path = "../../test_assets/test1.pdf"
    image_paths = [
        "../../test_assets/pic1.png",
        "../../test_assets/pic2.png"
    ]
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating async custom DPI settings...")
            
            # Example 1: PDF with high DPI for better quality
            print("\n1. PDF with high DPI (300) for maximum quality:")
            upload_response = await client.upload_pdf(pdf_path, dpi=300)
            print(f"   Task ID: {upload_response.task_id}")
            print(f"   Used custom DPI: 300")
            
            # Wait for completion
            result = await client.wait_for_completion(upload_response.task_id)
            print(f"   ✓ High-DPI PDF processing completed")
            
            # Example 2: Images with medium DPI
            print("\n2. Images with medium DPI (150) for balanced quality:")
            upload_response = await client.upload_images(image_paths, dpi=150)
            print(f"   Task ID: {upload_response.task_id}")
            print(f"   Used custom DPI: 150")
            
            # Wait for completion
            result = await client.wait_for_completion(upload_response.task_id)
            print(f"   ✓ Medium-DPI image processing completed")
            
            # Example 3: Concurrent processing with different DPIs
            print("\n3. Concurrent processing with different DPIs:")
            
            # Start multiple tasks concurrently
            tasks = []
            
            # High DPI PDF
            task1 = asyncio.create_task(
                client.upload_pdf(pdf_path, dpi=200)
            )
            tasks.append(("High-DPI PDF", task1))
            
            # Low DPI images
            task2 = asyncio.create_task(
                client.upload_images(image_paths, dpi=100)
            )
            tasks.append(("Low-DPI Images", task2))
            
            # Wait for all uploads to complete
            print("   Starting concurrent uploads...")
            upload_responses = []
            for name, task in tasks:
                response = await task
                upload_responses.append((name, response))
                print(f"   ✓ {name} uploaded: {response.task_id}")
            
            # Wait for all tasks to complete
            print("   Waiting for all tasks to complete...")
            for name, response in upload_responses:
                result = await client.wait_for_completion(response.task_id)
                print(f"   ✓ {name} processing completed")
            
            print("\n✓ All async DPI examples completed successfully!")
            print("\nAsync DPI Benefits:")
            print("- Concurrent processing of multiple DPI settings")
            print("- Non-blocking operations for better throughput")
            print("- Efficient resource utilization")
            
    except Exception as e:
        print(f"Error: {e}")

async def example_3_task_management_async():
    """Example 3: Async task management operations."""
    print("\n" + "=" * 50)
    print("Example 3: Async Task Management")
    print("=" * 50)
    
    server_url, auth_token = get_config()
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            # Check server health
            health = await client.health_check()
            print(f"Server health: {health.status}")
            print(f"Server version: {health.version}")
            
            # List all tasks
            tasks = await client.list_tasks()
            print(f"\nTotal tasks: {tasks.total_count}")
            
            # Show recent tasks
            for task in tasks.tasks[:30]:
                print(f"Task {task.task_id[:8]}...: {task.status} - {task.filename}")
            
            # Clean up old completed tasks
            cleanup_count = 0
            for task in tasks.tasks:
                if task.status == 'completed' or task.status == 'failed':
                    delete_response = await client.delete_task(task.task_id)
                    cleanup_count += 1
                    print(f"Cleaned up task {task.task_id[:8]}...: {delete_response.status}")
            
            if cleanup_count == 0:
                print("No completed tasks to clean up.")
                    
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run all async examples."""
    print("DotsOCRRunner Python Client - Async Usage Examples")
    print("Make sure to DotsOCR server is running on http://127.0.0.1:8080")
    print("And update the auth_token variable with your actual token.\n")
    
    # Check if test assets exist
    test_assets_path = Path("../../test_assets")
    if not test_assets_path.exists():
        print(f"Warning: Test assets directory not found at {test_assets_path}")
        print("Please update file paths in examples to point to your test files.")
        return
    
    # Run examples
    examples = [
        example_1_async_pdf_ocr,
        example_2_async_custom_dpi,
        example_3_task_management_async
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except KeyboardInterrupt:
            print("\nExample interrupted by user.")
            break
        except Exception as e:
            print(f"Example failed with error: {e}")
        
        print("\n" + "-" * 30)
        await asyncio.sleep(1)  # Brief pause between examples

if __name__ == "__main__":
    asyncio.run(main())
