# Architecture Overview

## System Architecture

BookForge follows a modular, microservices-inspired architecture designed for scalability and maintainability.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │  Web Interface  │    │   Python API    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │      Core Engine        │
                    │  ┌─────────────────────┐ │
                    │  │   Generation API    │ │
                    │  └─────────────────────┘ │
                    │  ┌─────────────────────┐ │
                    │  │  Processing Engine  │ │
                    │  └─────────────────────┘ │
                    │  ┌─────────────────────┐ │
                    │  │   Theme System      │ │
                    │  └─────────────────────┘ │
                    │  ┌─────────────────────┐ │
                    │  │   Plugin System     │ │
                    │  └─────────────────────┘ │
                    └─────────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │     Data Layer          │
                    │  ┌─────────────────────┐ │
                    │  │   File System       │ │
                    │  └─────────────────────┘ │
                    │  ┌─────────────────────┐ │
                    │  │   GitHub API        │ │
                    │  └─────────────────────┘ │
                    │  ┌─────────────────────┐ │
                    │  │   Cache Layer       │ │
                    │  └─────────────────────┘ │
                    └─────────────────────────┘
```

## Core Components

### 1. Generation API

Central orchestrator for EPUB generation:

```python
class GenerationAPI:
    def __init__(self):
        self.processor = ProcessingEngine()
        self.theme_manager = ThemeManager()
        self.validator = EPUBValidator()
    
    def generate_epub(self, source: Source, config: Config) -> EPUB:
        # Parse and process content
        content = self.processor.process(source)
        
        # Apply theme and styling
        styled_content = self.theme_manager.apply_theme(content, config.theme)
        
        # Generate EPUB structure
        epub = EPUBBuilder().build(styled_content, config)
        
        # Validate output
        if config.validate:
            self.validator.validate(epub)
        
        return epub
```

### 2. Processing Engine

Handles content transformation pipeline:

```python
class ProcessingEngine:
    def __init__(self):
        self.processors = [
            MarkdownProcessor(),
            ImageProcessor(),
            LinkProcessor(),
            TOCProcessor()
        ]
    
    def process(self, source: Source) -> ProcessedContent:
        content = source.load()
        
        for processor in self.processors:
            content = processor.process(content)
        
        return content
```

### 3. Theme System

Manages styling and layout:

```python
class ThemeManager:
    def __init__(self):
        self.theme_registry = ThemeRegistry()
        self.css_processor = CSSProcessor()
    
    def apply_theme(self, content: Content, theme_config: ThemeConfig) -> StyledContent:
        theme = self.theme_registry.get_theme(theme_config.name)
        css = self.css_processor.compile(theme, theme_config.overrides)
        
        return StyledContent(content, css, theme.templates)
```

## Data Flow

### 1. Input Processing

```
Markdown Files → Parser → AST → Content Model
     ↓
GitHub Repo → Downloader → File System → Parser → Content Model
     ↓
Directory → Scanner → File List → Parser → Content Model
```

### 2. Content Transformation

```
Content Model → Processors → Enhanced Content
    ↓
    ├── Markdown → HTML
    ├── Images → Optimized Images
    ├── Links → Validated Links
    └── Structure → TOC + Navigation
```

### 3. EPUB Generation

```
Enhanced Content → Theme Application → Styled Content
    ↓
Styled Content → EPUB Builder → EPUB Package
    ↓
EPUB Package → Validator → Final EPUB
```

## Module Structure

```
bookforge/
├── core/                   # Core engine
│   ├── __init__.py
│   ├── api.py             # Main API interface
│   ├── config.py          # Configuration management
│   └── exceptions.py      # Custom exceptions
├── processors/            # Content processors
│   ├── __init__.py
│   ├── markdown.py        # Markdown processing
│   ├── images.py          # Image optimization
│   ├── links.py           # Link validation
│   └── toc.py             # Table of contents
├── themes/                # Theme system
│   ├── __init__.py
│   ├── manager.py         # Theme management
│   ├── registry.py        # Theme registry
│   └── builtin/           # Built-in themes
├── sources/               # Input sources
│   ├── __init__.py
│   ├── directory.py       # Directory source
│   ├── github.py          # GitHub source
│   └── base.py            # Base source class
├── builders/              # EPUB builders
│   ├── __init__.py
│   ├── epub3.py           # EPUB 3 builder
│   └── validator.py       # EPUB validator
├── plugins/               # Plugin system
│   ├── __init__.py
│   ├── manager.py         # Plugin management
│   └── base.py            # Base plugin class
├── cli/                   # Command line interface
│   ├── __init__.py
│   └── main.py            # CLI entry point
└── web/                   # Web interface
    ├── __init__.py
    ├── app.py             # Flask application
    ├── api.py             # REST API
    └── templates/         # Web templates
```

## Design Patterns

### 1. Strategy Pattern

Used for different input sources:

```python
class Source(ABC):
    @abstractmethod
    def load(self) -> Content:
        pass

class DirectorySource(Source):
    def load(self) -> Content:
        # Load from directory
        
class GitHubSource(Source):
    def load(self) -> Content:
        # Load from GitHub
```

### 2. Chain of Responsibility

Used for content processing:

```python
class Processor(ABC):
    def __init__(self, next_processor=None):
        self.next_processor = next_processor
    
    @abstractmethod
    def process(self, content: Content) -> Content:
        processed = self._process(content)
        
        if self.next_processor:
            return self.next_processor.process(processed)
        
        return processed
```

### 3. Factory Pattern

Used for theme creation:

```python
class ThemeFactory:
    @staticmethod
    def create_theme(theme_name: str) -> Theme:
        if theme_name == "default":
            return DefaultTheme()
        elif theme_name == "academic":
            return AcademicTheme()
        else:
            raise ValueError(f"Unknown theme: {theme_name}")
```

## Performance Considerations

### 1. Caching

- **Template Caching**: Compiled templates cached in memory
- **Asset Caching**: Images and CSS cached with content hashing
- **GitHub Caching**: Repository content cached for 15 minutes

### 2. Parallel Processing

- **Image Processing**: Parallel optimization of images
- **Content Processing**: Concurrent processing of chapters
- **Validation**: Parallel validation of EPUB components

### 3. Memory Management

- **Streaming**: Large files processed in chunks
- **Lazy Loading**: Content loaded on-demand
- **Cleanup**: Temporary files cleaned up automatically

## Security Architecture

### 1. Input Validation

- **Path Traversal**: All file paths validated
- **Content Sanitization**: HTML content sanitized
- **Size Limits**: File size limits enforced

### 2. Authentication

- **API Keys**: JWT-based API authentication
- **GitHub Tokens**: Secure token storage
- **Rate Limiting**: Request rate limiting implemented

### 3. Sandboxing

- **Process Isolation**: Content processing in isolated environment
- **File System**: Restricted file system access
- **Network**: Limited network access for security