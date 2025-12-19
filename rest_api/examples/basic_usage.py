#!/usr/bin/env python3
"""
Basic usage examples for DotsOCR Python client.

This example demonstrates:
1. Basic PDF OCR processing
2. Image batch OCR processing
3. Task management operations
4. Error handling
"""

import sys
import os
import time
from pathlib import Path

# Add the parent directory to the path so we can import dotsocr_runner_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    DotsOCRRunnerClient, 
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

def example_1_basic_pdf_ocr():
    """Example 1: Basic PDF OCR processing."""
    print("=" * 50)
    print("Example 1: Basic PDF OCR Processing")
    print("=" * 50)
    
    # Get configuration from environment variables
    server_url, auth_token = get_config()
    pdf_path = "../../test_assets/test1.pdf"  # Adjust path as needed
    
    try:
        # Create client
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print(f"Processing PDF: {pdf_path}")
            
            # Upload PDF with default DPI (150 for PDFs)
            upload_response = client.upload_pdf(pdf_path)
            print(f"Task ID: {upload_response.task_id}")
            print(f"Status: {upload_response.status}")
            print(f"Estimated duration: {upload_response.estimated_duration}")
            print(f"Used default DPI: 150 (PDF default)")
            
            # Wait for completion with progress callback
            def progress_callback(progress, message):
                print(f"Progress: {progress:.1f}% - {message}")
            
            result = client.wait_for_completion(
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
            
            print(f"Metadata: {result.metadata}")
            
    except AuthenticationError:
        print("Authentication failed. Please check your auth token.")
    except ConnectionError:
        print("Failed to connect to server. Please ensure the server is running.")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def example_2_image_batch_ocr():
    """Example 2: Image batch OCR processing."""
    print("\n" + "=" * 50)
    print("Example 2: Image Batch OCR Processing")
    print("=" * 50)
    
    server_url, auth_token = get_config()
    image_paths = [
        "../../test_assets/pic1.png",
        "../../test_assets/pic2.png"
    ]
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print(f"Processing {len(image_paths)} images...")
            
            # Upload images with default DPI (72 for images)
            upload_response = client.upload_images(image_paths)
            print(f"Task ID: {upload_response.task_id}")
            print(f"Status: {upload_response.status}")
            print(f"Used default DPI: 72 (image default)")
            
            # Monitor progress
            while True:
                status = client.get_task_status(upload_response.task_id)
                print(f"Status: {status.status} - Progress: {status.progress:.1f}%")
                
                if status.status == 'completed':
                    result = client.get_task_result(upload_response.task_id)
                    print(f"\nOCR completed successfully!")
                    
                    # Handle different result structures
                    if result.result.get('type') == 'pdf':
                        pages = result.result.get('pages', [])
                        if pages:
                            first_page_content = pages[0].get('content', '')
                            print(f"Content preview (Page 1): {first_page_content[:200]}...")
                            print(f"Total pages: {result.result.get('page_count', 0)}")
                        else:
                            print("No pages found in result")
                    elif result.result.get('type') == 'batch_images':
                        images = result.result.get('images', [])
                        if images:
                            first_image_content = images[0].get('content', '')
                            print(f"Content preview (Image 1): {first_image_content[:200]}...")
                            print(f"Total images: {result.result.get('image_count', 0)}")
                        else:
                            print("No images found in result")
                    else:
                        print(f"Result: {result.result}")
                    break
                elif status.status == 'failed':
                    print(f"Task failed")
                    break
                
                time.sleep(2)
                
    except Exception as e:
        print(f"Error: {e}")

def example_3_task_management():
    """Example 3: Task management operations."""
    print("\n" + "=" * 50)
    print("Example 3: Task Management")
    print("=" * 50)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            # Check server health
            health = client.health_check()
            print(f"Server health: {health.status}")
            print(f"Server version: {health.version}")
            
            # List all tasks
            tasks = client.list_tasks()
            print(f"\nTotal tasks: {tasks.total_count}")
            
            for task in tasks.tasks[:5]:  # Show first 5 tasks
                print(f"Task {task.task_id}: {task.status} - {task.filename}")
            
            # Clean up: delete old completed tasks
            for task in tasks.tasks:
                if task.status == 'completed':
                    delete_response = client.delete_task(task.task_id)
                    print(f"Deleted task {task.task_id}: {delete_response.status}")
                    
    except Exception as e:
        print(f"Error: {e}")


def example_4_custom_dpi():
    """Example 4: Custom DPI usage."""
    print("\n" + "=" * 50)
    print("Example 4: Custom DPI Usage")
    print("=" * 50)
    
    server_url, auth_token = get_config()
    pdf_path = "../../test_assets/test1.pdf"
    image_paths = [
        "../../test_assets/pic1.png",
        "../../test_assets/pic2.png"
    ]
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating custom DPI settings...")
            
            # Example 1: PDF with high DPI for better quality (within valid range)
            print("\n1. PDF with high DPI (200) for maximum quality:")
            try:
                upload_response = client.upload_pdf(pdf_path, dpi=200)
                print(f"   Task ID: {upload_response.task_id}")
                print(f"   Used custom DPI: 200")
                
                # Wait for completion
                result = client.wait_for_completion(upload_response.task_id)
                print(f"   ✓ High-DPI PDF processing completed")
            except Exception as e:
                print(f"   ✗ High-DPI PDF processing failed: {e}")
            
            # Example 2: Images with medium DPI
            print("\n2. Images with medium DPI (150) for balanced quality:")
            try:
                upload_response = client.upload_images(image_paths, dpi=150)
                print(f"   Task ID: {upload_response.task_id}")
                print(f"   Used custom DPI: 150")
                
                # Wait for completion
                result = client.wait_for_completion(upload_response.task_id)
                print(f"   ✓ Medium-DPI image processing completed")
            except Exception as e:
                print(f"   ✗ Medium-DPI image processing failed: {e}")
            
            # Example 3: Images with low DPI for faster processing
            print("\n3. Images with low DPI (100) for faster processing:")
            try:
                upload_response = client.upload_images(image_paths, dpi=100)
                print(f"   Task ID: {upload_response.task_id}")
                print(f"   Used custom DPI: 100")
                
                # Wait for completion
                result = client.wait_for_completion(upload_response.task_id)
                print(f"   ✓ Low-DPI image processing completed")
            except Exception as e:
                print(f"   ✗ Low-DPI image processing failed: {e}")
            
            print("\n✓ All DPI examples completed!")
            print("\nDPI Guidelines:")
            print("- PDFs: Default 150, High quality 200, Fast processing 100")
            print("- Images: Default 72, High quality 150-200, Fast processing 72-100")
            print("- Valid range: 72-200 DPI")
            
    except Exception as e:
        print(f"Error: {e}")

def example_5_error_handling():
    """Example 5: Comprehensive error handling."""
    print("\n" + "=" * 50)
    print("Example 5: Error Handling")
    print("=" * 50)
    
    server_url, _ = get_config()  # Get server URL from env
    auth_token = "invalid-token"  # Invalid token for demonstration
    file_path = "../../test_assets/test1.pdf"
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            upload_response = client.upload_pdf(file_path)
            result = client.wait_for_completion(upload_response.task_id)
            
    except AuthenticationError:
        print("✓ Authentication error caught correctly")
    except ConnectionError:
        print("✓ Connection error caught correctly")
    except APIError as e:
        print(f"✓ API error caught: {e}")
    except Exception as e:
        print(f"✓ Other error caught: {e}")

def main():
    """Run all examples."""
    print("DotsOCRRunner Python Client - Basic Usage Examples")
    print("Make sure the DotsOCR server is running.")
    print("Set environment variables:")
    print("  export DOTSOCR_SERVER_URL='http://127.0.0.1:8080'")
    print("  export DOTSOCR_AUTH_TOKEN='your-secret-token'")
    print("Or the examples will use default values.\n")
    
    # Check if test assets exist
    test_assets_path = Path("../../test_assets")
    if not test_assets_path.exists():
        print(f"Warning: Test assets directory not found at {test_assets_path}")
        print("Please update the file paths in the examples to point to your test files.")
        print("You can also run the examples from the rest_api/examples directory.")
        return
    
    # Test server connection first
    server_url, auth_token = get_config()
    print(f"Testing connection to server at {server_url}...")
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            health = client.health_check()
            print(f"✓ Server is healthy (status: {health.status}, version: {health.version})")
    except Exception as e:
        print(f"✗ Failed to connect to server: {e}")
        print("Please make sure:")
        print("1. The DotsOCR server is running")
        print("2. The server URL is correct (default: http://127.0.0.1:8080)")
        print("3. The auth token is correct")
        print("4. No firewall is blocking the connection")
        return
    
    print("\nStarting examples...")
    
    # Run examples
    examples = [
        ("Basic PDF OCR", example_1_basic_pdf_ocr),
        ("Image Batch OCR", example_2_image_batch_ocr),
        ("Task Management", example_3_task_management),
        ("Custom DPI Usage", example_4_custom_dpi),
        ("Error Handling", example_5_error_handling)
    ]
    
    for example_name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {example_name}")
            print('='*60)
            example_func()
            print(f"✓ {example_name} completed successfully")
        except KeyboardInterrupt:
            print(f"\n{example_name} interrupted by user.")
            break
        except Exception as e:
            print(f"✗ {example_name} failed with error: {e}")
            import traceback
            print(f"Full error details:\n{traceback.format_exc()}")
        
        print("\n" + "-" * 60)
        time.sleep(2)  # Brief pause between examples
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)

if __name__ == "__main__":
    main()
