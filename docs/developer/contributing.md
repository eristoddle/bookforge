# Contributing Guide

## Welcome Contributors!

Thank you for your interest in contributing to BookForge! This guide will help you get started with contributing to the project.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/bookforge.git
cd bookforge
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Verify Setup

```bash
# Run tests
pytest

# Run linting
flake8 bookforge/
black --check bookforge/

# Run type checking
mypy bookforge/
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow these guidelines when making changes:

- Write clear, concise commit messages
- Add tests for new functionality
- Update documentation as needed
- Follow the coding standards

### 3. Test Changes

```bash
# Run full test suite
pytest

# Run specific test file
pytest tests/test_generation.py

# Run with coverage
pytest --cov=bookforge
```

### 4. Submit Pull Request

```bash
# Push changes
git push origin feature/your-feature-name

# Create pull request on GitHub
# Include description of changes and any relevant issue numbers
```

## Coding Standards

### Python Style

We follow PEP 8 with some modifications:

```python
# Good: Clear function names and docstrings
def generate_epub_from_directory(
    input_dir: str,
    output_path: str,
    title: str,
    author: str
) -> str:
    """
    Generate EPUB from directory of markdown files.
    
    Args:
        input_dir: Directory containing markdown files
        output_path: Path for output EPUB file
        title: Book title
        author: Book author
        
    Returns:
        Path to generated EPUB file
        
    Raises:
        FileNotFoundError: If input directory doesn't exist
    """
    # Implementation here
    pass

# Good: Type hints and clear variable names
def process_markdown_content(
    content: str,
    config: ProcessingConfig
) -> ProcessedContent:
    processed_html = markdown_to_html(content)
    return ProcessedContent(processed_html, config.metadata)
```

### Code Organization

```python
# File structure
class EPUBGenerator:
    """Main class for EPUB generation."""
    
    def __init__(self, config: Config):
        self.config = config
        self.processors = self._init_processors()
        
    def _init_processors(self) -> List[Processor]:
        """Initialize content processors."""
        return [
            MarkdownProcessor(),
            ImageProcessor(),
            LinkProcessor()
        ]
        
    def generate(self, source: Source) -> EPUB:
        """Generate EPUB from source."""
        # Implementation
```

### Error Handling

```python
# Good: Specific exceptions with clear messages
class BookForgeError(Exception):
    """Base exception for BookForge errors."""
    pass

class ValidationError(BookForgeError):
    """Raised when EPUB validation fails."""
    pass

def validate_epub(epub_path: str) -> None:
    if not epub_path.endswith('.epub'):
        raise ValidationError(f"Invalid file extension: {epub_path}")
        
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")
```

## Testing Guidelines

### Test Structure

```python
# tests/test_generation.py
import pytest
from bookforge import BookForge
from bookforge.exceptions import ValidationError

class TestEPUBGeneration:
    """Test EPUB generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.bookforge = BookForge()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
        
    def test_generate_from_directory_success(self):
        """Test successful EPUB generation from directory."""
        # Arrange
        input_dir = self._create_test_content()
        
        # Act
        epub_path = self.bookforge.generate_from_directory(
            input_dir=input_dir,
            title="Test Book",
            author="Test Author"
        )
        
        # Assert
        assert os.path.exists(epub_path)
        assert epub_path.endswith('.epub')
        
    def test_generate_invalid_directory_raises_error(self):
        """Test that invalid directory raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            self.bookforge.generate_from_directory(
                input_dir="/nonexistent/directory",
                title="Test Book",
                author="Test Author"
            )
```

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test performance characteristics

## Documentation

### Docstring Format

```python
def process_markdown(
    content: str,
    options: Dict[str, Any] = None
) -> str:
    """
    Process markdown content to HTML.
    
    This function converts markdown text to HTML using the configured
    markdown processor with support for extensions and custom options.
    
    Args:
        content: Raw markdown content to process
        options: Optional processing options. Supported keys:
            - extensions: List of markdown extensions to use
            - strict_mode: Whether to use strict markdown parsing
            
    Returns:
        Processed HTML content as string
        
    Raises:
        ProcessingError: If markdown processing fails
        
    Example:
        >>> html = process_markdown("# Hello World\n\nThis is **bold**.")
        >>> print(html)
        <h1>Hello World</h1><p>This is <strong>bold</strong>.</p>
    """
```

### Adding Documentation

When adding new features:

1. Update relevant documentation files
2. Add examples to the examples directory
3. Update API documentation
4. Add or update docstrings

## Issue Guidelines

### Reporting Bugs

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Environment:**
- OS: [e.g., Windows 10, macOS 12.0, Ubuntu 20.04]
- Python version: [e.g., 3.9.0]
- BookForge version: [e.g., 1.2.0]

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request.
```

## Release Process

### Version Numbers

We use semantic versioning (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. Update version in `setup.py` and `__init__.py`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Update documentation
6. Create GitHub release
7. Publish to PyPI

## Code Review Process

### Pull Request Guidelines

- **Small, focused changes**: Keep PRs small and focused
- **Clear description**: Explain what changes and why
- **Link issues**: Reference relevant issue numbers
- **Tests included**: Include tests for new functionality
- **Documentation updated**: Update docs as needed

### Review Checklist

Reviewers should check:

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No breaking changes (unless major version)
- [ ] Security considerations addressed
- [ ] Performance impact considered

## Community Guidelines

### Code of Conduct

We follow the Contributor Covenant Code of Conduct. Key points:

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy towards other community members

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

Thank you for contributing to BookForge!