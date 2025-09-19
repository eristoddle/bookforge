# Python API Reference

## Installation

```bash
pip install bookforge
```

## Quick Start

```python
from bookforge import BookForge

# Initialize BookForge
bf = BookForge()

# Generate EPUB from directory
epub_path = bf.generate_from_directory(
    input_dir="./content",
    output_path="./my-book.epub",
    title="My Book",
    author="Author Name"
)

print(f"EPUB generated: {epub_path}")
```

## Core Classes

### BookForge

Main class for EPUB generation.

```python
class BookForge:
    def __init__(self, config_path=None, theme=None):
        """
        Initialize BookForge instance.
        
        Args:
            config_path (str): Path to configuration file
            theme (str): Theme name to use
        """
```

#### Methods

##### generate_from_directory()

```python
def generate_from_directory(
    self,
    input_dir: str,
    output_path: str = None,
    title: str = None,
    author: str = None,
    **kwargs
) -> str:
    """
    Generate EPUB from a directory of markdown files.
    
    Args:
        input_dir: Directory containing markdown files
        output_path: Path for output EPUB file
        title: Book title
        author: Book author
        **kwargs: Additional book metadata
        
    Returns:
        str: Path to generated EPUB file
        
    Raises:
        FileNotFoundError: If input directory doesn't exist
        ValidationError: If EPUB validation fails
    """
```

##### generate_from_github()

```python
def generate_from_github(
    self,
    repo_url: str,
    output_path: str = None,
    branch: str = "main",
    path: str = "",
    token: str = None,
    **kwargs
) -> str:
    """
    Generate EPUB from GitHub repository.
    
    Args:
        repo_url: GitHub repository URL
        output_path: Path for output EPUB file
        branch: Git branch to use
        path: Subdirectory path in repository
        token: GitHub access token
        **kwargs: Additional book metadata
        
    Returns:
        str: Path to generated EPUB file
    """
```

### Book

Represents book metadata and content.

```python
class Book:
    def __init__(self, title: str, author: str):
        self.title = title
        self.author = author
        self.chapters = []
        self.metadata = {}
    
    def add_chapter(self, chapter: Chapter):
        """Add a chapter to the book."""
        
    def set_metadata(self, **kwargs):
        """Set book metadata."""
        
    def validate(self) -> bool:
        """Validate book structure."""
```

### Chapter

Represents a book chapter.

```python
class Chapter:
    def __init__(self, title: str, content: str, order: int = 0):
        self.title = title
        self.content = content
        self.order = order
        self.id = None
    
    @classmethod
    def from_markdown_file(cls, file_path: str) -> 'Chapter':
        """Create chapter from markdown file."""
        
    def to_html(self) -> str:
        """Convert chapter content to HTML."""
```

## Configuration

### Using Configuration Files

```python
from bookforge import BookForge

# Load from configuration file
bf = BookForge(config_path="bookforge.yaml")

# Generate with configuration
epub_path = bf.generate_from_directory("./content")
```

### Programmatic Configuration

```python
from bookforge import BookForge, Config

# Create configuration programmatically
config = Config({
    'book': {
        'title': 'My Book',
        'author': 'Author Name',
        'language': 'en'
    },
    'theme': {
        'name': 'academic'
    },
    'output': {
        'validate': True
    }
})

bf = BookForge(config=config)
```

## Advanced Usage

### Custom Processing

```python
from bookforge import BookForge, processors

bf = BookForge()

# Add custom processor
bf.add_processor(processors.ImageOptimizer(quality=85))
bf.add_processor(processors.LinkValidator())

# Custom markdown extensions
bf.set_markdown_extensions(['tables', 'codehilite', 'toc'])

epub_path = bf.generate_from_directory("./content")
```

### Batch Processing

```python
from bookforge import BookForge
import os

bf = BookForge()

books = [
    {"dir": "./book1", "title": "Book One"},
    {"dir": "./book2", "title": "Book Two"},
    {"dir": "./book3", "title": "Book Three"}
]

for book in books:
    try:
        epub_path = bf.generate_from_directory(
            input_dir=book["dir"],
            title=book["title"],
            author="Series Author"
        )
        print(f"Generated: {epub_path}")
    except Exception as e:
        print(f"Failed to generate {book['title']}: {e}")
```

### Theme Customization

```python
from bookforge import BookForge, Theme

# Load custom theme
theme = Theme.load_from_directory("./my-theme")

bf = BookForge(theme=theme)

# Or modify existing theme
bf.theme.set_option('chapter_numbering', True)
bf.theme.set_color('primary', '#2c3e50')
```

## Error Handling

```python
from bookforge import BookForge, BookForgeError, ValidationError

bf = BookForge()

try:
    epub_path = bf.generate_from_directory("./content")
except FileNotFoundError as e:
    print(f"Input directory not found: {e}")
except ValidationError as e:
    print(f"EPUB validation failed: {e}")
except BookForgeError as e:
    print(f"BookForge error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Async Support

```python
import asyncio
from bookforge import AsyncBookForge

async def generate_books():
    bf = AsyncBookForge()
    
    # Generate multiple books concurrently
    tasks = [
        bf.generate_from_directory("./book1"),
        bf.generate_from_directory("./book2"),
        bf.generate_from_github("https://github.com/user/repo")
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Run async generation
epub_paths = asyncio.run(generate_books())
```