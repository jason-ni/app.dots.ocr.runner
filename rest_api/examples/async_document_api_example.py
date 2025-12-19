#!/usr/bin/env python3
"""
Async Document API Examples for DotsOCR Python Client.

This example demonstrates async usage of the Document API:
1. Async document listing with filters and pagination
2. Async document search across different scopes
3. Async document details retrieval
4. Async document export in various formats
5. Async document deletion and lifecycle management
6. Async batch operations and concurrent processing
7. Comprehensive async error handling
"""

import asyncio
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

# Add parent directory to the path so we can import dotsocr_runner_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    AsyncDotsOCRRunnerClient,
    setup_logging,
    APIError,
    AuthenticationError,
    ConnectionError,
    DocumentType,
    ProcessingStatus,
    SortField,
    SortOrder,
    SearchScope,
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

async def example_1_async_document_listing():
    """Example 1: Async document listing with filters and pagination."""
    print("=" * 60)
    print("Async Example 1: Document Listing with Filters")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating async document listing...")
            
            # Basic document listing
            print("\n1. Basic document listing:")
            documents = await client.list_documents()
            print(f"   Found {len(documents.documents)} documents")
            print(f"   Total documents: {documents.pagination.total_count}")
            
            # Concurrent filtering with different document types
            print("\n2. Concurrent filtering by document type:")
            
            async def get_documents_by_type(doc_type):
                try:
                    docs = await client.list_documents(
                        document_type=doc_type,
                        page_size=5
                    )
                    return doc_type, docs
                except Exception as e:
                    return doc_type, None
            
            # Run filters concurrently
            tasks = [
                get_documents_by_type(DocumentType.PDF),
                get_documents_by_type(DocumentType.IMAGES)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    doc_type, docs = result
                    if docs:
                        print(f"   {doc_type.value}: {len(docs.documents)} documents")
                        for doc in docs.documents[:3]:
                            print(f"     - {doc.name} ({doc.status})")
                    else:
                        print(f"   {doc_type.value}: No documents found")
            
            # Concurrent filtering by status
            print("\n3. Concurrent filtering by status:")
            
            async def get_documents_by_status(status):
                try:
                    docs = await client.list_documents(
                        status=status,
                        page_size=3
                    )
                    return status, docs
                except Exception as e:
                    return status, None
            
            status_tasks = [
                get_documents_by_status(ProcessingStatus.COMPLETED),
                get_documents_by_status(ProcessingStatus.RUNNING),
                get_documents_by_status(ProcessingStatus.ERROR)
            ]
            
            status_results = await asyncio.gather(*status_tasks, return_exceptions=True)
            
            for result in status_results:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    status, docs = result
                    if docs:
                        print(f"   {status.value}: {len(docs.documents)} documents")
                        for doc in docs.documents:
                            print(f"     - {doc.name} ({doc.type})")
                    else:
                        print(f"   {status.value}: No documents found")
            
            # Pagination with concurrent page fetching
            print("\n4. Concurrent pagination:")
            
            if documents.pagination.total_pages > 1:
                pages_to_fetch = min(3, documents.pagination.total_pages)
                
                async def get_page(page_num):
                    try:
                        page_docs = await client.list_documents(
                            page=page_num,
                            page_size=3
                        )
                        return page_num, page_docs
                    except Exception as e:
                        return page_num, None
                
                page_tasks = [get_page(i) for i in range(1, pages_to_fetch + 1)]
                page_results = await asyncio.gather(*page_tasks, return_exceptions=True)
                
                for result in page_results:
                    if isinstance(result, Exception):
                        print(f"   Error fetching page: {result}")
                    else:
                        page_num, page_docs = result
                        if page_docs:
                            print(f"   Page {page_num}: {len(page_docs.documents)} documents")
                            for doc in page_docs.documents:
                                print(f"     - {doc.name}")
                        else:
                            print(f"   Page {page_num}: No documents")
            else:
                print("   Not enough pages for pagination demo")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Full error details:\n{traceback.format_exc()}")

async def example_2_async_document_search():
    """Example 2: Async document search with concurrent operations."""
    print("\n" + "=" * 60)
    print("Async Example 2: Document Search with Concurrency")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating async document search...")
            
            # Get some documents for search reference
            all_docs = await client.list_documents(page_size=10)
            if all_docs.pagination.total_count == 0:
                print("No documents found for search examples.")
                return
            
            print(f"Found {all_docs.pagination.total_count} documents for searching")
            
            # Common search terms
            search_terms = ["test", "document", "pdf", "image", "ocr"]
            
            # Concurrent search across different scopes
            print("\n1. Concurrent search across scopes:")
            
            async def search_with_scope(term, scope):
                try:
                    results = await client.search_documents(
                        query=term,
                        scope=scope,
                        page_size=5
                    )
                    return term, scope, results
                except Exception as e:
                    return term, scope, None
            
            # Create search tasks for different terms and scopes
            search_tasks = []
            for term in search_terms:
                for scope in [SearchScope.FILENAMES, SearchScope.CONTENT, SearchScope.BOTH]:
                    search_tasks.append(search_with_scope(term, scope))
            
            # Run all searches concurrently
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Group results by term
            results_by_term = {}
            for result in search_results:
                if isinstance(result, Exception):
                    print(f"   Search error: {result}")
                    continue
                
                term, scope, docs = result
                if term not in results_by_term:
                    results_by_term[term] = {}
                results_by_term[term][scope] = docs
            
            # Display results
            for term, scope_results in results_by_term.items():
                print(f"\n   Search term: '{term}'")
                for scope, docs in scope_results.items():
                    if docs:
                        print(f"     {scope.value}: {len(docs.documents)} matches")
                        for doc in docs.documents[:2]:
                            print(f"       - {doc.name}")
                    else:
                        print(f"     {scope.value}: No results")
            
            # Performance comparison with concurrent searches
            print("\n2. Performance comparison:")
            
            test_query = "document"
            
            # Sequential search
            start_time = time.time()
            for scope in [SearchScope.FILENAMES, SearchScope.CONTENT, SearchScope.BOTH]:
                await client.search_documents(query=test_query, scope=scope)
            sequential_time = time.time() - start_time
            
            # Concurrent search
            start_time = time.time()
            concurrent_tasks = [
                client.search_documents(query=test_query, scope=scope)
                for scope in [SearchScope.FILENAMES, SearchScope.CONTENT, SearchScope.BOTH]
            ]
            await asyncio.gather(*concurrent_tasks)
            concurrent_time = time.time() - start_time
            
            print(f"   Sequential search time: {sequential_time:.3f}s")
            print(f"   Concurrent search time: {concurrent_time:.3f}s")
            print(f"   Performance improvement: {sequential_time/concurrent_time:.2f}x")
            
            # Batch search with multiple terms
            print("\n3. Batch search with multiple terms:")
            
            batch_terms = ["report", "analysis", "data"][:2]  # Limit for demo
            
            async def batch_search(term):
                try:
                    results = await client.search_documents(
                        query=term,
                        scope=SearchScope.BOTH,
                        page_size=3
                    )
                    return term, results
                except Exception as e:
                    return term, None
            
            batch_tasks = [batch_search(term) for term in batch_terms]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"   Batch search error: {result}")
                else:
                    term, docs = result
                    if docs:
                        print(f"   '{term}': {len(docs.documents)} documents")
                        for doc in docs.documents:
                            print(f"     - {doc.name}")
                    else:
                        print(f"   '{term}': No results")
            
    except Exception as e:
        print(f"Error: {e}")

async def example_3_async_document_details():
    """Example 3: Async document details retrieval with concurrent processing."""
    print("\n" + "=" * 60)
    print("Async Example 3: Document Details Retrieval")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating async document details retrieval...")
            
            # Get documents for details retrieval
            documents = await client.list_documents(page_size=5)
            
            if documents.pagination.total_count == 0:
                print("No documents found for details examples.")
                return
            
            print(f"Found {len(documents.documents)} documents")
            
            # Concurrent details retrieval
            print("\n1. Concurrent details retrieval:")
            
            async def get_document_details_with_timing(doc):
                start_time = time.time()
                try:
                    details = await client.get_document_details(doc.id)
                    end_time = time.time()
                    return doc, details, end_time - start_time
                except Exception as e:
                    end_time = time.time()
                    return doc, None, end_time - start_time
            
            # Get details for all documents concurrently
            detail_tasks = [get_document_details_with_timing(doc) for doc in documents.documents]
            detail_results = await asyncio.gather(*detail_tasks, return_exceptions=True)
            
            total_time = 0
            successful_retrievals = 0
            
            for result in detail_results:
                if isinstance(result, Exception):
                    print(f"   Error retrieving details: {result}")
                    continue
                
                doc, details, elapsed_time = result
                total_time += elapsed_time
                
                if details:
                    successful_retrievals += 1
                    print(f"\n   Document: {doc.name}")
                    print(f"     Retrieval time: {elapsed_time:.3f}s")
                    print(f"     Type: {details.base.type}")
                    print(f"     Status: {details.base.status}")
                    print(f"     OCR Engine: {details.base.ocr_engine}")
                    
                    # Show type-specific metadata
                    metadata = details.base.metadata
                    if details.base.type == "pdf":
                        print(f"     Pages: {metadata.page_count}")
                        print(f"     Completed: {metadata.completed_pages}")
                        print(f"     Completion: {metadata.completion_rate:.1%}")
                    elif details.base.type == "images":
                        print(f"     Images: {metadata.image_count}")
                        print(f"     Completed: {metadata.completed_images}")
                        print(f"     Completion: {metadata.completion_rate:.1%}")
                    
                    # Show content preview
                    if details.base.type == "pdf" and hasattr(details.content, 'pages'):
                        pages_with_content = [p for p in details.content.pages if p.has_result]
                        print(f"     Pages with content: {len(pages_with_content)}")
                        if pages_with_content:
                            first_page = pages_with_content[0]
                            preview = first_page.content[:100].replace('\n', ' ') if first_page.content else "No content"
                            print(f"     Preview: {preview}...")
                    elif details.base.type == "images" and hasattr(details.content, 'images'):
                        images_with_content = [img for img in details.content.images if img.has_result]
                        print(f"     Images with content: {len(images_with_content)}")
                        if images_with_content:
                            first_image = images_with_content[0]
                            preview = first_image.content[:100].replace('\n', ' ') if first_image.content else "No content"
                            print(f"     Preview: {preview}...")
                else:
                    print(f"   Failed to retrieve details for {doc.name}")
            
            if successful_retrievals > 0:
                avg_time = total_time / successful_retrievals
                print(f"\n   Average retrieval time: {avg_time:.3f}s")
                print(f"   Total concurrent time: {total_time:.3f}s")
            
            # Selective details retrieval by document type
            print("\n2. Selective details retrieval by type:")
            
            # Get documents by type
            pdf_docs = await client.list_documents(document_type=DocumentType.PDF, page_size=3)
            image_docs = await client.list_documents(document_type=DocumentType.IMAGES, page_size=3)
            
            async def process_documents_by_type(docs, doc_type):
                if not docs.documents:
                    print(f"   No {doc_type} documents found")
                    return
                
                print(f"\n   Processing {doc_type} documents:")
                
                tasks = [get_document_details_with_timing(doc) for doc in docs.documents]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        print(f"     Error: {result}")
                        continue
                    
                    doc, details, elapsed_time = result
                    if details:
                        print(f"     {doc.name}: {elapsed_time:.3f}s")
                        if doc_type == "pdf":
                            metadata = details.base.metadata
                            print(f"       Pages: {metadata.page_count}, Completion: {metadata.completion_rate:.1%}")
                        else:
                            metadata = details.base.metadata
                            print(f"       Images: {metadata.image_count}, Completion: {metadata.completion_rate:.1%}")
            
            # Process different types concurrently
            type_tasks = [
                process_documents_by_type(pdf_docs, "PDF"),
                process_documents_by_type(image_docs, "Images")
            ]
            await asyncio.gather(*type_tasks, return_exceptions=True)
            
    except Exception as e:
        print(f"Error: {e}")

async def example_4_async_document_export():
    """Example 4: Async document export with concurrent operations."""
    print("\n" + "=" * 60)
    print("Async Example 4: Document Export Operations")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating async document export...")
            
            # Get completed documents for export
            documents = await client.list_documents(
                status=ProcessingStatus.COMPLETED,
                page_size=3
            )
            
            if documents.pagination.total_count == 0:
                print("No completed documents found for export examples.")
                return
            
            print(f"Found {len(documents.documents)} completed documents")
            
            # Concurrent export in different formats
            print("\n1. Concurrent export in different formats:")
            
            # Use the first document for export demo
            doc = documents.documents[0]
            print(f"Exporting document: {doc.name} (ID: {doc.id})")
            
            async def export_document_with_timing(format_type):
                start_time = time.time()
                try:
                    export_response = await client.export_document(
                        document_id=doc.id,
                        export_format=format_type
                    )
                    end_time = time.time()
                    return format_type, export_response, end_time - start_time
                except Exception as e:
                    end_time = time.time()
                    return format_type, None, end_time - start_time
            
            # Export in different formats concurrently
            export_formats = [ExportFormat.JSON]  # REST API only supports JSON
            export_tasks = [export_document_with_timing(fmt) for fmt in export_formats]
            export_results = await asyncio.gather(*export_tasks, return_exceptions=True)
            
            for result in export_results:
                if isinstance(result, Exception):
                    print(f"   Export error: {result}")
                    continue
                
                format_type, export_response, elapsed_time = result
                
                if export_response:
                    print(f"\n   {format_type.value.upper()} Export:")
                    print(f"     Time: {elapsed_time:.3f}s")
                    print(f"     Size: {len(export_response.content)} bytes")
                    print(f"     Content type: {export_response.content_type}")
                    print(f"     Filename: {export_response.filename}")
                    
                    # Show preview for text-based formats
                    if format_type == ExportFormat.JSON:
                        try:
                            content_str = export_response.content.decode('utf-8')
                            preview = content_str[:200].replace('\n', ' ')
                            print(f"     Preview: {preview}...")
                        except UnicodeDecodeError:
                            print(f"     Preview: Binary content")
                else:
                    print(f"   {format_type.value} export failed")
            
            # Batch export of multiple documents
            print("\n2. Batch export of multiple documents:")
            
            async def export_single_document(doc, format_type):
                try:
                    export_response = await client.export_document(
                        document_id=doc.id,
                        export_format=format_type
                    )
                    return doc, export_response
                except Exception as e:
                    return doc, None
            
            # Export all documents concurrently
            batch_tasks = [
                export_single_document(doc, ExportFormat.JSON)
                for doc in documents.documents
            ]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            successful_exports = 0
            total_size = 0
            
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"   Batch export error: {result}")
                    continue
                
                doc, export_response = result
                if export_response:
                    successful_exports += 1
                    total_size += len(export_response.content)
                    print(f"   ✓ {doc.name}: {len(export_response.content)} bytes")
                else:
                    print(f"   ✗ {doc.name}: Export failed")
            
            if successful_exports > 0:
                print(f"\n   Batch export summary:")
                print(f"     Successful: {successful_exports}/{len(documents.documents)}")
                print(f"     Total size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
            
            # Export with file saving
            print("\n3. Export with file saving:")
            
            if documents.documents:
                demo_doc = documents.documents[0]
                
                async def save_export_to_file(doc, format_type):
                    try:
                        export_response = await client.export_document(
                            document_id=doc.id,
                            export_format=format_type
                        )
                        
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(
                            mode='wb',
                            suffix=f'.{format_type.value}',
                            delete=False
                        ) as temp_file:
                            temp_file.write(export_response.content)
                            temp_path = temp_file.name
                        
                        return doc, format_type, temp_path, len(export_response.content)
                    except Exception as e:
                        return doc, format_type, None, None
                
                save_tasks = [
                    save_export_to_file(demo_doc, fmt)
                    for fmt in [ExportFormat.JSON]
                ]
                save_results = await asyncio.gather(*save_tasks, return_exceptions=True)
                
                for result in save_results:
                    if isinstance(result, Exception):
                        print(f"   Save error: {result}")
                        continue
                    
                    doc, format_type, temp_path, size = result
                    if temp_path and size:
                        print(f"   Saved {format_type.value} export: {temp_path}")
                        print(f"     Size: {size} bytes")
                        
                        # Clean up
                        try:
                            os.unlink(temp_path)
                            print(f"     Cleaned up temporary file")
                        except OSError:
                            print(f"     Could not clean up temporary file")
                    else:
                        print(f"   Failed to save {format_type.value} export")
            
    except Exception as e:
        print(f"Error: {e}")

async def example_5_async_document_management():
    """Example 5: Async document management with concurrent operations."""
    print("\n" + "=" * 60)
    print("Async Example 5: Document Management Operations")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating async document management...")
            
            # Get document overview
            print("\n1. Document overview analysis:")
            
            # Get all documents concurrently with different filters
            async def get_filtered_documents(filter_name, **kwargs):
                try:
                    docs = await client.list_documents(page_size=20, **kwargs)
                    return filter_name, docs
                except Exception as e:
                    return filter_name, None
            
            overview_tasks = [
                get_filtered_documents("all_documents"),
                get_filtered_documents("completed", status=ProcessingStatus.COMPLETED),
                get_filtered_documents("running", status=ProcessingStatus.RUNNING),
                get_filtered_documents("error", status=ProcessingStatus.ERROR),
                get_filtered_documents("pdfs", document_type=DocumentType.PDF),
                get_filtered_documents("images", document_type=DocumentType.IMAGES)
            ]
            
            overview_results = await asyncio.gather(*overview_tasks, return_exceptions=True)
            
            document_stats = {}
            
            for result in overview_results:
                if isinstance(result, Exception):
                    print(f"   Overview error: {result}")
                    continue
                
                filter_name, docs = result
                if docs:
                    document_stats[filter_name] = {
                        'count': len(docs.documents),
                        'total': docs.pagination.total_count
                    }
                    print(f"   {filter_name}: {len(docs.documents)} (total: {docs.pagination.total_count})")
            
            # Concurrent document analysis
            print("\n2. Concurrent document analysis:")
            
            # Get documents for analysis
            all_docs = await client.list_documents(page_size=10)
            
            if all_docs.documents:
                async def analyze_document(doc):
                    try:
                        # Get details
                        details = await client.get_document_details(doc.id)
                        
                        # Calculate metrics
                        metadata = details.base.metadata
                        analysis = {
                            'name': doc.name,
                            'type': doc.type,
                            'status': doc.status,
                            'completion_rate': metadata.completion_rate,
                            'file_size': getattr(metadata, 'file_size', 0),
                            'has_content': False
                        }
                        
                        # Check if document has content
                        if doc.type == "pdf" and hasattr(details.content, 'pages'):
                            analysis['has_content'] = any(p.has_result for p in details.content.pages)
                        elif doc.type == "images" and hasattr(details.content, 'images'):
                            analysis['has_content'] = any(img.has_result for img in details.content.images)
                        
                        return analysis
                    except Exception as e:
                        return {'name': doc.name, 'error': str(e)}
                
                # Analyze documents concurrently
                analysis_tasks = [analyze_document(doc) for doc in all_docs.documents[:5]]  # Limit for demo
                analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                
                completed_docs = 0
                total_size = 0
                docs_with_content = 0
                
                for result in analysis_results:
                    if isinstance(result, Exception):
                        print(f"   Analysis error: {result}")
                        continue
                    
                    if 'error' in result:
                        print(f"   {result['name']}: Analysis failed - {result['error']}")
                    else:
                        completed_docs += 1
                        total_size += result['file_size']
                        if result['has_content']:
                            docs_with_content += 1
                        
                        print(f"   {result['name']}:")
                        print(f"     Type: {result['type']}, Status: {result['status']}")
                        print(f"     Completion: {result['completion_rate']:.1%}")
                        print(f"     Size: {result['file_size']} bytes")
                        print(f"     Has content: {'Yes' if result['has_content'] else 'No'}")
                
                if completed_docs > 0:
                    print(f"\n   Analysis Summary:")
                    print(f"     Documents analyzed: {completed_docs}")
                    print(f"     Total size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
                    print(f"     Documents with content: {docs_with_content}/{completed_docs}")
            
            # Safe deletion demonstration (with confirmation)
            print("\n3. Document deletion (demonstration only):")
            
            # Find documents that could be deleted (failed or old completed)
            failed_docs = await client.list_documents(
                status=ProcessingStatus.ERROR,
                page_size=3
            )
            
            if failed_docs.documents:
                print(f"   Found {len(failed_docs.documents)} failed documents that could be deleted:")
                for doc in failed_docs.documents:
                    print(f"     - {doc.name} (ID: {doc.id[:8]}...)")
                
                print("   (Actual deletion commented out for safety)")
                print("   To delete, uncomment the deletion code below:")
                
                # Example deletion code (commented out for safety):
                # async def delete_document_safely(doc):
                #     try:
                #         delete_response = await client.delete_document(doc.id)
                #         return doc, delete_response
                #     except Exception as e:
                #         return doc, None
                # 
                # delete_tasks = [delete_document_safely(doc) for doc in failed_docs.documents]
                # delete_results = await asyncio.gather(*delete_tasks, return_exceptions=True)
            else:
                print("   No failed documents found for deletion demonstration")
            
    except Exception as e:
        print(f"Error: {e}")

async def example_6_async_error_handling():
    """Example 6: Comprehensive async error handling."""
    print("\n" + "=" * 60)
    print("Async Example 6: Error Handling and Resilience")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating async error handling...")
            
            # Test 1: Invalid document ID with timeout
            print("\n1. Testing invalid document ID with timeout:")
            
            async def get_details_with_timeout(doc_id, timeout_seconds=2.0):
                try:
                    # Use asyncio.wait_for to add timeout
                    details = await asyncio.wait_for(
                        client.get_document_details(doc_id),
                        timeout=timeout_seconds
                    )
                    return doc_id, details, None
                except asyncio.TimeoutError:
                    return doc_id, None, f"Timeout after {timeout_seconds}s"
                except Exception as e:
                    return doc_id, None, str(e)
            
            invalid_ids = [
                "nonexistent-document-id-12345",
                "invalid-id-format",
                ""
            ]
            
            timeout_tasks = [
                get_details_with_timeout(doc_id, 2.0)
                for doc_id in invalid_ids
            ]
            
            timeout_results = await asyncio.gather(*timeout_tasks, return_exceptions=True)
            
            for result in timeout_results:
                if isinstance(result, Exception):
                    print(f"   Unexpected error: {result}")
                else:
                    doc_id, details, error = result
                    if error:
                        print(f"   {doc_id or 'empty'}: {error}")
                    else:
                        print(f"   {doc_id}: Unexpected success")
            
            # Test 2: Concurrent operations with error handling
            print("\n2. Concurrent operations with error handling:")
            
            async def safe_operation(operation_name, operation_func):
                try:
                    result = await operation_func()
                    return operation_name, result, None
                except Exception as e:
                    return operation_name, None, str(e)
            
            # Mix of valid and potentially problematic operations
            operations = [
                ("list_documents", lambda: client.list_documents(page_size=5)),
                ("search_empty_query", lambda: client.search_documents(query="")),  # Should fail
                ("search_valid_query", lambda: client.search_documents(query="test", page_size=3)),
                ("get_invalid_document", lambda: client.get_document_details("invalid-id")),
                ("export_invalid_document", lambda: client.export_document("invalid-id", ExportFormat.JSON))
            ]
            
            safe_tasks = [
                safe_operation(name, func)
                for name, func in operations
            ]
            
            safe_results = await asyncio.gather(*safe_tasks, return_exceptions=True)
            
            for result in safe_results:
                if isinstance(result, Exception):
                    print(f"   Operation error: {result}")
                else:
                    operation_name, operation_result, error = result
                    if error:
                        print(f"   {operation_name}: {error}")
                    else:
                        print(f"   {operation_name}: Success")
            
            # Test 3: Retry mechanism demonstration
            print("\n3. Retry mechanism demonstration:")
            
            async def retry_operation(operation_func, max_retries=3, delay=0.5):
                """Retry an operation with exponential backoff."""
                for attempt in range(max_retries):
                    try:
                        result = await operation_func()
                        return result, attempt + 1  # Return result and attempt count
                    except Exception as e:
                        if attempt == max_retries - 1:
                            return None, max_retries  # Failed after all retries
                        
                        print(f"     Attempt {attempt + 1} failed: {e}")
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            # Test retry with a potentially failing operation
            async def potentially_failing_operation():
                # This might fail due to network issues or server problems
                return await client.list_documents(page_size=1)
            
            print("   Testing retry mechanism...")
            result, attempts = await retry_operation(potentially_failing_operation, max_retries=3)
            
            if result:
                print(f"   ✓ Operation succeeded after {attempts} attempt(s)")
            else:
                print(f"   ✗ Operation failed after {attempts} attempt(s)")
            
            # Test 4: Circuit breaker pattern simulation
            print("\n4. Circuit breaker pattern:")
            
            class SimpleCircuitBreaker:
                def __init__(self, failure_threshold=3, timeout=5.0):
                    self.failure_threshold = failure_threshold
                    self.timeout = timeout
                    self.failure_count = 0
                    self.last_failure_time = None
                    self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
                
                async def call(self, operation_func):
                    if self.state == "OPEN":
                        if time.time() - self.last_failure_time > self.timeout:
                            self.state = "HALF_OPEN"
                        else:
                            raise Exception("Circuit breaker is OPEN")
                    
                    try:
                        result = await operation_func()
                        if self.state == "HALF_OPEN":
                            self.state = "CLOSED"
                            self.failure_count = 0
                        return result
                    except Exception as e:
                        self.failure_count += 1
                        self.last_failure_time = time.time()
                        
                        if self.failure_count >= self.failure_threshold:
                            self.state = "OPEN"
                        
                        raise e
            
            # Create circuit breaker
            circuit_breaker = SimpleCircuitBreaker(failure_threshold=2, timeout=2.0)
            
            async def protected_operation():
                return await circuit_breaker.call(
                    lambda: client.get_document_details("nonexistent-id")
                )
            
            print("   Testing circuit breaker with failing operations...")
            
            for i in range(4):
                try:
                    result = await protected_operation()
                    print(f"   Attempt {i + 1}: Success (unexpected)")
                except Exception as e:
                    print(f"   Attempt {i + 1}: {e}")
                    print(f"     Circuit breaker state: {circuit_breaker.state}")
                
                if i < 3:  # Don't sleep after last attempt
                    await asyncio.sleep(0.5)
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run all async document API examples."""
    print("DotsOCR Document API - Async Usage Examples")
    print("Make sure DotsOCR server is running and has some documents.")
    print("Set environment variables:")
    print("  export DOTSOCR_SERVER_URL='http://127.0.0.1:8080'")
    print("  export DOTSOCR_AUTH_TOKEN='your-secret-token'")
    print()
    
    # Test server connection first
    server_url, auth_token = get_config()
    print(f"Testing connection to server at {server_url}...")
    
    try:
        async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
            health = await client.health_check()
            print(f"✓ Server is healthy (status: {health.status}, version: {health.version})")
            
            # Check if there are any documents
            docs = await client.list_documents(page_size=1)
            if docs.pagination.total_count == 0:
                print("⚠️  No documents found. Please upload some documents first using basic OCR examples.")
                print("You can run basic_usage.py or async_usage.py examples to create some documents.")
                return
            
    except Exception as e:
        print(f"✗ Failed to connect to server: {e}")
        print("Please make sure:")
        print("1. The DotsOCR server is running")
        print("2. The server URL is correct")
        print("3. The auth token is correct")
        return
    
    print("\nStarting async document API examples...")
    
    # Run examples
    examples = [
        ("Async Document Listing", example_1_async_document_listing),
        ("Async Document Search", example_2_async_document_search),
        ("Async Document Details", example_3_async_document_details),
        ("Async Document Export", example_4_async_document_export),
        ("Async Document Management", example_5_async_document_management),
        ("Async Error Handling", example_6_async_error_handling)
    ]
    
    for example_name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {example_name}")
            print('='*60)
            await example_func()
            print(f"✓ {example_name} completed successfully")
        except KeyboardInterrupt:
            print(f"\n{example_name} interrupted by user.")
            break
        except Exception as e:
            print(f"✗ {example_name} failed with error: {e}")
            print(f"Full error details:\n{traceback.format_exc()}")
        
        print("\n" + "-" * 60)
        await asyncio.sleep(1)  # Brief pause between examples
    
    print("\n" + "="*60)
    print("All async document API examples completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
