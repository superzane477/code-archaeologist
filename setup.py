"""
Code Archaeologist Setup
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="code-archaeologist",
    version="0.1.0",
    description="A tool for analyzing legacy codebases and generating health reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Code Archaeologist Team",
    url="https://github.com/code-archaeologist/code-archaeologist",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "jinja2>=3.0",
        "pygments>=2.10",
        "radon>=6.0",
        "rich>=13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
        "llm": [
            "openai>=1.0",
        ],
        "full": [
            "vulture>=2.0",
            "bandit>=1.7",
            "safety>=2.0",
            "openai>=1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "code-archaeologist=code_archaeologist.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="code-analysis archaeology technical-debt legacy refactoring",
    project_urls={
        "Bug Reports": "https://github.com/code-archaeologist/code-archaeologist/issues",
        "Source": "https://github.com/code-archaeologist/code-archaeologist",
    }
)