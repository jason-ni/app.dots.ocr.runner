#!/usr/bin/env python3
"""
Document API - Document Management Example

This example demonstrates:
1. Document details retrieval
2. Document deletion
3. Document export in various formats
4. Complete document lifecycle management
5. Error handling for document operations
"""

import sys
import os
import tempfile
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
    ProcessingStatus,
    ExportFormat
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

def example_1_document_details_retrieval():
    """Example 1: Get detailed document information."""
    print("=" * 60)
    print("Example 1: Document Details Retrieval")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Retrieving document details...")
            
            # Get a list of documents first
            documents = client.list_documents(page_size=5)
            
            if documents.pagination.total_count == 0:
                print("No documents found. Please upload some documents first.")
                return
            
            print(f"Found {documents.pagination.total_count} documents")
            
            # Get details for each document
            for doc in documents.documents:
                print(f"\n--- Details for document: {doc.name} ---")
                print(f"Document ID: {doc.id}")
                print(f"Type: {doc.type}")
                print(f"Status: {doc.status}")
                
                try:
                    # Get detailed information
                    details = client.get_document_details(doc.id)
                    
                    print(f"Created: {details.base.created_at}")
                    print(f"Updated: {details.base.updated_at}")
                    print(f"OCR Engine: {details.base.ocr_engine}")
                    
                    # Show base metadata
                    base_metadata = details.base.metadata
                    if details.base.type == "pdf":
                        print(f"PDF Metadata:")
                        print(f"  Page count: {base_metadata.page_count}")
                        print(f"  Completed pages: {base_metadata.completed_pages}")
                        print(f"  File size: {base_metadata.file_size} bytes")
                        print(f"  Completion rate: {base_metadata.completion_rate:.1%}")
                    elif details.base.type == "images":
                        print(f"Image Batch Metadata:")
                        print(f"  Image count: {base_metadata.image_count}")
                        print(f"  Completed images: {base_metadata.completed_images}")
                        print(f"  Completion rate: {base_metadata.completion_rate:.1%}")
                    
                    # Show content information
                    content = details.content
                    if details.base.type == "pdf" and hasattr(content, 'pages'):
                        print(f"Content: {len(content.pages)} pages")
                        for i, page in enumerate(content.pages[:3]):  # Show first 3 pages
                            has_content = page.has_result and page.content
                            print(f"  Page {page.page_num}: {'✓' if has_content else '✗'}")
                            if has_content and page.content:
                                preview = page.content[:100].replace('\n', ' ')
                                print(f"    Preview: {preview}...")
                    elif details.base.type == "images" and hasattr(content, 'images'):
                        print(f"Content: {len(content.images)} images")
                        for i, img in enumerate(content.images[:3]):  # Show first 3 images
                            has_content = img.has_result and img.content
                            print(f"  Image {img.id} ({img.file_name}): {'✓' if has_content else '✗'}")
                            if has_content and img.content:
                                preview = img.content[:100].replace('\n', ' ')
                                print(f"    Preview: {preview}...")
                    
                except APIError as e:
                    print(f"Error getting details: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    print(f"Full error details:\n{traceback.format_exc()}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_2_document_export_formats():
    """Example 2: Export documents in different formats."""
    print("\n" + "=" * 60)
    print("Example 2: Document Export Formats")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Exporting documents in different formats...")
            
            # Get a completed document for export
            documents = client.list_documents(
                status=ProcessingStatus.COMPLETED,
                page_size=3
            )
            
            if documents.pagination.total_count == 0:
                print("No completed documents found for export.")
                return
            
            # Use the first completed document
            doc = documents.documents[0]
            print(f"Exporting document: {doc.name} (ID: {doc.id})")
            
            # Note: The REST API only supports JSON export format
            # The UI uses markdown export through separate endpoints
            # Export formats to test
            export_formats = ["json"]
            
            for format_type in export_formats:
                print(f"\n--- Exporting as {format_type.upper()} ---")
                
                try:
                    # Create temporary file for export
                    with tempfile.NamedTemporaryFile(
                        mode='wb',
                        suffix=f'.{format_type}',
                        delete=False
                    ) as temp_file:
                        temp_path = temp_file.name
                    
                    # Export document
                    export_response = client.export_document(
                        document_id=doc.id,
                        export_format=ExportFormat.JSON
                    )
                    
                    # Save to temporary file
                    with open(temp_path, 'wb') as f:
                        f.write(export_response.content)
                    
                    # Show file info
                    file_size = os.path.getsize(temp_path)
                    print(f"✓ Export successful")
                    print(f"  File size: {file_size} bytes")
                    print(f"  Content type: {export_response.content_type}")
                    print(f"  Saved to: {temp_path}")
                    
                    # Show preview for text-based formats
                    if format_type in ["json"]:
                        try:
                            with open(temp_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            preview = content[:200].replace('\n', ' ')
                            print(f"  Preview: {preview}...")
                        except UnicodeDecodeError:
                            print(f"  Preview: Binary content")
                    
                    # Clean up
                    os.unlink(temp_path)
                    
                except APIError as e:
                    print(f"✗ Export failed: {e}")
                except Exception as e:
                    print(f"✗ Unexpected error: {e}")
                    print(f"Full error details:\n{traceback.format_exc()}")
            
            # Note about markdown export
            print(f"\n--- Note about Markdown Export ---")
            print("Markdown export is handled through separate UI-specific endpoints:")
            print("- export_batch_images_to_markdown() for image batches")
            print("- export_pdf_file_to_markdown() for PDF files")
            print("These are not available through the REST API export endpoint.")
            
    except Exception as e:
        print(f"Error: {e}")

def example_3_document_deletion():
    """Example 3: Document deletion operations."""
    print("\n" + "=" * 60)
    print("Example 3: Document Deletion")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating document deletion...")
            
            # Get documents for potential deletion
            documents = client.list_documents(page_size=10)
            
            if documents.pagination.total_count == 0:
                print("No documents found.")
                return
            
            print(f"Found {documents.pagination.total_count} documents")
            
            # Show documents with their status
            print("\nAvailable documents:")
            for i, doc in enumerate(documents.documents):
                print(f"  {i+1}. {doc.name} ({doc.type}, {doc.status}) - ID: {doc.id[:8]}...")
            
            # For demonstration, we'll show how to delete documents
            # In a real scenario, you might want to be more selective
            print("\n--- Deletion Examples ---")
            
            # Example 1: Try to delete a completed document
            completed_docs = [doc for doc in documents.documents if doc.status == ProcessingStatus.COMPLETED.value]
            if completed_docs:
                doc_to_delete = completed_docs[0]
                print(f"\n1. Deleting completed document: {doc_to_delete.name}")
                
                try:
                    delete_response = client.delete_document(doc_to_delete.id)
                    print(f"✓ Delete successful: {delete_response.status}")
                    print(f"  Message: {delete_response.message}")
                    print(f"  Document ID: {delete_response.id}")
                except APIError as e:
                    print(f"✗ Delete failed: {e}")
            else:
                print("\n1. No completed documents available for deletion example")
            
            # Example 2: Try to delete a failed document
            failed_docs = [doc for doc in documents.documents if doc.status == ProcessingStatus.ERROR.value]
            if failed_docs:
                doc_to_delete = failed_docs[0]
                print(f"\n2. Deleting failed document: {doc_to_delete.name}")
                
                try:
                    delete_response = client.delete_document(doc_to_delete.id)
                    print(f"✓ Delete successful: {delete_response.status}")
                    print(f"  Message: {delete_response.message}")
                except APIError as e:
                    print(f"✗ Delete failed: {e}")
            else:
                print("\n2. No failed documents available for deletion example")
            
            # Example 3: Try to delete a running document (should fail or be handled carefully)
            running_docs = [doc for doc in documents.documents if doc.status == ProcessingStatus.RUNNING.value]
            if running_docs:
                doc_to_delete = running_docs[0]
                print(f"\n3. Attempting to delete running document: {doc_to_delete.name}")
                print("   (This might be prevented by the system)")
                
                try:
                    delete_response = client.delete_document(doc_to_delete.id)
                    print(f"✓ Delete successful: {delete_response.status}")
                except APIError as e:
                    print(f"✗ Delete failed (expected): {e}")
            else:
                print("\n3. No running documents available for deletion example")
            
    except Exception as e:
        print(f"Error: {e}")

def example_4_document_lifecycle_management():
    """Example 4: Complete document lifecycle management."""
    print("\n" + "=" * 60)
    print("Example 4: Document Lifecycle Management")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating complete document lifecycle...")
            
            # Step 1: Get overview of all documents
            print("\n--- Step 1: Document Overview ---")
            all_docs = client.list_documents(page_size=20)
            print(f"Total documents: {all_docs.pagination.total_count}")
            
            # Group by status
            status_counts = {}
            type_counts = {}
            
            for doc in all_docs.documents:
                status_counts[doc.status] = status_counts.get(doc.status, 0) + 1
                type_counts[doc.type] = type_counts.get(doc.type, 0) + 1
            
            print("By status:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            print("By type:")
            for doc_type, count in type_counts.items():
                print(f"  {doc_type}: {count}")
            
            # Step 2: Analyze completed documents
            print("\n--- Step 2: Analyze Completed Documents ---")
            completed_docs = client.list_documents(
                status=ProcessingStatus.COMPLETED,
                page_size=10
            )
            
            if completed_docs.documents:
                print(f"Found {len(completed_docs.documents)} completed documents")
                
                for doc in completed_docs.documents[:3]:  # Analyze first 3
                    print(f"\nAnalyzing: {doc.name}")
                    
                    # Get detailed information
                    details = client.get_document_details(doc.id)
                    
                    # Export summary
                    print("  Export capabilities:")
                    for format_type in ["json"]:
                        try:
                            export_response = client.export_document(
                                document_id=doc.id,
                                export_format=ExportFormat.JSON
                            )
                            print(f"    {format_type}: ✓ ({len(export_response.content)} bytes)")
                        except APIError:
                            print(f"    {format_type}: ✗")
                    
                    print("    markdown: ✓ (via separate UI endpoints)")
            
            # Step 3: Cleanup old/failed documents
            print("\n--- Step 3: Cleanup Operations ---")
            
            # Find old failed documents
            failed_docs = client.list_documents(
                status=ProcessingStatus.ERROR,
                page_size=10
            )
            
            if failed_docs.documents:
                print(f"Found {len(failed_docs.documents)} failed documents")
                
                # In a real scenario, you might want to delete old failed documents
                # For this example, we'll just show what we would do
                print("Documents that could be cleaned up:")
                for doc in failed_docs.documents:
                    print(f"  - {doc.name} (ID: {doc.id[:8]}...)")
                    # Uncomment the following lines to actually delete:
                    # try:
                    #     client.delete_document(doc.id)
                    #     print(f"    ✓ Deleted")
                    # except APIError as e:
                    #     print(f"    ✗ Delete failed: {e}")
            else:
                print("No failed documents to clean up")
            
            # Step 4: Storage analysis
            print("\n--- Step 4: Storage Analysis ---")
            
            total_size = 0
            document_sizes = []
            
            for doc in all_docs.documents:
                try:
                    details = client.get_document_details(doc.id)
                    metadata = details.base.metadata
                    
                    if hasattr(metadata, 'file_size'):
                        size = metadata.file_size
                        total_size += size
                        document_sizes.append((doc.name, size))
                except APIError:
                    # Skip documents we can't get details for
                    pass
            
            if document_sizes:
                print(f"Total storage used: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
                
                # Show largest documents
                document_sizes.sort(key=lambda x: x[1], reverse=True)
                print("\nLargest documents:")
                for name, size in document_sizes[:5]:
                    print(f"  {name}: {size:,} bytes ({size / 1024:.1f} KB)")
            
    except Exception as e:
        print(f"Error: {e}")

def example_5_error_handling():
    """Example 5: Comprehensive error handling."""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating error handling for document operations...")
            
            # Test 1: Get details for non-existent document
            print("\n1. Testing non-existent document ID:")
            try:
                fake_id = "nonexistent-document-id-12345"
                details = client.get_document_details(fake_id)
                print("   ✗ Should have failed with non-existent document")
            except APIError as e:
                print(f"   ✓ Correctly caught error: {e}")
            
            # Test 2: Delete non-existent document
            print("\n2. Testing delete non-existent document:")
            try:
                fake_id = "nonexistent-document-id-67890"
                delete_response = client.delete_document(fake_id)
                print("   ✗ Should have failed with non-existent document")
            except APIError as e:
                print(f"   ✓ Correctly caught error: {e}")
            
            # Test 3: Export non-existent document
            print("\n3. Testing export non-existent document:")
            try:
                fake_id = "nonexistent-document-id-abcde"
                export_response = client.export_document(
                    document_id=fake_id,
                    export_format=ExportFormat.JSON
                )
                print("   ✗ Should have failed with non-existent document")
            except APIError as e:
                print(f"   ✓ Correctly caught error: {e}")
            
            # Test 4: Invalid export format
            print("\n4. Testing invalid export format:")
            # Get a real document first
            documents = client.list_documents(page_size=1)
            if documents.documents:
                real_doc = documents.documents[0]
                try:
                    export_response = client.export_document(
                        document_id=real_doc.id,
                        export_format="invalid_format"
                    )
                    print("   ✗ Should have failed with invalid format")
                except APIError as e:
                    print(f"   ✓ Correctly caught error: {e}")
            else:
                print("   No documents available to test invalid format")
            
            # Test 5: Invalid document ID format
            print("\n5. Testing invalid document ID formats:")
            invalid_ids = [
                "",
                "too-short",
                "with spaces",
                "with/slash",
                "with\nnewline"
            ]
            
            for invalid_id in invalid_ids:
                try:
                    details = client.get_document_details(invalid_id)
                    print(f"   ✗ Should have failed with invalid ID: '{invalid_id}'")
                except APIError as e:
                    print(f"   ✓ Correctly caught error for '{invalid_id}': {e}")
                except Exception as e:
                    print(f"   ✓ Caught other error for '{invalid_id}': {e}")
            
            # Test 6: Network connectivity issues (simulation)
            print("\n6. Testing network error handling:")
            # This would require actual network failure, so we'll just show the pattern
            print("   Network errors would be caught as ConnectionError")
            print("   Example handling pattern:")
            print("   try:")
            print("       client.get_document_details(doc_id)")
            print("   except ConnectionError:")
            print("       print('Network connection failed')")
            print("   except APIError as e:")
            print("       print(f'API error: {e}')")
            
    except Exception as e:
        print(f"Error: {e}")

def example_6_batch_operations():
    """Example 6: Batch document operations."""
    print("\n" + "=" * 60)
    print("Example 6: Batch Operations")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating batch document operations...")
            
            # Get all documents
            all_docs = client.list_documents(page_size=50)
            
            if all_docs.pagination.total_count == 0:
                print("No documents found for batch operations.")
                return
            
            print(f"Processing {all_docs.pagination.total_count} documents")
            
            # Batch operation 1: Export all completed documents as JSON
            print("\n--- Batch Export: All Completed Documents as JSON ---")
            completed_docs = [doc for doc in all_docs.documents if doc.status == ProcessingStatus.COMPLETED.value]
            
            if completed_docs:
                print(f"Found {len(completed_docs)} completed documents")
                
                export_results = []
                for doc in completed_docs[:5]:  # Limit to first 5 for demo
                    try:
                        export_response = client.export_document(
                            document_id=doc.id,
                            export_format=ExportFormat.JSON
                        )
                        export_results.append({
                            'document_id': doc.id,
                            'name': doc.name,
                            'size': len(export_response.content),
                            'success': True
                        })
                        print(f"  ✓ {doc.name}: {len(export_response.content)} bytes")
                    except APIError as e:
                        export_results.append({
                            'document_id': doc.id,
                            'name': doc.name,
                            'error': str(e),
                            'success': False
                        })
                        print(f"  ✗ {doc.name}: {e}")
                
                # Summary
                successful = sum(1 for r in export_results if r['success'])
                print(f"\nBatch export summary: {successful}/{len(export_results)} successful")
            else:
                print("No completed documents to export")
            
            # Batch operation 2: Get details for all documents of a specific type
            print("\n--- Batch Details: All PDF Documents ---")
            pdf_docs = [doc for doc in all_docs.documents if doc.type == "pdf"]
            
            if pdf_docs:
                print(f"Found {len(pdf_docs)} PDF documents")
                
                details_results = []
                for doc in pdf_docs[:5]:  # Limit to first 5 for demo
                    try:
                        details = client.get_document_details(doc.id)
                        metadata = details.base.metadata
                        details_results.append({
                            'document_id': doc.id,
                            'name': doc.name,
                            'page_count': metadata.page_count,
                            'completed_pages': metadata.completed_pages,
                            'completion_rate': metadata.completion_rate,
                            'success': True
                        })
                        print(f"  ✓ {doc.name}: {metadata.completed_pages}/{metadata.page_count} pages")
                    except APIError as e:
                        details_results.append({
                            'document_id': doc.id,
                            'name': doc.name,
                            'error': str(e),
                            'success': False
                        })
                        print(f"  ✗ {doc.name}: {e}")
                
                # Summary statistics
                successful = [r for r in details_results if r['success']]
                if successful:
                    total_pages = sum(r['page_count'] for r in successful)
                    total_completed = sum(r['completed_pages'] for r in successful)
                    avg_completion = sum(r['completion_rate'] for r in successful) / len(successful)
                    
                    print(f"\nPDF batch summary:")
                    print(f"  Documents: {len(successful)}")
                    print(f"  Total pages: {total_pages}")
                    print(f"  Completed pages: {total_completed}")
                    print(f"  Average completion: {avg_completion:.1%}")
            else:
                print("No PDF documents found")
            
            # Batch operation 3: Cleanup old failed documents
            print("\n--- Batch Cleanup: Old Failed Documents ---")
            failed_docs = [doc for doc in all_docs.documents if doc.status == ProcessingStatus.ERROR.value]
            
            if failed_docs:
                print(f"Found {len(failed_docs)} failed documents")
                print("Documents that could be cleaned up (not actually deleting in demo):")
                
                for doc in failed_docs:
                    print(f"  - {doc.name} (ID: {doc.id[:8]}...)")
                    # In a real scenario, you might uncomment:
                    # try:
                    #     client.delete_document(doc.id)
                    #     print(f"    ✓ Deleted")
                    # except APIError as e:
                    #     print(f"    ✗ Delete failed: {e}")
            else:
                print("No failed documents to clean up")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all document management examples."""
    print("DotsOCR Document API - Document Management Examples")
    print("Make sure DotsOCR server is running and has some documents.")
    print("Set environment variables:")
    print("  export DOTSOCR_SERVER_URL='http://127.0.0.1:8080'")
    print("  export DOTSOCR_AUTH_TOKEN='your-secret-token'")
    print()
    print("⚠️  WARNING: This example includes document deletion operations!")
    print("   Use with caution and backup important documents.")
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
    
    print("\nStarting document management examples...")
    
    # Run examples
    examples = [
        ("Document Details Retrieval", example_1_document_details_retrieval),
        ("Document Export Formats", example_2_document_export_formats),
        ("Document Deletion", example_3_document_deletion),
        ("Document Lifecycle Management", example_4_document_lifecycle_management),
        ("Error Handling", example_5_error_handling),
        ("Batch Operations", example_6_batch_operations)
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
    
    print("\n" + "="*60)
    print("All document management examples completed!")
    print("="*60)

if __name__ == "__main__":
    main()
