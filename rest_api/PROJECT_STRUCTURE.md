# DotsOCRRunner Python Client - Project Structure

This document outlines the complete structure of the DotsOCR Python client implementation.

## Directory Structure

```
rest_api/
├── dotsocr_runner_client/      # Main package directory
│   ├── __init__.py             # Package initialization and exports
│   ├── models.py               # Data models and response types
│   ├── exceptions.py           # Custom exception classes
│   ├── utils.py                # Utility functions
│   ├── client.py               # Synchronous HTTP client
│   └── async_client.py         # Asynchronous HTTP client
├── examples/                   # Usage examples
│   ├── basic_usage.py          # Synchronous client examples
│   └── async_usage.py          # Asynchronous client examples
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_models.py          # Model tests
├── docs/                       # Documentation (to be generated)
├── README.md                   # Main documentation
├── PROJECT_STRUCTURE.md        # This file
├── setup.py                    # Legacy setup script
├── pyproject.toml              # Modern Python packaging configuration
├── requirements.txt            # Runtime dependencies
├── pytest.ini                 # Test configuration
└── LICENSE                     # MIT license
```

## Core Components

### 1. Data Models (`models.py`)

Defines all data structures used by the client:

- **UploadResponse**: Response from file upload endpoints
- **TaskStatusResponse**: Task status and progress information
- **OCRResult**: Final OCR results with metadata
- **DeleteResponse**: Task deletion confirmation
- **TasksListResponse**: List of all tasks
- **HealthResponse**: Server health check response

All models use `@dataclass` decorators and include `to_dict()` methods for JSON serialization.

### 2. Exception Handling (`exceptions.py`)

Comprehensive exception hierarchy:

```
DotsOCRRunnerClientError (base)
├── AuthenticationError
├── ConnectionError
├── TimeoutError
├── APIError
├── FileNotFoundError
├── InvalidFileTypeError
├── FileTooLargeError
├── TaskNotFoundError
└── TaskCreationError
```

### 3. Synchronous Client (`client.py`)

Main synchronous client implementation with methods:

- **File Operations**: `upload_pdf()`, `upload_images()`
- **Task Management**: `get_task_status()`, `get_task_result()`, `wait_for_completion()`
- **Cleanup**: `delete_task()`, `list_tasks()`
- **Health**: `health_check()`

Features:
- Context manager support (`with` statement)
- Automatic retry logic
- Progress callbacks
- Comprehensive error handling

### 4. Asynchronous Client (`async_client.py`)

Async version of the client with identical API:

- All methods are `async` and return awaitable results
- Uses `aiohttp` for HTTP requests
- Supports concurrent operations
- Same error handling and progress tracking as sync client


### 6. Utility Functions (`utils.py`)

Helper functions for:
- File validation and type checking
- Progress callback formatting
- Error message formatting
- Common data transformations

## Usage Patterns

### Basic Usage
```python
from dotsocr_runner_client import DotsOCRRunnerClient

with DotsOCRRunnerClient("http://127.0.0.1:8080", "token") as client:
    result = client.wait_for_completion(
        client.upload_pdf("document.pdf").task_id
    )
```

### Async Usage
```python
import asyncio
from dotsocr_runner_client import AsyncDotsOCRRunnerClient

async def process():
    async with AsyncDotsOCRRunnerClient("http://127.0.0.1:8080", "token") as client:
        result = await client.wait_for_completion(
            (await client.upload_pdf("document.pdf")).task_id
        )
```


## Testing

The test suite covers:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflows
- **Mock Testing**: External dependency isolation
- **Error Scenarios**: Exception handling validation

Run tests with:
```bash
pytest
pytest --cov=dotsocr_runner_client  # With coverage
```

## Packaging and Distribution

### Modern Packaging (pyproject.toml)
- Uses `setuptools` build backend
- Supports both `pip install` and `pip install -e .`
- Includes development dependencies
- Configures code quality tools

### Installation Options
```bash
# From PyPI (when published)
pip install dotsocr-client

# From source
pip install -e .

# Development installation
pip install -e ".[dev]"
```

## Development Workflow

### Code Quality
```bash
# Format code
black dotsocr_runner_client/

# Lint code
flake8 dotsocr_runner_client/

# Type checking
mypy dotsocr_runner_client/

# Run all checks
pre-commit run --all-files
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=dotsocr_runner_client --cov-report=html
```

## Integration with DotsOCR Server

The client is designed to work seamlessly with the DotsOCR REST API:

### API Endpoints Used
- `POST /api/v1/ocr/pdf/upload` - PDF upload
- `POST /api/v1/ocr/images/upload` - Image batch upload
- `GET /api/v1/ocr/status/{id}` - Task status
- `GET /api/v1/ocr/result/{id}` - Task results
- `DELETE /api/v1/ocr/task/{id}` - Task deletion
- `GET /api/v1/ocr/tasks` - List all tasks
- `GET /api/v1/health` - Health check

### Authentication
- Bearer token authentication
- Configurable timeout settings
- Automatic token inclusion in headers

### Error Handling
- HTTP status code mapping to exceptions
- Detailed error messages from API responses
- Graceful handling of network issues

## Performance Considerations

### Memory Usage
- Streaming file uploads to avoid loading large files in memory
- Efficient JSON parsing and serialization
- Minimal object creation in hot paths

### Concurrency
- Async client supports concurrent operations
- Non-blocking progress tracking

### Network Efficiency
- Connection pooling (requests/aiohttp)
- Appropriate timeout defaults
- Retry logic for transient failures

## Security Features

### Input Validation
- File type validation using magic numbers
- File size limits
- Path traversal prevention

### Authentication Security
- Secure token handling
- No credential logging
- Support for token rotation

### Data Privacy
- No sensitive data in logs
- Optional file cleanup after processing
- Secure temporary file handling

## Extensibility

The client is designed to be extensible:

### Custom Handlers
- Progress callbacks can be customized
- Error handling can be extended
- Response parsing can be modified

### Plugin Architecture
- Custom file validators can be added
- Additional API endpoints can be integrated

### Configuration
- Flexible timeout settings
- Custom headers support
- Configurable retry policies

## Future Enhancements

Planned improvements include:

- **WebSocket Support**: Real-time task updates
- **File Streaming**: Direct file streaming for large files
- **Caching Layer**: Response caching for repeated requests
- **Retry Mechanisms**: Exponential backoff retry logic
- **Framework Integration**: Django/FastAPI integration helpers
- **Monitoring**: Built-in metrics and monitoring support

## Dependencies

### Runtime Dependencies
- `requests>=2.28.0` - HTTP client for sync operations
- `aiohttp>=3.8.0` - HTTP client for async operations

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing support
- `pytest-cov>=4.0.0` - Coverage reporting
- `black>=22.0.0` - Code formatting
- `flake8>=5.0.0` - Linting
- `mypy>=1.0.0` - Type checking

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

- **Documentation**: [README.md](README.md)
- **Examples**: [examples/](examples/)
- **Issues**: GitHub Issues
- **Email**: support@dotsocr.com
