#!/usr/bin/env python3
"""
Document API - List Documents Example

This example demonstrates:
1. Basic document listing
2. Document listing with filters
3. Pagination handling
4. Sorting options
5. Error handling
"""

import sys
import os
import traceback
from pathlib import Path

# Add the parent directory to the path so we can import dotsocr_runner_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    DotsOCRRunnerClient, 
    setup_logging,
    APIError,
    AuthenticationError,
    ConnectionError,
    DocumentType,
    ProcessingStatus,
    SortField,
    SortOrder
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

def example_1_basic_document_listing():
    """Example 1: Basic document listing."""
    print("=" * 60)
    print("Example 1: Basic Document Listing")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Getting all documents (first page)...")
            
            # Basic document listing
            documents = client.list_documents()
            print(f"Found {len(documents.documents)} documents")
            print(f"Total documents: {documents.pagination.total_count}")
            print(f"Current page: {documents.pagination.page}")
            print(f"Page size: {documents.pagination.page_size}")
            print(f"Total pages: {documents.pagination.total_pages}")
            
            # Display document summaries
            for doc in documents.documents[:5]:  # Show first 5
                print(f"\nDocument: {doc.name}")
                print(f"  ID: {doc.id}")
                print(f"  Type: {doc.type}")
                print(f"  Status: {doc.status}")
                print(f"  Created: {doc.created_at}")
                print(f"  OCR Engine: {doc.ocr_engine}")
                
                # Show type-specific metadata
                if doc.type == "pdf":
                    metadata = doc.metadata
                    print(f"  Pages: {metadata.page_count}")
                    print(f"  Completed: {metadata.completed_pages}")
                    print(f"  File size: {metadata.file_size} bytes")
                    print(f"  Completion: {metadata.completion_rate:.1%}")
                elif doc.type == "images":
                    metadata = doc.metadata
                    print(f"  Images: {metadata.image_count}")
                    print(f"  Completed: {metadata.completed_images}")
                    print(f"  Completion: {metadata.completion_rate:.1%}")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Full error details:\n{traceback.format_exc()}")

def example_2_filtered_document_listing():
    """Example 2: Document listing with filters."""
    print("\n" + "=" * 60)
    print("Example 2: Document Listing with Filters")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating various filters...")
            
            # Filter by document type - PDFs only
            print("\n1. PDF documents only:")
            pdf_docs = client.list_documents(
                document_type=DocumentType.PDF,
                page_size=5
            )
            print(f"   Found {len(pdf_docs.documents)} PDF documents")
            for doc in pdf_docs.documents:
                print(f"   - {doc.name} ({doc.status})")
            
            # Filter by document type - Images only
            print("\n2. Image documents only:")
            image_docs = client.list_documents(
                document_type=DocumentType.IMAGES,
                page_size=5
            )
            print(f"   Found {len(image_docs.documents)} image documents")
            for doc in image_docs.documents:
                print(f"   - {doc.name} ({doc.status})")
            
            # Filter by status - Completed documents
            print("\n3. Completed documents only:")
            completed_docs = client.list_documents(
                status=ProcessingStatus.COMPLETED,
                page_size=5
            )
            print(f"   Found {len(completed_docs.documents)} completed documents")
            for doc in completed_docs.documents:
                print(f"   - {doc.name} ({doc.type})")
            
            # Filter by status - Running documents
            print("\n4. Running documents only:")
            running_docs = client.list_documents(
                status=ProcessingStatus.RUNNING,
                page_size=5
            )
            print(f"   Found {len(running_docs.documents)} running documents")
            for doc in running_docs.documents:
                print(f"   - {doc.name} ({doc.type})")
            
            # Combined filters - PDF documents that are completed
            print("\n5. Combined filter: Completed PDFs:")
            completed_pdfs = client.list_documents(
                document_type=DocumentType.PDF,
                status=ProcessingStatus.COMPLETED,
                page_size=5
            )
            print(f"   Found {len(completed_pdfs.documents)} completed PDFs")
            for doc in completed_pdfs.documents:
                print(f"   - {doc.name}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_3_pagination_and_sorting():
    """Example 3: Pagination and sorting options."""
    print("\n" + "=" * 60)
    print("Example 3: Pagination and Sorting")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating pagination and sorting...")
            
            # Get total count first
            all_docs = client.list_documents(page_size=1)
            total_count = all_docs.pagination.total_count
            print(f"Total documents in system: {total_count}")
            
            if total_count == 0:
                print("No documents found. Please upload some documents first.")
                return
            
            # Pagination example - show first few pages
            print(f"\n1. Pagination (showing first 3 pages, 3 items per page):")
            for page in range(1, min(4, all_docs.pagination.total_pages + 1)):
                page_docs = client.list_documents(
                    page=page,
                    page_size=3
                )
                print(f"\n   Page {page} ({len(page_docs.documents)} documents):")
                for doc in page_docs.documents:
                    print(f"   - {doc.name} (ID: {doc.id[:8]}...)")
            
            # Sorting by creation date (newest first)
            print(f"\n2. Sorted by creation date (newest first):")
            newest_docs = client.list_documents(
                page_size=5,
                sort_by=SortField.CREATED_AT,
                sort_order=SortOrder.DESC
            )
            for doc in newest_docs.documents:
                print(f"   - {doc.name} (Created: {doc.created_at})")
            
            # Sorting by name (alphabetical)
            print(f"\n3. Sorted by name (A-Z):")
            alpha_docs = client.list_documents(
                page_size=5,
                sort_by=SortField.NAME,
                sort_order=SortOrder.ASC
            )
            for doc in alpha_docs.documents:
                print(f"   - {doc.name}")
            
            # Sorting by status
            print(f"\n4. Sorted by status:")
            status_docs = client.list_documents(
                page_size=10,
                sort_by=SortField.STATUS,
                sort_order=SortOrder.ASC
            )
            for doc in status_docs.documents:
                print(f"   - {doc.name} ({doc.status})")
            
    except Exception as e:
        print(f"Error: {e}")

def example_4_date_range_filtering():
    """Example 4: Date range filtering."""
    print("\n" + "=" * 60)
    print("Example 4: Date Range Filtering")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating date range filtering...")
            
            # Get recent documents (last 24 hours)
            from datetime import datetime, timedelta, timezone
            
            now = datetime.now(timezone.utc)
            yesterday = now - timedelta(days=1)
            
            print(f"\n1. Documents from last 24 hours:")
            recent_docs = client.list_documents(
                date_start=yesterday.isoformat(),
                date_end=now.isoformat(),
                page_size=10
            )
            print(f"   Found {len(recent_docs.documents)} recent documents")
            for doc in recent_docs.documents:
                print(f"   - {doc.name} (Created: {doc.created_at})")
            
            # Get documents from last week
            last_week = now - timedelta(days=7)
            
            print(f"\n2. Documents from last 7 days:")
            week_docs = client.list_documents(
                date_start=last_week.isoformat(),
                date_end=now.isoformat(),
                page_size=10
            )
            print(f"   Found {len(week_docs.documents)} documents from last week")
            for doc in week_docs.documents:
                print(f"   - {doc.name} (Created: {doc.created_at})")
            
            # Get older documents (before last week)
            print(f"\n3. Older documents (before last 7 days):")
            older_docs = client.list_documents(
                date_end=last_week.isoformat(),
                page_size=10,
                sort_by=SortField.CREATED_AT,
                sort_order=SortOrder.DESC
            )
            print(f"   Found {len(older_docs.documents)} older documents")
            for doc in older_docs.documents:
                print(f"   - {doc.name} (Created: {doc.created_at})")
            
    except Exception as e:
        print(f"Error: {e}")

def example_5_error_handling():
    """Example 5: Error handling for document listing."""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating error handling...")
            
            # Test invalid document type (this will cause AttributeError before API call)
            print("\n1. Testing invalid document type:")
            try:
                invalid_docs = client.list_documents(document_type="invalid_type")
                print("   ✗ Should have failed with invalid document type")
            except AttributeError as e:
                print(f"   ✓ Correctly caught client-side error: {e}")
            except APIError as e:
                print(f"   ✓ Correctly caught API error: {e}")
            
            # Test invalid status (this will cause AttributeError before API call)
            print("\n2. Testing invalid status:")
            try:
                invalid_docs = client.list_documents(status="invalid_status")
                print("   ✗ Should have failed with invalid status")
            except AttributeError as e:
                print(f"   ✓ Correctly caught client-side error: {e}")
            except APIError as e:
                print(f"   ✓ Correctly caught API error: {e}")
            
            # Test invalid page number
            print("\n3. Testing page out of range:")
            try:
                # Get total pages first
                all_docs = client.list_documents(page_size=1)
                max_page = all_docs.pagination.total_pages + 10  # Intentionally too high
                
                out_of_range_docs = client.list_documents(page=max_page)
                print(f"   ✓ Handled out of range page gracefully: {len(out_of_range_docs.documents)} documents")
            except Exception as e:
                print(f"   ✓ Caught error for out of range page: {e}")
            
            # Test invalid date format
            print("\n4. Testing invalid date format:")
            try:
                invalid_date_docs = client.list_documents(
                    date_start="invalid-date",
                    date_end="also-invalid"
                )
                print("   ✗ Should have failed with invalid date format")
            except APIError as e:
                print(f"   ✓ Correctly caught error: {e}")
            
            # Test page size too large
            print("\n5. Testing page size limit:")
            try:
                large_page_docs = client.list_documents(page_size=200)  # Over the 100 limit
                print(f"   ✓ Page size limited to {large_page_docs.pagination.page_size}")
            except Exception as e:
                print(f"   ✓ Caught error for large page size: {e}")
            
            # Test negative page number
            print("\n6. Testing negative page number:")
            try:
                negative_page_docs = client.list_documents(page=-1)
                print("   ✗ Should have failed with negative page number")
            except APIError as e:
                print(f"   ✓ Correctly caught API error: {e}")
            except Exception as e:
                print(f"   ✓ Caught error for negative page: {e}")
            
            # Test zero page size
            print("\n7. Testing zero page size:")
            try:
                zero_page_docs = client.list_documents(page_size=0)
                print("   ✗ Should have failed with zero page size")
            except APIError as e:
                print(f"   ✓ Correctly caught API error: {e}")
            except Exception as e:
                print(f"   ✓ Caught error for zero page size: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Full error details:\n{traceback.format_exc()}")

def main():
    """Run all document listing examples."""
    print("DotsOCR Document API - List Documents Examples")
    print("Make sure DotsOCR server is running and has some documents.")
    print("Set environment variables:")
    print("  export DOTSOCR_SERVER_URL='http://127.0.0.1:8080'")
    print("  export DOTSOCR_AUTH_TOKEN='your-secret-token'")
    print()
    
    # Test server connection first
    server_url, auth_token = get_config()
    print(f"Testing connection to server at {server_url}...")
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            health = client.health_check()
            print(f"✓ Server is healthy (status: {health.status}, version: {health.version})")
            
            # Check if there are any documents
            docs = client.list_documents(page_size=1)
            if docs.pagination.total_count == 0:
                print("⚠️  No documents found. Please upload some documents first using basic OCR examples.")
                print("You can run basic_usage.py examples to create some documents.")
                return
            
    except Exception as e:
        print(f"✗ Failed to connect to server: {e}")
        print("Please make sure:")
        print("1. The DotsOCR server is running")
        print("2. The server URL is correct")
        print("3. The auth token is correct")
        return
    
    print("\nStarting document listing examples...")
    
    # Run examples
    examples = [
        ("Basic Document Listing", example_1_basic_document_listing),
        ("Filtered Document Listing", example_2_filtered_document_listing),
        ("Pagination and Sorting", example_3_pagination_and_sorting),
        ("Date Range Filtering", example_4_date_range_filtering),
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
            print(f"Full error details:\n{traceback.format_exc()}")
        
        print("\n" + "-" * 60)
    
    print("\n" + "="*60)
    print("All document listing examples completed!")
    print("="*60)

if __name__ == "__main__":
    main()
