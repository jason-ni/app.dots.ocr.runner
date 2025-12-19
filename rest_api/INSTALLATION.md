# DotsOCRRunner Python Client - Installation and Usage Guide

## Overview

The DotsOCR Python client provides both synchronous and asynchronous interfaces to interact with the DotsOCR REST API for OCR processing of PDF files and image batches.

## Installation

### Prerequisites

- Python 3.8 or higher
- `requests` library (for synchronous client)
- `aiohttp` library (for asynchronous client)
- DotsOCR server running and accessible

### Install Dependencies

```bash
# Install required dependencies
pip install requests aiohttp

# Or install from requirements.txt
pip install -r requirements.txt
```

### Install the Client

```bash
# Option 1: Install from setup.py
python setup.py install

# Option 2: Install in development mode
pip install -e .

# Option 3: Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/rest_api"
```

## Configuration

### Environment Variables

The client can be configured using environment variables:

```bash
# Server URL (optional, defaults to http://127.0.0.1:8080)
export DOTSOCR_SERVER_URL="http://127.0.0.1:8080"

# Authentication token (required)
export DOTSOCR_AUTH_TOKEN="your-secret-token"
```

### Server Setup

1. Start the DotsOCR server
2. Ensure the HTTP server is enabled in the settings
3. Note the authentication token from the server settings

## Quick Start

### Synchronous Usage

```python
from dotsocr_runner_client import DotsOCRRunnerClient

# Basic usage
with DotsOCRRunnerClient("http://127.0.0.1:8080", "your-token") as client:
    # Upload PDF with default DPI (150)
    upload_response = client.upload_pdf("document.pdf")
    print(f"Task ID: {upload_response.task_id}")
    
    # Upload PDF with custom DPI (300 for high quality)
    upload_response = client.upload_pdf("document.pdf", dpi=300)
    print(f"Task ID: {upload_response.task_id}")
    
    # Upload images with custom DPI (150 for better quality)
    upload_response = client.upload_images(["img1.jpg", "img2.png"], dpi=150)
    print(f"Task ID: {upload_response.task_id}")
    
    # Wait for completion
    result = client.wait_for_completion(upload_response.task_id)
    print(f"OCR Result: {result.result['content']}")
```

### Asynchronous Usage

```python
import asyncio
from dotsocr_runner_client import AsyncDotsOCRRunnerClient

async def main():
    # Advanced usage
    async with AsyncDotsOCRRunnerClient("http://127.0.0.1:8080", "your-token") as client:
        # Upload PDF
        upload_response = await client.upload_pdf("document.pdf")
        print(f"Task ID: {upload_response.task_id}")
        
        # Wait for completion with progress
        def progress_callback(progress, message):
            print(f"Progress: {progress:.1f}% - {message}")
        
        result = await client.wait_for_completion(
            upload_response.task_id,
            progress_callback=progress_callback
        )
        print(f"OCR Result: {result.result['content']}")

asyncio.run(main())
```

## Examples

### Running Examples

The client includes comprehensive examples:

```bash
# Run synchronous examples
cd rest_api
python examples/basic_usage.py

# Run asynchronous examples
python examples/async_usage.py
```

### Example Features

1. **Basic PDF OCR**: Simple file processing
2. **Image Batch OCR**: Process multiple images
3. **Concurrent Processing**: Handle multiple files simultaneously
4. **Progress Tracking**: Monitor processing progress
5. **Task Management**: List, monitor, and clean up tasks

## API Reference

### Synchronous Client

#### Core Methods

- `upload_pdf(file_path, dpi=None)`: Upload a PDF file for OCR with optional DPI setting
- `upload_images(file_paths, dpi=None)`: Upload multiple images for OCR with optional DPI setting
- `get_task_status(task_id)`: Check task status
- `get_task_result(task_id)`: Get OCR results
- `wait_for_completion(task_id, progress_callback=None)`: Wait for task completion
- `delete_task(task_id)`: Delete a task and clean up files
- `list_tasks()`: List all tasks
- `health_check()`: Check server health

### Asynchronous Client

Same methods as synchronous client but with `async`/`await` support:

- `await upload_pdf(file_path, dpi=None)`
- `await upload_images(file_paths, dpi=None)`
- `await get_task_status(task_id)`
- `await get_task_result(task_id)`
- `await wait_for_completion(task_id, progress_callback=None)`
- `await delete_task(task_id)`
- `await list_tasks()`
- `await health_check()`


## Error Handling

The client provides specific exception types:

```python
from dotsocr_runner_client import (
    DotsOCRRunnerClient,
    APIError,
    AuthenticationError,
    ConnectionError,
    FileNotFoundError,
    ValidationError
)

try:
    with DotsOCRRunnerClient(server_url, token) as client:
        upload_response = client.upload_pdf("file.pdf")
        result = client.wait_for_completion(upload_response.task_id)
except AuthenticationError:
    print("Invalid authentication token")
except ConnectionError:
    print("Cannot connect to server")
except APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=dotsocr_runner_client

# Run specific test file
python -m pytest tests/test_models.py
```

### Test Coverage

The test suite covers:
- Data model validation
- Error handling
- Client operations (mocked)

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure DotsOCR server is running
   - Check server URL and port
   - Verify firewall settings

2. **Authentication Failed**
   - Verify auth token is correct
   - Check token in server settings
   - Ensure token is passed correctly

3. **File Not Found**
   - Verify file paths are correct
   - Check file permissions
   - Ensure files exist and are accessible

4. **Timeout Errors**
   - Increase timeout values
   - Check server performance
   - Verify file sizes are within limits

### Debug Mode

Enable debug logging:

```python
from dotsocr_runner_client import setup_logging

setup_logging("DEBUG")
```

### Server Health Check

```python
from dotsocr_runner_client import DotsOCRRunnerClient

client = DotsOCRRunnerClient(server_url, token)
health = client.health_check()
print(f"Server status: {health.status}")
print(f"Version: {health.version}")
```

## Performance Tips

1. **Use Async Client**: For concurrent processing of multiple files
2. **Progress Callbacks**: Monitor progress without blocking
3. **Connection Reuse**: Use context managers (`with` statements)
4. **Appropriate Timeouts**: Set reasonable timeout values for large files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples
3. Check the test cases for usage patterns
4. Review the API documentation
