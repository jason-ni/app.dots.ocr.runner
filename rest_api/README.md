# DotsOCRRunner Python Client

A comprehensive Python client for the DotsOCR REST API, supporting both synchronous and asynchronous operations.

## Features

- **Synchronous and Asynchronous APIs**: Choose between `DotsOCRRunnerClient` (sync) and `AsyncDotsOCRRunnerClient` (async)
- **Error Handling**: Comprehensive error handling with custom exception types
- **Type Safety**: Full type hints for better IDE support and error detection
- **Easy Integration**: Simple API for easy integration

## Installation

### From PyPI (recommended)

```bash
pip install dotsocr-client
```

### From Source

```bash
git clone https://github.com/jason-ni/app.dots.ocr.runner.git
cd app.dots.ocr.runner/rest_api
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/jason-ni/app.dots.ocr.runner.git
cd app.dots.ocr.runner/rest_api
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from dotsocr_runner_client import DotsOCRRunnerClient

# Create client
with DotsOCRRunnerClient("http://127.0.0.1:8080", "your-auth-token") as client:
    # Upload PDF
    upload_response = client.upload_pdf("document.pdf")
    print(f"Task ID: {upload_response.task_id}")
    
    # Wait for completion
    result = client.wait_for_completion(upload_response.task_id)
    print(f"OCR Result: {result.result['content']}")
```

### Async Usage

```python
import asyncio
from dotsocr_runner_client import AsyncDotsOCRRunnerClient

async def process_document():
    async with AsyncDotsOCRRunnerClient("http://127.0.0.1:8080", "your-auth-token") as client:
        # Upload images
        upload_response = await client.upload_images(["img1.jpg", "img2.png"])
        
        # Wait for completion
        result = await client.wait_for_completion(upload_response.task_id)
        print(f"OCR Result: {result.result['content']}")

asyncio.run(process_document())
```


## Advanced Usage

### DPI Configuration

The DotsOCR client supports custom DPI (Dots Per Inch) settings for both PDF and image processing. DPI affects the resolution and quality of OCR processing.

#### Default DPI Values
- **PDFs**: 150 DPI (balanced quality and performance)
- **Images**: 72 DPI (standard web resolution)

#### Custom DPI Usage

```python
from dotsocr_runner_client import DotsOCRRunnerClient

with DotsOCRRunnerClient("http://127.0.0.1:8080", "your-auth-token") as client:
    # PDF with high DPI for maximum quality
    upload_response = client.upload_pdf("document.pdf", dpi=300)
    
    # Images with medium DPI for balanced quality
    upload_response = client.upload_images(["img1.jpg", "img2.png"], dpi=150)
    
    # Images with low DPI for faster processing
    upload_response = client.upload_images(["img1.jpg", "img2.png"], dpi=100)
```

#### DPI Guidelines

| Use Case | Recommended DPI | Description |
|----------|----------------|-------------|
| High Quality PDFs | 300 | Maximum OCR accuracy, slower processing |
| Standard PDFs | 150 (default) | Balanced quality and performance |
| Fast PDF Processing | 100 | Quick processing, reduced accuracy |
| High Quality Images | 150-200 | Better OCR for detailed images |
| Standard Images | 72 (default) | Good for most web images |
| Fast Image Processing | 72-100 | Quick processing for simple images |

#### Valid DPI Range
- **Minimum**: 72 DPI
- **Maximum**: 200 DPI (for images), 300 DPI (for PDFs)
- **Recommended**: 72-300 DPI depending on use case

#### Async DPI Usage

```python
import asyncio
from dotsocr_runner_client import AsyncDotsOCRRunnerClient

async def process_with_custom_dpi():
    async with AsyncDotsOCRRunnerClient("http://127.0.0.1:8080", "your-auth-token") as client:
        # Concurrent processing with different DPIs
        tasks = [
            client.upload_pdf("doc1.pdf", dpi=300),  # High quality
            client.upload_images(["img1.jpg"], dpi=100),  # Fast processing
        ]
        
        upload_responses = await asyncio.gather(*tasks)
        
        # Wait for all to complete
        for response in upload_responses:
            result = await client.wait_for_completion(response.task_id)
            print(f"Task {response.task_id} completed")

asyncio.run(process_with_custom_dpi())
```

### Error Handling

```python
from dotsocr_runner_client import DotsOCRRunnerClient, AuthenticationError, ConnectionError, APIError, TaskNotCompletedError

try:
    with DotsOCRRunnerClient("http://127.0.0.1:8080", "your-auth-token") as client:
        result = client.wait_for_completion(task_id)
        # Try to delete the task after completion
        client.delete_task(task_id)
        
except AuthenticationError:
    print("Authentication failed. Check your token.")
except ConnectionError:
    print("Cannot connect to server. Check if server is running.")
except TaskNotCompletedError as e:
    print(f"Cannot delete task: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## API Reference

### DotsOCRRunnerClient (Synchronous)

#### Initialization

```python
DotsOCRRunnerClient(base_url="http://127.0.0.1:8080", auth_token=None, timeout=30.0)
```

#### Methods

- `upload_pdf(pdf_path: str, dpi: Optional[int] = None) -> UploadResponse`
- `upload_images(image_paths: List[str], dpi: Optional[int] = None) -> UploadResponse`
- `get_task_status(task_id: str) -> TaskStatusResponse`
- `get_task_result(task_id: str) -> OCRResult`
- `wait_for_completion(task_id: str, poll_interval=2.0, progress_callback=None) -> OCRResult`
- `delete_task(task_id: str) -> DeleteResponse`: Delete a completed task and clean up files (only completed tasks can be deleted)
- `list_tasks() -> TasksListResponse`
- `health_check() -> HealthResponse`

### AsyncDotsOCRRunnerClient (Asynchronous)

Same methods as `DotsOCRRunnerClient` but all are `async` and return awaitable results.

## Data Models

### UploadResponse

```python
@dataclass
class UploadResponse:
    task_id: str
    status: str
    file_type: str
    filename: str
    estimated_duration: str
```

### TaskStatusResponse

```python
@dataclass
class TaskStatusResponse:
    task_id: str
    status: str
    progress: float
    current_step: Optional[str]
    queue_position: Optional[int]
    estimated_remaining: Optional[str]
```

### OCRResult

```python
@dataclass
class OCRResult:
    task_id: str
    status: str
    result: Dict[str, Any]
    metadata: Dict[str, Any]
```

## Exceptions

- `DotsOCRRunnerClientError`: Base exception
- `AuthenticationError`: Authentication failed
- `ConnectionError`: Connection issues
- `TimeoutError`: Request timeout
- `APIError`: General API errors
- `FileNotFoundError`: File not found
- `InvalidFileTypeError`: Invalid file type
- `FileTooLargeError`: File too large
- `TaskNotFoundError`: Task not found
- `TaskCreationError`: Task creation failed
- `TaskNotCompletedError`: Task cannot be deleted because it's not completed

## Configuration

### Server Configuration

Make sure your DotsOCR server is running and configured with:

- HTTP server enabled
- Authentication token set
- Proper file size limits
- CORS origins configured (if needed)

### Client Configuration

```python
# Custom timeout
client = DotsOCRRunnerClient(timeout=60.0)

# Custom headers
client = DotsOCRRunnerClient()
client.session.headers.update({'Custom-Header': 'value'})
```

## Examples

See the `examples/` directory for comprehensive examples:

- `basic_usage.py`: Synchronous usage examples
- `async_usage.py`: Asynchronous usage examples

Run examples:

```bash
cd examples
python basic_usage.py
python async_usage.py
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=dotsocr_runner_client

# Run async tests
pytest tests/test_async_client.py
```

### Code Quality

```bash
# Format code
black dotsocr_runner_client/

# Lint code
flake8 dotsocr_runner_client/

# Type checking
mypy dotsocr_runner_client/
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/jason-ni/app.dots.ocr.runner/issues)

## Changelog

### v1.0.0

- Initial release
- Synchronous and asynchronous client implementations
- Comprehensive error handling
- Full type hints
- Documentation and examples

## Requirements

- Python 3.8+
- `requests>=2.28.0` (for sync client)
- `aiohttp>=3.8.0` (for async client)


