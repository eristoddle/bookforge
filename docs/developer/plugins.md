# Plugin Development

## Overview

BookForge supports a flexible plugin system that allows developers to extend functionality without modifying the core codebase.

## Plugin Architecture

### Plugin Interface

All plugins must implement the base `Plugin` interface:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class Plugin(ABC):
    """Base class for all BookForge plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        pass
    
    @abstractmethod
    def execute(self, context: Any) -> Any:
        """Execute the plugin logic."""
        pass
```

## Plugin Types

### 1. Processor Plugins

Process content during EPUB generation:

```python
from bookforge.plugins import ProcessorPlugin
from bookforge.models import Content

class CustomMarkdownProcessor(ProcessorPlugin):
    """Custom markdown processor plugin."""
    
    name = "custom-markdown"
    version = "1.0.0"
    
    def process(self, content: Content) -> Content:
        """Process markdown content with custom rules."""
        # Add custom markdown processing logic
        processed_text = self._apply_custom_rules(content.text)
        
        return Content(
            text=processed_text,
            metadata=content.metadata,
            path=content.path
        )
    
    def _apply_custom_rules(self, text: str) -> str:
        # Custom processing logic
        text = text.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
        text = text.replace("{{version}}", self.get_config("version", "1.0"))
        return text
```

### 2. Theme Plugins

Extend theme functionality:

```python
from bookforge.plugins import ThemePlugin

class CustomThemePlugin(ThemePlugin):
    """Custom theme plugin."""
    
    name = "academic-plus"
    version = "1.0.0"
    
    def apply_theme(self, content: Content, config: ThemeConfig) -> StyledContent:
        """Apply custom theme styling."""
        # Base theme application
        styled_content = super().apply_theme(content, config)
        
        # Add custom CSS
        custom_css = self._generate_custom_css(config)
        styled_content.add_css(custom_css)
        
        return styled_content
    
    def _generate_custom_css(self, config: ThemeConfig) -> str:
        return f"""
        .chapter-title {{
            color: {config.primary_color};
            border-bottom: 2px solid {config.accent_color};
        }}
        
        .footnote {{
            font-size: 0.8em;
            color: #666;
        }}
        """
```

### 3. Source Plugins

Add new input source types:

```python
from bookforge.plugins import SourcePlugin
from bookforge.models import Content

class NotionSourcePlugin(SourcePlugin):
    """Plugin to generate EPUB from Notion pages."""
    
    name = "notion-source"
    version = "1.0.0"
    
    def load_content(self, source_config: Dict[str, Any]) -> List[Content]:
        """Load content from Notion."""
        notion_client = NotionClient(
            token=source_config["notion_token"]
        )
        
        database_id = source_config["database_id"]
        pages = notion_client.get_database_pages(database_id)
        
        content_list = []
        for page in pages:
            content = Content(
                text=self._convert_notion_to_markdown(page),
                metadata={
                    "title": page.title,
                    "created": page.created_time,
                    "updated": page.last_edited_time
                },
                path=f"notion-{page.id}.md"
            )
            content_list.append(content)
        
        return content_list
```

### 4. Export Plugins

Add new output formats:

```python
from bookforge.plugins import ExportPlugin

class PDFExportPlugin(ExportPlugin):
    """Plugin to export EPUB as PDF."""
    
    name = "pdf-export"
    version = "1.0.0"
    
    def export(self, epub_path: str, output_path: str, config: Dict[str, Any]) -> str:
        """Convert EPUB to PDF."""
        from weasyprint import HTML, CSS
        
        # Extract EPUB content
        epub_content = self._extract_epub_content(epub_path)
        
        # Convert to PDF
        html = HTML(string=epub_content)
        css = CSS(string=self._get_pdf_styles(config))
        
        pdf_path = output_path or epub_path.replace('.epub', '.pdf')
        html.write_pdf(pdf_path, stylesheets=[css])
        
        return pdf_path
```

## Plugin Configuration

### Plugin Manifest

Create a `plugin.yaml` file for your plugin:

```yaml
name: "custom-markdown"
version: "1.0.0"
description: "Custom markdown processor with template variables"
author: "Your Name"
homepage: "https://github.com/username/bookforge-custom-markdown"

type: "processor"
entry_point: "custom_markdown:CustomMarkdownProcessor"

dependencies:
  - "bookforge>=1.0.0"
  - "jinja2>=3.0.0"

configuration:
  schema:
    type: "object"
    properties:
      template_vars:
        type: "object"
        description: "Template variables for replacement"
      date_format:
        type: "string"
        default: "%Y-%m-%d"
        description: "Date format for {{date}} variable"

permissions:
  - "read_content"
  - "modify_content"
```

### Loading Configuration

```python
class CustomMarkdownProcessor(ProcessorPlugin):
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        self.template_vars = config.get("template_vars", {})
        self.date_format = config.get("date_format", "%Y-%m-%d")
        
        # Validate configuration
        if not isinstance(self.template_vars, dict):
            raise ValueError("template_vars must be a dictionary")
```

## Plugin Installation

### Method 1: pip Install

```bash
pip install bookforge-plugin-custom-markdown
```

### Method 2: Local Development

```bash
# Install in development mode
pip install -e ./my-plugin/

# Or install from directory
pip install ./my-plugin/
```

### Method 3: Git Install

```bash
pip install git+https://github.com/username/bookforge-plugin.git
```

## Using Plugins

### Configuration File

Enable plugins in `bookforge.yaml`:

```yaml
plugins:
  - name: "custom-markdown"
    enabled: true
    config:
      template_vars:
        version: "2.1.0"
        author: "John Doe"
      date_format: "%B %d, %Y"
  
  - name: "pdf-export"
    enabled: true
    config:
      page_size: "A4"
      margin: "2cm"
```

### Programmatic Usage

```python
from bookforge import BookForge
from bookforge.plugins import PluginManager

# Load plugins
plugin_manager = PluginManager()
plugin_manager.load_plugin("custom-markdown")
plugin_manager.load_plugin("pdf-export")

# Configure BookForge with plugins
bf = BookForge(plugin_manager=plugin_manager)

# Generate EPUB with plugins
epub_path = bf.generate_from_directory("./content")

# Export to PDF using plugin
pdf_path = plugin_manager.get_plugin("pdf-export").export(epub_path)
```

## Plugin Development Best Practices

### 1. Error Handling

```python
class SafePlugin(Plugin):
    def execute(self, context: Any) -> Any:
        try:
            return self._process(context)
        except Exception as e:
            self.logger.error(f"Plugin {self.name} failed: {e}")
            # Return original context on failure
            return context
```

### 2. Logging

```python
import logging

class LoggingPlugin(Plugin):
    def __init__(self):
        self.logger = logging.getLogger(f"bookforge.plugins.{self.name}")
    
    def process(self, content: Content) -> Content:
        self.logger.info(f"Processing content: {content.path}")
        # Process content
        self.logger.debug(f"Processed {len(content.text)} characters")
        return processed_content
```

### 3. Testing

```python
import pytest
from bookforge.models import Content
from my_plugin import CustomMarkdownProcessor

class TestCustomMarkdownProcessor:
    def setup_method(self):
        self.processor = CustomMarkdownProcessor()
        self.processor.initialize({
            "template_vars": {"version": "1.0"},
            "date_format": "%Y-%m-%d"
        })
    
    def test_template_replacement(self):
        content = Content(
            text="Version: {{version}}",
            metadata={},
            path="test.md"
        )
        
        result = self.processor.process(content)
        assert "Version: 1.0" in result.text
    
    def test_date_replacement(self):
        content = Content(
            text="Date: {{date}}",
            metadata={},
            path="test.md"
        )
        
        result = self.processor.process(content)
        assert "Date: " in result.text
        # Verify date format
```

### 4. Documentation

Create comprehensive documentation:

```markdown
# Custom Markdown Plugin

## Installation

```bash
pip install bookforge-plugin-custom-markdown
```

## Configuration

```yaml
plugins:
  - name: "custom-markdown"
    config:
      template_vars:
        version: "1.0.0"
        author: "Author Name"
```

## Template Variables

- `{{date}}`: Current date
- `{{version}}`: Project version
- `{{author}}`: Book author
- Custom variables from configuration
```

## Plugin Distribution

### PyPI Package

Create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="bookforge-plugin-custom-markdown",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "bookforge>=1.0.0",
    ],
    entry_points={
        "bookforge.plugins": [
            "custom-markdown = custom_markdown:CustomMarkdownProcessor",
        ],
    },
    author="Your Name",
    description="Custom markdown processor for BookForge",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8+",
    ],
)
```

### GitHub Release

Tag and release:

```bash
git tag v1.0.0
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0" --notes "Initial release"
```