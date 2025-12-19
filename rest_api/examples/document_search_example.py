#!/usr/bin/env python3
"""
Document API - Search Documents Example

This example demonstrates:
1. Basic document search functionality
2. Search across different scopes (filenames, content, both)
3. Search with pagination
4. Advanced search techniques
5. Error handling for search operations
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import dotsocr_runner_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    DotsOCRRunnerClient, 
    setup_logging,
    APIError,
    AuthenticationError,
    ConnectionError,
    SearchScope
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

def example_1_basic_document_search():
    """Example 1: Basic document search."""
    print("=" * 60)
    print("Example 1: Basic Document Search")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating basic search functionality...")
            
            # Get all documents first to understand what we can search for
            all_docs = client.list_documents(page_size=10)
            if all_docs.pagination.total_count == 0:
                print("No documents found. Please upload some documents first.")
                return
            
            print(f"Found {all_docs.pagination.total_count} total documents")
            
            # Display some document names for search reference
            print("\nAvailable documents for searching:")
            for doc in all_docs.documents[:5]:
                print(f"  - {doc.name} ({doc.type})")
            
            # Search for common terms
            search_terms = ["test", "document", "pdf", "image", "ocr"]
            
            for term in search_terms:
                print(f"\n--- Searching for: '{term}' ---")
                
                try:
                    # Search in filenames only
                    filename_results = client.search_documents(
                        query=term,
                        scope=SearchScope.FILENAMES,
                        page_size=5
                    )
                    print(f"Filename matches: {len(filename_results.documents)}")
                    for doc in filename_results.documents:
                        print(f"  - {doc.name} ({doc.type})")
                    
                    # Search in content only
                    content_results = client.search_documents(
                        query=term,
                        scope=SearchScope.CONTENT,
                        page_size=5
                    )
                    print(f"Content matches: {len(content_results.documents)}")
                    for doc in content_results.documents:
                        print(f"  - {doc.name} ({doc.type})")
                    
                    # Search in both filenames and content
                    both_results = client.search_documents(
                        query=term,
                        scope=SearchScope.BOTH,
                        page_size=5
                    )
                    print(f"Both matches: {len(both_results.documents)}")
                    for doc in both_results.documents:
                        print(f"  - {doc.name} ({doc.type})")
                        
                except APIError as e:
                    print(f"Search error for '{term}': {e}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_2_search_scopes_comparison():
    """Example 2: Comparing different search scopes."""
    print("\n" + "=" * 60)
    print("Example 2: Search Scopes Comparison")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Comparing search scopes with different queries...")
            
            # Test queries
            test_queries = [
                "test",
                "report",
                "analysis",
                "data"
            ]
            
            for query in test_queries:
                print(f"\n--- Query: '{query}' ---")
                
                # Get results from all scopes
                scope_mapping = {
                    "filenames": SearchScope.FILENAMES,
                    "content": SearchScope.CONTENT,
                    "both": SearchScope.BOTH
                }
                results_by_scope = {}
                
                for scope_name, scope_enum in scope_mapping.items():
                    try:
                        results = client.search_documents(
                            query=query,
                            scope=scope_enum,
                            page_size=10
                        )
                        results_by_scope[scope_name] = results
                        print(f"{scope_name.capitalize()}: {len(results.documents)} matches")
                        
                        # Show document names
                        for doc in results.documents[:3]:  # Show first 3
                            print(f"  - {doc.name}")
                            
                    except APIError as e:
                        print(f"{scope_name.capitalize()}: Error - {e}")
                        results_by_scope[scope_name] = None
                
                # Analyze overlap
                if all(results_by_scope.values()):
                    filename_docs = {doc.id for doc in results_by_scope["filenames"].documents}
                    content_docs = {doc.id for doc in results_by_scope["content"].documents}
                    both_docs = {doc.id for doc in results_by_scope["both"].documents}
                    
                    print(f"Analysis:")
                    print(f"  Filename only: {len(filename_docs - content_docs)}")
                    print(f"  Content only: {len(content_docs - filename_docs)}")
                    print(f"  Both scopes: {len(filename_docs & content_docs)}")
                    print(f"  Total unique: {len(both_docs)}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_3_search_with_pagination():
    """Example 3: Search with pagination."""
    print("\n" + "=" * 60)
    print("Example 3: Search with Pagination")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating search with pagination...")
            
            # Use a broad search term to get more results
            search_query = "document"
            
            print(f"Searching for: '{search_query}'")
            
            # Get first page to see total results
            first_page = client.search_documents(
                query=search_query,
                scope=SearchScope.BOTH,
                page=1,
                page_size=3
            )
            
            total_results = first_page.pagination.total_count
            total_pages = first_page.pagination.total_pages
            
            print(f"Total results: {total_results}")
            print(f"Total pages: {total_pages}")
            print(f"Page size: {first_page.pagination.page_size}")
            
            if total_results == 0:
                print("No results found. Try a different search term.")
                return
            
            # Show pagination
            pages_to_show = min(3, total_pages)
            print(f"\nShowing first {pages_to_show} pages:")
            
            for page in range(1, pages_to_show + 1):
                page_results = client.search_documents(
                    query=search_query,
                    scope=SearchScope.BOTH,
                    page=page,
                    page_size=3
                )
                
                print(f"\nPage {page} ({len(page_results.documents)} results):")
                for doc in page_results.documents:
                    print(f"  - {doc.name} ({doc.type}, {doc.status})")
            
            # Demonstrate different page sizes
            print(f"\n--- Different page sizes ---")
            for page_size in [1, 5, 10]:
                try:
                    results = client.search_documents(
                        query=search_query,
                        scope=SearchScope.BOTH,
                        page=1,
                        page_size=page_size
                    )
                    print(f"Page size {page_size}: {len(results.documents)} results (showing page 1 of {results.pagination.total_pages})")
                except Exception as e:
                    print(f"Page size {page_size}: Error - {e}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_4_advanced_search_techniques():
    """Example 4: Advanced search techniques."""
    print("\n" + "=" * 60)
    print("Example 4: Advanced Search Techniques")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating advanced search techniques...")
            
            # Get document names for intelligent search
            all_docs = client.list_documents(page_size=20)
            document_names = [doc.name for doc in all_docs.documents]
            
            if not document_names:
                print("No documents available for advanced search examples.")
                return
            
            print(f"Available documents: {len(document_names)}")
            
            # Extract common terms from document names
            import re
            all_text = " ".join(document_names).lower()
            words = re.findall(r'\b\w+\b', all_text)
            common_words = [word for word in set(words) if len(word) > 2 and words.count(word) > 1]
            
            print(f"Common terms in filenames: {common_words[:5]}")
            
            # Search for document extensions
            print(f"\n--- Search by file extension ---")
            extensions = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
            for ext in extensions:
                try:
                    results = client.search_documents(
                        query=ext,
                        scope=SearchScope.FILENAMES,
                        page_size=5
                    )
                    if results.documents:
                        print(f"{ext}: {len(results.documents)} documents")
                        for doc in results.documents:
                            print(f"  - {doc.name}")
                except Exception as e:
                    print(f"{ext}: Error - {e}")
            
            # Search for partial matches
            print(f"\n--- Partial word searches ---")
            if common_words:
                base_word = common_words[0]
                partial_terms = [
                    base_word[:3],  # First 3 letters
                    base_word[:-2],  # All but last 2 letters
                    base_word[1:-1]  # Middle letters
                ]
                
                for term in partial_terms:
                    try:
                        results = client.search_documents(
                            query=term,
                            scope=SearchScope.BOTH,
                            page_size=3
                        )
                        print(f"'{term}': {len(results.documents)} matches")
                        for doc in results.documents:
                            print(f"  - {doc.name}")
                    except Exception as e:
                        print(f"'{term}': Error - {e}")
            
            # Case sensitivity test
            print(f"\n--- Case sensitivity tests ---")
            if common_words:
                test_word = common_words[0]
                case_variations = [
                    test_word.lower(),
                    test_word.upper(),
                    test_word.capitalize()
                ]
                
                for variation in case_variations:
                    try:
                        results = client.search_documents(
                            query=variation,
                            scope=SearchScope.BOTH,
                            page_size=3
                        )
                        print(f"'{variation}': {len(results.documents)} matches")
                    except Exception as e:
                        print(f"'{variation}': Error - {e}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_5_search_error_handling():
    """Example 5: Search error handling."""
    print("\n" + "=" * 60)
    print("Example 5: Search Error Handling")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Demonstrating search error handling...")
            
            # Test empty search query
            print("\n1. Testing empty search query:")
            try:
                empty_results = client.search_documents(query="")
                print("   ✗ Should have failed with empty query")
            except APIError as e:
                print(f"   ✓ Correctly caught error: {e}")
            
            # Test single character query
            print("\n2. Testing single character query:")
            try:
                single_char_results = client.search_documents(query="a")
                print("   ✗ Should have failed with single character")
            except APIError as e:
                print(f"   ✓ Correctly caught error: {e}")
            
            # Test invalid search scope
            print("\n3. Testing invalid search scope:")
            try:
                invalid_scope_results = client.search_documents(
                    query="test",
                    scope="invalid_scope"
                )
                print("   ✗ Should have failed with invalid scope")
            except APIError as e:
                print(f"   ✓ Correctly caught error: {e}")
            
            # Test very long search query
            print("\n4. Testing very long search query:")
            long_query = "a" * 1000  # 1000 character query
            try:
                long_results = client.search_documents(query=long_query)
                print(f"   ✓ Handled long query gracefully: {len(long_results.documents)} results")
            except Exception as e:
                print(f"   ✓ Caught error for long query: {e}")
            
            # Test special characters
            print("\n5. Testing special characters in search:")
            special_queries = [
                "test@document.com",
                "file#name",
                "search&query",
                "document/name",
                "test\\document"
            ]
            
            for query in special_queries:
                try:
                    results = client.search_documents(query=query)
                    print(f"   '{query}': {len(results.documents)} results")
                except Exception as e:
                    print(f"   '{query}': Error - {e}")
            
            # Test Unicode characters
            print("\n6. Testing Unicode characters:")
            unicode_queries = [
                "测试",  # Chinese
                "документ",  # Russian
                "documento",  # Spanish/Italian
                "ドキュメント"  # Japanese
            ]
            
            for query in unicode_queries:
                try:
                    results = client.search_documents(query=query)
                    print(f"   '{query}': {len(results.documents)} results")
                except Exception as e:
                    print(f"   '{query}': Error - {e}")
            
    except Exception as e:
        print(f"Error: {e}")

def example_6_search_performance_tips():
    """Example 6: Search performance tips and best practices."""
    print("\n" + "=" * 60)
    print("Example 6: Search Performance Tips")
    print("=" * 60)
    
    server_url, auth_token = get_config()
    
    try:
        with DotsOCRRunnerClient(server_url, auth_token) as client:
            print("Search performance tips and best practices...")
            
            import time
            
            # Tip 1: Use specific scopes when possible
            print("\n1. Scope-specific search performance:")
            test_query = "test"
            
            scope_mapping = {
                "filenames": SearchScope.FILENAMES,
                "content": SearchScope.CONTENT,
                "both": SearchScope.BOTH
            }
            
            for scope_name, scope_enum in scope_mapping.items():
                start_time = time.time()
                try:
                    results = client.search_documents(
                        query=test_query,
                        scope=scope_enum,
                        page_size=10
                    )
                    end_time = time.time()
                    print(f"   {scope_name.capitalize()}: {len(results.documents)} results in {end_time - start_time:.3f}s")
                except Exception as e:
                    print(f"   {scope_name.capitalize()}: Error - {e}")
            
            # Tip 2: Use appropriate page sizes
            print("\n2. Page size performance impact:")
            page_sizes = [1, 5, 10, 20, 50]
            
            for page_size in page_sizes:
                start_time = time.time()
                try:
                    results = client.search_documents(
                        query=test_query,
                        scope=SearchScope.BOTH,
                        page=1,
                        page_size=page_size
                    )
                    end_time = time.time()
                    print(f"   Page size {page_size}: {end_time - start_time:.3f}s")
                except Exception as e:
                    print(f"   Page size {page_size}: Error - {e}")
            
            # Tip 3: Query length impact
            print("\n3. Query length performance impact:")
            query_lengths = [3, 5, 10, 20, 50]
            
            for length in query_lengths:
                query = "a" * length
                start_time = time.time()
                try:
                    results = client.search_documents(
                        query=query,
                        scope=SearchScope.BOTH,
                        page_size=10
                    )
                    end_time = time.time()
                    print(f"   Length {length}: {end_time - start_time:.3f}s")
                except Exception as e:
                    print(f"   Length {length}: Error - {e}")
            
            print("\n--- Best Practices Summary ---")
            print("1. Use 'filenames' scope when searching for specific documents")
            print("2. Use 'content' scope when searching for specific information")
            print("3. Use 'both' scope for comprehensive searches (slower)")
            print("4. Use smaller page sizes for faster initial results")
            print("5. Use specific, meaningful search terms")
            print("6. Avoid very short queries (minimum 2 characters)")
            print("7. Consider pagination for large result sets")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all document search examples."""
    print("DotsOCR Document API - Search Documents Examples")
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
    
    print("\nStarting document search examples...")
    
    # Run examples
    examples = [
        ("Basic Document Search", example_1_basic_document_search),
        ("Search Scopes Comparison", example_2_search_scopes_comparison),
        ("Search with Pagination", example_3_search_with_pagination),
        ("Advanced Search Techniques", example_4_advanced_search_techniques),
        ("Search Error Handling", example_5_search_error_handling),
        ("Search Performance Tips", example_6_search_performance_tips)
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
    print("All document search examples completed!")
    print("="*60)

if __name__ == "__main__":
    main()
