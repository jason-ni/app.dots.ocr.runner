#!/usr/bin/env python3
"""
Comprehensive examples demonstrating the enhanced markdown export functionality.

This example shows how to use both embedded and separated export modes
for exporting OCR results as markdown.
"""

import sys
import os
import asyncio
import traceback
from pathlib import Path

# Add parent directory to the path so we can import client
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotsocr_runner_client import (
    DotsOCRRunnerClient, AsyncDotsOCRRunnerClient,
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


def example_embedded_export():
    """Example: Export markdown with embedded base64 images (original behavior)."""
    print("=== Embedded Export Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize client
    with DotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # First, list available documents
            print("Fetching available documents...")
            documents_response = client.list_documents(page_size=10)
            
            if not documents_response.documents:
                print("ℹ No documents found on the server. Please upload some documents first.")
                return
            
            # Use the first available document for this example
            document = documents_response.documents[0]
            print(f"✓ Found document: {document.name} (ID: {document.id}, Type: {document.type})")
            
            # Export with embedded images (default mode)
            response = client.get_document_markdown(
                content_hash=document.id,
                document_type=document.type,
                file_name=document.name if document.type == "pdf" else None,
                mode=MarkdownExportMode.EMBEDDED  # or omit for default
            )
            
            print(f"✓ Export successful!")
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
            print(f"✗ Error: {e}")


def example_separated_export():
    """Example: Export markdown with separated images (new feature)."""
    print("\n=== Separated Export Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize client
    with DotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # First, list available documents
            print("Fetching available documents...")
            documents_response = client.list_documents(page_size=10)
            
            if not documents_response.documents:
                print("ℹ No documents found on the server. Please upload some documents first.")
                return
            
            # Use the first available document for this example
            document = documents_response.documents[0]
            print(f"✓ Found document: {document.name} (ID: {document.id}, Type: {document.type})")
            
            # Export with separated images
            response = client.get_document_markdown(
                content_hash=document.id,
                document_type=document.type,
                file_name=document.name if document.type == "pdf" else None,
                mode=MarkdownExportMode.SEPARATED
            )
            
            print(f"✓ Export successful!")
            print(f"Mode: {response.mode.value}")
            print(f"Content type: {response.content_type}")
            print(f"Generated at: {response.generated_at}")
            print(f"Text length: {len(response.text)} characters")
            
            # Show a preview of the markdown
            preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
            print(f"Preview: {preview}")
            
            # In separated mode, images are provided separately
            if response.clips and response.image_names:
                print(f"✓ Found {len(response.clips)} separated images:")
                for i, (clip, name) in enumerate(zip(response.clips, response.image_names)):
                    print(f"  Image {i+1}: {name} ({len(clip)} characters of base64 data)")
                
                # Show how to save images separately
                print("\n--- Saving Images Separately ---")
                for i, (clip, name) in enumerate(zip(response.clips, response.image_names)):
                    # Decode base64 and save as file
                    import base64
                    try:
                        # Extract base64 data (remove data URL prefix if present)
                        if clip.startswith('data:image'):
                            base64_data = clip.split(',')[1]
                        else:
                            base64_data = clip
                        
                        image_data = base64.b64decode(base64_data)
                        with open(f"exported_{name}", 'wb') as f:
                            f.write(image_data)
                        print(f"✓ Saved {name}")
                    except Exception as e:
                        print(f"✗ Failed to save {name}: {e}")
            else:
                print("ℹ No images found in the document")
                
        except Exception as e:
            print(f"✗ Error: {e}")


def example_request_object():
    """Example: Export using MarkdownExportRequest object."""
    print("\n=== Request Object Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize client
    with DotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # First, list available documents
            print("Fetching available documents...")
            documents_response = client.list_documents(page_size=10)
            
            if not documents_response.documents:
                print("ℹ No documents found on the server. Please upload some documents first.")
                return
            
            # Use the first available document for this example
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
            
            # Export using the request object
            response = client.export_document_markdown(request)
            
            print(f"✓ Export with request object successful!")
            print(f"Mode: {response.mode.value}")
            if request.page_range:
                print(f"Page range: {request.page_range}")
            print(f"Text length: {len(response.text)} characters")
            
            if response.clips:
                print(f"✓ Exported {len(response.clips)} images from specified pages")
                
        except Exception as e:
            print(f"✗ Error: {e}")


def example_image_batch_export():
    """Example: Export markdown from image batch."""
    print("\n=== Image Batch Export Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize client
    with DotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # Export from image batch with specific image range
            response = client.get_document_markdown(
                content_hash="image_batch_hash",
                document_type="images",  # Note: 'images' for batch
                mode=MarkdownExportMode.SEPARATED,
                image_range="1-5,7"  # Export specific images
            )
            
            print(f"✓ Image batch export successful!")
            print(f"Mode: {response.mode.value}")
            print(f"Image range: {response.clips if response.clips else 'None'}")
            
            if response.clips:
                print(f"✓ Exported {len(response.clips)} images from batch")
                for i, name in enumerate(response.image_names or []):
                    print(f"  Image {i+1}: {name}")
                    
        except Exception as e:
            print(f"✗ Error: {e}")


async def example_async_export():
    """Example: Async markdown export."""
    print("\n=== Async Export Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize async client
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # Export with separated mode asynchronously
            response = await client.get_document_markdown(
                content_hash="abc123def456",
                document_type="pdf",
                file_name="document.pdf",
                mode=MarkdownExportMode.SEPARATED
            )
            
            print(f"✓ Async export successful!")
            print(f"Mode: {response.mode.value}")
            print(f"Text length: {len(response.text)} characters")
            
            if response.clips:
                print(f"✓ Exported {len(response.clips)} images asynchronously")
                
        except Exception as e:
            print(f"✗ Async error: {e}")


def example_comparison():
    """Example: Compare embedded vs separated export modes."""
    print("\n=== Mode Comparison Example ===")
    
    # Get configuration from environment
    server_url, auth_token = get_config()
    
    # Initialize client
    with DotsOCRRunnerClient(server_url, auth_token) as client:
        try:
            # Export same document in both modes
            print("Exporting in embedded mode...")
            embedded_response = client.get_document_markdown(
                content_hash="abc123def456",
                document_type="pdf",
                file_name="document.pdf",
                mode=MarkdownExportMode.EMBEDDED
            )
            
            print("Exporting in separated mode...")
            separated_response = client.get_document_markdown(
                content_hash="abc123def456",
                document_type="pdf", 
                file_name="document.pdf",
                mode=MarkdownExportMode.SEPARATED
            )
            
            # Compare results
            print("\n--- Comparison Results ---")
            print(f"Embedded mode:")
            print(f"  Text length: {len(embedded_response.text)} chars")
            print(f"  Has images: {'Yes' if 'data:image' in embedded_response.text else 'No'}")
            print(f"  Clips: {len(embedded_response.clips or [])}")
            
            print(f"Separated mode:")
            print(f"  Text length: {len(separated_response.text)} chars")
            print(f"  Has images: {'Yes' if separated_response.clips else 'No'}")
            print(f"  Clips: {len(separated_response.clips or [])}")
            
            # Show size difference
            embedded_size = len(embedded_response.text)
            separated_size = len(separated_response.text) + sum(len(clip) for clip in separated_response.clips or [])
            
            print(f"\nSize comparison:")
            print(f"  Embedded total: {embedded_size} chars")
            print(f"  Separated total: {separated_size} chars")
            print(f"  Difference: {abs(embedded_size - separated_size)} chars")
            
        except Exception as e:
            print(f"✗ Comparison error: {e}")


def main():
    """Run all examples."""
    print("DotsOCR Enhanced Markdown Export Examples")
    print("=" * 50)
    
    # Run examples
    try:
        example_embedded_export()
        example_separated_export()
    except KeyboardInterrupt:
        print("\n✗ Examples interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error running examples: {e}")
    

if __name__ == "__main__":
    main()
