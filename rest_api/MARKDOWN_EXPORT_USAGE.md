# DotsOCR Enhanced Markdown Export Usage Guide

This guide explains how to use the enhanced markdown export functionality added to the DotsOCR Python client API. The new implementation supports both embedded and separated image modes, as well as page/image range filtering.

## Overview

The enhanced markdown export feature provides flexible options for retrieving OCR results as markdown content. You can choose between embedding images directly in the markdown text or separating them into individual files for better readability and management.

## Key Features

### 1. Two Export Modes

**Embedded Mode (Default):**
- Images are embedded as base64 data URLs directly in the markdown text
- Compatible with the original format
- Self-contained markdown files

**Separated Mode:**
- Images are extracted and referenced by filename (e.g., `img1.png`, `img2.png`)
- Images are returned as separate base64 data in the response
- Cleaner, more readable markdown text
- Allows users to save images separately or ignore them

### 2. Range Filtering

**Page Range (PDF documents):**
- Export specific pages using range syntax like "1-5,7,9-10"
- Useful for large documents when you only need certain sections

**Image Range (Image batches):**
- Export specific images using range syntax like "1-5,7,9-10"
- Filter out unwanted images from batch processing

### 3. JSON Response Format

The API now returns structured JSON responses instead of plain text:

```json
{
  "success": true,
  "mode": "embedded|separated",
  "text": "markdown content here",
  "clips": ["base64_image_data_1", "base64_image_data_2"],  // Only in separated mode
  "image_names": ["img1.png", "img2.png"],  // Only in separated mode
  "content_type": "text/markdown|application/json",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

## API Methods

### 1. Enhanced get_document_markdown()

New enhanced method with support for modes and ranges:

```python
# Synchronous client
response = client.get_document_markdown(
    content_hash="abc123",
    document_type="pdf",
    file_name="document.pdf",
    mode=MarkdownExportMode.EMBEDDED,  # or SEPARATED
    page_range="1-5,7,9-10"  // Optional: for PDF only
)

# Asynchronous client
response = await client.get_document_markdown(
    content_hash="abc123",
    document_type="images",
    mode=MarkdownExportMode.SEPARATED,
    image_range="1-5,7"  // Optional: for images only
)
```

### 2. export_document_markdown()

Alternative method using a request object:

```python
# Create request object
request = MarkdownExportRequest(
    content_hash="abc123",
    document_type="pdf",
    file_name="document.pdf",
    mode=MarkdownExportMode.SEPARATED,
    page_range="1-3,5"
)

# Execute request
response = client.export_document_markdown(request)
```

### 3. Backward Compatibility

The existing `export_document()` method remains available for other formats:

```python
# Still works for other formats (json, csv, txt)
export_response = client.export_document(document_id, "json")
print(export_response.content)  # Binary content
```

## API Endpoint

The backend implements the enhanced export endpoint:

```
POST /api/v1/documents/export
```

**Request Body:**
```json
{
  "content_hash": "abc123",
  "type": "pdf|images",
  "file_name": "document.pdf",  // Required for PDF documents only
  "mode": "embedded|separated",  // Optional, default: "embedded"
  "page_range": "1-5,7,9-10",  // Optional, for PDF only
  "image_range": "1-5,7,9-10"   // Optional, for images only
}
```

**Response (Embedded Mode):**
```json
{
  "success": true,
  "mode": "embedded",
  "text": "# Document Title\n\nContent with ![image](data:image/png;base64,iVBORw0KGgo...)",
  "clips": null,
  "image_names": null,
  "content_type": "text/markdown",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

**Response (Separated Mode):**
```json
{
  "success": true,
  "mode": "separated",
  "text": "# Document Title\n\nContent with ![img1.png](img1.png) and ![img2.png](img2.png)",
  "clips": ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "another_base64_string"],
  "image_names": ["img1.png", "img2.png"],
  "content_type": "application/json",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

## Usage Examples

### Basic Usage - Embedded Mode

```python
from dotsocr_runner_client import DotsOCRRunnerClient, MarkdownExportMode

# Initialize client
with DotsOCRRunnerClient(server_url, auth_token) as client:
    # Upload and process document
    upload_response = client.upload_pdf("document.pdf", dpi=150)
    result = client.wait_for_completion(upload_response.task_id)
    
    # Get document details to extract content hash
    documents = client.list_documents()
    document_info = None
    for doc in documents.documents:
        if doc.status == 'completed' and upload_response.filename in doc.name:
            document_info = doc
            break
    
    if document_info:
        # Retrieve markdown content in embedded mode (default)
        response = client.get_document_markdown(
            content_hash=document_info.id,
            document_type='pdf',
            file_name=upload_response.filename,
            mode=MarkdownExportMode.EMBEDDED
        )
        print(f"Mode: {response.mode}")
        print(f"Content: {response.text}")
        print(f"Images embedded: {response.clips is None}")
```

### Separated Mode Example

```python
from dotsocr_runner_client import DotsOCRRunnerClient, MarkdownExportMode

with DotsOCRRunnerClient(server_url, auth_token) as client:
    # Export in separated mode
    response = client.get_document_markdown(
        content_hash="abc123",
        document_type="pdf",
        file_name="document.pdf",
        mode=MarkdownExportMode.SEPARATED
    )
    
    print("Markdown text (clean, with image references):")
    print(response.text)
    print("\nExtracted images:")
    for i, (clip, name) in enumerate(zip(response.clips, response.image_names)):
        print(f"  {i+1}. {name} ({len(clip)} characters of base64 data)")
        
        # Optionally save images to files
        import base64
        with open(name, 'wb') as img_file:
            img_file.write(base64.b64decode(clip))
        print(f"     Saved to {name}")
```

### Page Range Filtering (PDF)

```python
from dotsocr_runner_client import DotsOCRRunnerClient, MarkdownExportMode

with DotsOCRRunnerClient(server_url, auth_token) as client:
    # Export specific pages only
    response = client.get_document_markdown(
        content_hash="abc123",
        document_type="pdf",
        file_name="large_document.pdf",
        mode=MarkdownExportMode.SEPARATED,
        page_range="1-5,7,9-10"  # Pages 1-5, 7, and 9-10
    )
    
    print(f"Exported pages 1-5,7,9-10 from large document")
    print(f"Content length: {len(response.text)} characters")
    print(f"Images found: {len(response.clips) if response.clips else 0}")
```

### Image Range Filtering (Image Batches)

```python
from dotsocr_runner_client import DotsOCRRunnerClient, MarkdownExportMode

with DotsOCRRunnerClient(server_url, auth_token) as client:
    # Export specific images from batch
    response = client.get_document_markdown(
        content_hash="def456",
        document_type="images",
        mode=MarkdownExportMode.SEPARATED,
        image_range="1-5,7"  # Images 1-5 and 7
    )
    
    print(f"Exported images 1-5,7 from batch")
    print(f"Content: {response.text}")
    if response.clips:
        print(f"Extracted {len(response.clips)} images")
```

### Using Request Object

```python
from dotsocr_runner_client import (
    DotsOCRRunnerClient, 
    MarkdownExportRequest, 
    MarkdownExportMode
)

with DotsOCRRunnerClient(server_url, auth_token) as client:
    # Create detailed request
    request = MarkdownExportRequest(
        content_hash="abc123",
        document_type="pdf",
        file_name="document.pdf",
        mode=MarkdownExportMode.SEPARATED,
        page_range="1-3,5"
    )
    
    # Execute request
    response = client.export_document_markdown(request)
    
    print(f"Export successful: {response.success}")
    print(f"Mode: {response.mode}")
    print(f"Generated at: {response.generated_at}")
```

### Asynchronous Usage

```python
import asyncio
from dotsocr_runner_client import AsyncDotsOCRRunnerClient, MarkdownExportMode

async def export_markdown_async():
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        # Upload and process
        upload_response = await client.upload_pdf("document.pdf", dpi=150)
        result = await client.wait_for_completion(upload_response.task_id)
        
        # Get document details
        documents = await client.list_documents()
        document_info = None
        for doc in documents.documents:
            if doc.status == 'completed' and upload_response.filename in doc.name:
                document_info = doc
                break
        
        if document_info:
            # Get markdown content in separated mode
            response = await client.get_document_markdown(
                content_hash=document_info.id,
                document_type='pdf',
                file_name=upload_response.filename,
                mode=MarkdownExportMode.SEPARATED
            )
            
            print(f"Async export completed: {response.success}")
            return response

# Run async function
response = asyncio.run(export_markdown_async())
```

### Batch Processing with Different Modes

```python
import asyncio
from dotsocr_runner_client import AsyncDotsOCRRunnerClient, MarkdownExportMode

async def batch_export_mixed():
    async with AsyncDotsOCRRunnerClient(server_url, auth_token) as client:
        # Get completed documents
        documents = await client.list_documents(status="completed")
        
        # Export with different modes based on document type
        export_tasks = []
        for doc in documents.documents:
            if doc.type == 'pdf':
                # PDFs in separated mode with page range
                task = client.get_document_markdown(
                    content_hash=doc.id,
                    document_type='pdf',
                    file_name=doc.name,
                    mode=MarkdownExportMode.SEPARATED,
                    page_range="1-3"  # First 3 pages only
                )
            else:  # images
                # Images in embedded mode
                task = client.get_document_markdown(
                    content_hash=doc.id,
                    document_type='images',
                    mode=MarkdownExportMode.EMBEDDED
                )
            export_tasks.append(task)
        
        responses = await asyncio.gather(*export_tasks)
        
        # Process results
        for i, response in enumerate(responses):
            print(f"Document {i+1}: {response.mode} mode, {len(response.text)} chars")
            if response.clips:
                print(f"  Images: {len(response.clips)}")
        
        return responses

# Run batch export
responses = asyncio.run(batch_export_mixed())
```

### Save to File with Image Handling

```python
import base64
import os
from dotsocr_runner_client import DotsOCRRunnerClient, MarkdownExportMode

def save_markdown_with_images(response, output_dir="export"):
    """Save markdown content and extract images to separate files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save markdown file
    md_path = os.path.join(output_dir, "content.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"Saved markdown to {md_path}")
    
    # Save images if in separated mode
    if response.clips and response.image_names:
        for clip, name in zip(response.clips, response.image_names):
            img_path = os.path.join(output_dir, name)
            with open(img_path, 'wb') as img_file:
                img_file.write(base64.b64decode(clip))
            print(f"Saved image to {img_path}")

# Usage
with DotsOCRRunnerClient(server_url, auth_token) as client:
    response = client.get_document_markdown(
        content_hash="abc123",
        document_type="pdf",
        file_name="document.pdf",
        mode=MarkdownExportMode.SEPARATED
    )
    
    save_markdown_with_images(response, "my_export")
```

### Error Handling and Validation

```python
from dotsocr_runner_client import (
    DotsOCRRunnerClient, 
    MarkdownExportMode,
    APIError,
    ValueError
)

def safe_export_markdown(client, content_hash, document_type, file_name=None):
    """Safely export markdown with comprehensive error handling."""
    try:
        # Validate parameters
        if document_type not in ['pdf', 'images']:
            raise ValueError("document_type must be 'pdf' or 'images'")
        
        if document_type == 'pdf' and not file_name:
            raise ValueError("file_name is required for PDF documents")
        
        # Attempt export
        response = client.get_document_markdown(
            content_hash=content_hash,
            document_type=document_type,
            file_name=file_name,
            mode=MarkdownExportMode.SEPARATED
        )
        
        if response.success:
            print(f"Export successful: {response.mode} mode")
            return response
        else:
            print(f"Export failed: {response}")
            return None
            
    except ValueError as e:
        print(f"Validation error: {e}")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None

# Usage
with DotsOCRRunnerClient(server_url, auth_token) as client:
    response = safe_export_markdown(
        client=client,
        content_hash="abc123",
        document_type="pdf",
        file_name="document.pdf"
    )
```

## Configuration

### Environment Variables

Set these environment variables for easy configuration:

```bash
export DOTSOCR_SERVER_URL='http://127.0.0.1:8080'
export DOTSOCR_AUTH_TOKEN='your-actual-auth-token'
```

### Server Requirements

Ensure your DotsOCR server:
1. Is running and accessible
2. Has HTTP server enabled
3. Has proper authentication configured
4. Supports the new POST export endpoint

## Error Handling

The new methods include comprehensive error handling:

```python
try:
    markdown_content = client.get_document_markdown(
        content_hash="abc123",
        document_type="pdf",
        file_name="document.pdf"
    )
except APIError as e:
    if "DOCUMENT_NOT_FOUND" in str(e):
        print("Document does not exist")
    else:
        print(f"API error: {e}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except ConnectionError:
    print("Cannot connect to server")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Methods

### `get_document_markdown(content_hash: str, document_type: str, file_name: Optional[str] = None) -> str`

Get document content as markdown string directly.

**Parameters:**
- `content_hash`: Document content hash (from document list)
- `document_type`: Document type ('pdf' or 'images')
- `file_name`: File name (required for PDF documents only)

**Returns:**
- `str`: Markdown content

**Validation:**
- `document_type` must be 'pdf' or 'images'
- `file_name` is required when `document_type` is 'pdf'

**Example:**
```python
# PDF document
markdown_content = client.get_document_markdown(
    content_hash="abc123",
    document_type='pdf',
    file_name='document.pdf'
)

# Image batch
markdown_content = client.get_document_markdown(
    content_hash="def456",
    document_type='images'
)
```

## Performance Benefits

### Compared to File-Based Export

1. **No File I/O**: Eliminates intermediate file operations
2. **Faster Access**: Direct string retrieval
3. **Memory Efficient**: No temporary file storage
4. **Better for APIs**: Ideal for web service responses

### Use Cases

- **Web Applications**: Return markdown content directly to users
- **API Services**: Provide markdown content via REST APIs
- **Data Processing**: Process markdown content in memory
- **Integration**: Feed markdown content to other systems

## Examples Directory

The `examples/` directory includes comprehensive examples:

- `markdown_export_example.py`: Synchronous usage examples
- `async_markdown_export_example.py`: Asynchronous usage examples
- `README_DOCUMENT_API.md`: Complete documentation

## Testing

Run simple test to verify implementation:

```bash
cd rest_api
python simple_test.py
```

This verifies that:
- Methods exist and have correct signatures
- Imports work correctly
- Basic functionality is available

## Migration from File Export

If you were previously using file-based export:

### Old Way
```python
export_response = client.export_document(document_id, "markdown")
# export_response.file_path contains path to saved file
with open(export_response.file_path, 'r') as f:
    content = f.read()
```

### New Way
```python
# Method 1: Direct retrieval
markdown_content = client.get_document_markdown(
    content_hash="abc123",
    document_type="pdf",
    file_name="document.pdf"
)

# Method 2: Enhanced export method
export_response = client.export_document(document_id, "markdown")
# export_response.content contains markdown string directly
```

## Backward Compatibility

The existing `export_document()` method remains fully backward compatible:
- File-based export still works for other formats (JSON, CSV, TXT)
- Markdown format now returns content directly as string
- No breaking changes to existing code

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your auth token
   - Ensure server is running
   - Verify token is passed correctly

2. **Document Not Found**
   - Verify content hash is correct
   - Check if document processing is completed
   - Use `list_documents()` to find valid document IDs

3. **Invalid Parameters**
   - Ensure `document_type` is 'pdf' or 'images'
   - Provide `file_name` for PDF documents
   - Check parameter types are strings

4. **Server Not Accessible**
   - Check server URL
   - Verify network connectivity
   - Ensure HTTP server is enabled

### Debug Mode

Enable debug logging:

```python
from dotsocr_runner_client import setup_logging
setup_logging("DEBUG")
```

## API Reference

### Synchronous Client

#### `get_document_markdown(content_hash: str, document_type: str, file_name: Optional[str] = None) -> str`

Retrieves markdown content for a document.

**Parameters:**
- `content_hash`: The content hash of the document to export
- `document_type`: Document type ('pdf' or 'images')
- `file_name`: File name (required for PDF documents only)

**Returns:**
- `str`: Markdown content as string

**Raises:**
- `APIError`: For API-related errors
- `ConnectionError`: For network issues
- `AuthenticationError`: For auth failures
- `ValueError`: For invalid parameters

### Asynchronous Client

#### `get_document_markdown(content_hash: str, document_type: str, file_name: Optional[str] = None) -> str`

Async version of the markdown export method.

**Parameters and Returns:** Same as synchronous version

**Usage:**
```python
markdown_content = await client.get_document_markdown(
    content_hash="abc123",
    document_type="pdf",
    file_name="document.pdf"
)
```

## Support

For issues or questions:

1. Check examples directory for usage patterns
2. Review the test files for implementation details
3. Enable debug logging for troubleshooting
4. Verify server configuration and connectivity

## Future Enhancements

Planned improvements include:

- **Streaming Support**: For large documents
- **Partial Export**: Export specific sections
- **Template Support**: Custom markdown templates
- **Metadata Inclusion**: Include document metadata in markdown
- **Batch Operations**: Optimized batch export endpoints
