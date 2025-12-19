#!/usr/bin/env python3
"""
Setup script for DotsOCRRunner Python Client.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="dotsocr-runner-client",
    version="1.0.0",
    author="DotsOCR Team",
    author_email="support@dotsocr.com",
    description="Python client for DotsOCR REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dotsocr/dotsocr-runner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dotsocr-runner-client=dotsocr_runner_client.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dotsocr_runner_client": ["py.typed"],
    },
    keywords="ocr, optical character recognition, api client, rest api, image processing, pdf",
    project_urls={
        "Bug Reports": "https://github.com/dotsocr/dotsocr-runner/issues",
        "Source": "https://github.com/dotsocr/dotsocr-runner",
        "Documentation": "https://dotsocr-client.readthedocs.io/",
    },
)
