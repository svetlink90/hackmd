"""
Setup script for Legal Research AI Agents
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="legal-ai-agents",
    version="1.0.0",
    author="Legal Research AI Team",
    author_email="info@legal-ai-agents.com",
    description="AI agents specialized for legal research and document analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/legal-ai/legal-research-agents",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Legal",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.3.0",
        "anthropic>=0.7.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "transformers>=4.35.0",
        "torch>=2.0.0",
        "sentence-transformers>=2.2.2",
        "pypdf2>=3.0.1",
        "python-docx>=0.8.11",
        "pdfplumber>=0.9.0",
        "pymupdf>=1.23.0",
        "python-magic>=0.4.27",
        "nltk>=3.8.1",
        "spacy>=3.7.0",
        "textstat>=0.7.3",
        "fuzzywuzzy>=0.18.0",
        "python-levenshtein>=0.20.9",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "selenium>=4.15.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "flask>=3.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "pyyaml>=6.0.1",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-mock>=3.12.0",
        "loguru>=0.7.2",
        "tqdm>=4.66.0",
        "click>=8.1.7",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "advanced": [
            "chromadb>=0.4.0",
            "faiss-cpu>=1.7.4",
            "elasticsearch>=8.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "legal-ai-setup=deployment.local_setup:main",
        ],
    },
    include_package_data=True,
    package_data={
        "legal-ai-agents": [
            "config/*.py",
            "examples/*.py",
            "tests/*.py",
            "deployment/*.py",
            "*.md",
            "*.txt",
            ".env.example",
        ],
    },
    keywords="legal ai agents research document analysis nlp",
    project_urls={
        "Bug Reports": "https://github.com/legal-ai/legal-research-agents/issues",
        "Source": "https://github.com/legal-ai/legal-research-agents",
        "Documentation": "https://github.com/legal-ai/legal-research-agents/blob/main/README.md",
    },
)