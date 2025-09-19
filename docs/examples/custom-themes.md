# Custom Themes

## Creating Your First Custom Theme

### Basic Theme Structure

Create a custom theme directory:

```
my-custom-theme/
├── theme.yaml
├── styles/
│   ├── base.css
│   ├── typography.css
│   └── layout.css
├── templates/
│   ├── chapter.html
│   ├── toc.html
│   └── cover.html
└── assets/
    ├── fonts/
    └── images/
```

### Theme Configuration (`theme.yaml`)

```yaml
name: "Corporate Professional"
version: "1.0.0"
author: "Your Name"
description: "Professional theme for corporate documentation"

# Base theme to inherit from (optional)
extends: "default"

# Theme metadata
metadata:
  category: "business"
  tags: ["professional", "corporate", "clean"]
  preview_image: "preview.png"

# Default configuration
defaults:
  colors:
    primary: "#2c3e50"
    secondary: "#3498db"
    accent: "#e74c3c"
    text: "#2c3e50"
    background: "#ffffff"
    muted: "#95a5a6"
  
  typography:
    heading_font: "Montserrat, sans-serif"
    body_font: "Source Sans Pro, sans-serif"
    code_font: "Source Code Pro, monospace"
    base_size: "16px"
    line_height: "1.6"
  
  layout:
    max_width: "800px"
    margin: "2rem"
    chapter_break: "page"
    toc_depth: 3

# Customizable options
options:
  - name: "logo_position"
    type: "select"
    default: "header"
    choices: ["header", "footer", "cover-only"]
    description: "Where to place the company logo"
  
  - name: "color_scheme"
    type: "select"
    default: "blue"
    choices: ["blue", "green", "purple", "orange"]
    description: "Primary color scheme"
  
  - name: "chapter_numbering"
    type: "boolean"
    default: true
    description: "Enable automatic chapter numbering"
  
  - name: "watermark_text"
    type: "string"
    default: ""
    description: "Optional watermark text"

# Required fonts (will be downloaded if not available)
fonts:
  - name: "Montserrat"
    weights: [400, 600, 700]
    url: "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700"
  
  - name: "Source Sans Pro"
    weights: [400, 600]
    url: "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600"
```

## Advanced Theme Development

### Dynamic Styles with CSS Variables

`styles/base.css`:
```css
:root {
  /* Colors - can be overridden by theme options */
  --primary-color: var(--theme-primary, #2c3e50);
  --secondary-color: var(--theme-secondary, #3498db);
  --accent-color: var(--theme-accent, #e74c3c);
  --text-color: var(--theme-text, #2c3e50);
  --background-color: var(--theme-background, #ffffff);
  --muted-color: var(--theme-muted, #95a5a6);
  
  /* Typography */
  --heading-font: var(--theme-heading-font, "Montserrat, sans-serif");
  --body-font: var(--theme-body-font, "Source Sans Pro, sans-serif");
  --code-font: var(--theme-code-font, "Source Code Pro, monospace");
  --base-font-size: var(--theme-base-size, 16px);
  --line-height: var(--theme-line-height, 1.6);
  
  /* Layout */
  --max-width: var(--theme-max-width, 800px);
  --margin: var(--theme-margin, 2rem);
}

/* Base styles */
body {
  font-family: var(--body-font);
  font-size: var(--base-font-size);
  line-height: var(--line-height);
  color: var(--text-color);
  background-color: var(--background-color);
  max-width: var(--max-width);
  margin: 0 auto;
  padding: var(--margin);
}

/* Dynamic color schemes */
.theme-blue {
  --theme-primary: #2c3e50;
  --theme-secondary: #3498db;
  --theme-accent: #e74c3c;
}

.theme-green {
  --theme-primary: #27ae60;
  --theme-secondary: #2ecc71;
  --theme-accent: #f39c12;
}

.theme-purple {
  --theme-primary: #8e44ad;
  --theme-secondary: #9b59b6;
  --theme-accent: #e67e22;
}
```

### Custom Chapter Template

`templates/chapter.html`:
```html
<div class="chapter" data-chapter="{{ chapter.number }}">
  <!-- Chapter header -->
  <header class="chapter-header">
    {% if config.chapter_numbering %}
    <div class="chapter-number">Chapter {{ chapter.number }}</div>
    {% endif %}
    
    <h1 class="chapter-title">{{ chapter.title }}</h1>
    
    {% if chapter.subtitle %}
    <div class="chapter-subtitle">{{ chapter.subtitle }}</div>
    {% endif %}
    
    {% if chapter.author and chapter.author != book.author %}
    <div class="chapter-author">by {{ chapter.author }}</div>
    {% endif %}
  </header>
  
  <!-- Chapter content -->
  <div class="chapter-content">
    {{ chapter.content|safe }}
  </div>
  
  <!-- Chapter footer -->
  <footer class="chapter-footer">
    {% if config.watermark_text %}
    <div class="watermark">{{ config.watermark_text }}</div>
    {% endif %}
    
    <div class="chapter-navigation">
      {% if chapter.previous %}
      <a href="#chapter-{{ chapter.previous.number }}" class="nav-previous">
        ← {{ chapter.previous.title }}
      </a>
      {% endif %}
      
      {% if chapter.next %}
      <a href="#chapter-{{ chapter.next.number }}" class="nav-next">
        {{ chapter.next.title }} →
      </a>
      {% endif %}
    </div>
  </footer>
</div>
```

### Interactive Theme Options

Create a theme configuration interface:

```python
from bookforge.themes import ThemeBuilder
from typing import Dict, Any

class CorporateThemeBuilder(ThemeBuilder):
    """Builder for corporate professional theme."""
    
    def __init__(self):
        self.theme_name = "corporate-professional"
        self.base_path = Path(__file__).parent
    
    def build_theme(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Build theme with custom options."""
        # Start with base configuration
        config = self._load_base_config()
        
        # Apply color scheme
        if options.get("color_scheme"):
            config = self._apply_color_scheme(config, options["color_scheme"])
        
        # Apply logo settings
        if options.get("logo_url"):
            config = self._configure_logo(config, options)
        
        # Generate CSS with variables
        css = self._generate_css(config, options)
        
        return {
            "css": css,
            "templates": self._load_templates(),
            "assets": self._prepare_assets(options),
            "config": config
        }
    
    def _apply_color_scheme(self, config: Dict, scheme: str) -> Dict:
        """Apply selected color scheme."""
        schemes = {
            "blue": {
                "primary": "#2c3e50",
                "secondary": "#3498db",
                "accent": "#e74c3c"
            },
            "green": {
                "primary": "#27ae60",
                "secondary": "#2ecc71",
                "accent": "#f39c12"
            },
            "purple": {
                "primary": "#8e44ad",
                "secondary": "#9b59b6",
                "accent": "#e67e22"
            }
        }
        
        if scheme in schemes:
            config["colors"].update(schemes[scheme])
        
        return config
    
    def _configure_logo(self, config: Dict, options: Dict) -> Dict:
        """Configure logo placement."""
        logo_config = {
            "url": options["logo_url"],
            "position": options.get("logo_position", "header"),
            "max_width": options.get("logo_max_width", "200px"),
            "alt_text": options.get("logo_alt", "Company Logo")
        }
        
        config["logo"] = logo_config
        return config
    
    def _generate_css(self, config: Dict, options: Dict) -> str:
        """Generate CSS with theme variables."""
        css_template = """
        :root {
          --theme-primary: {{ colors.primary }};
          --theme-secondary: {{ colors.secondary }};
          --theme-accent: {{ colors.accent }};
          --theme-text: {{ colors.text }};
          --theme-background: {{ colors.background }};
          
          --theme-heading-font: {{ typography.heading_font }};
          --theme-body-font: {{ typography.body_font }};
          --theme-base-size: {{ typography.base_size }};
          --theme-line-height: {{ typography.line_height }};
        }
        
        {% if logo %}
        .logo {
          max-width: {{ logo.max_width }};
          {% if logo.position == 'center' %}
          display: block;
          margin: 0 auto;
          {% endif %}
        }
        {% endif %}
        
        {% if watermark_text %}
        .watermark::before {
          content: "{{ watermark_text }}";
          position: fixed;
          bottom: 20px;
          right: 20px;
          opacity: 0.1;
          font-size: 12px;
          color: var(--theme-muted);
        }
        {% endif %}
        """
        
        from jinja2 import Template
        template = Template(css_template)
        return template.render(**config, **options)

# Usage example
def create_corporate_theme():
    builder = CorporateThemeBuilder()
    
    options = {
        "color_scheme": "blue",
        "logo_url": "https://company.com/logo.png",
        "logo_position": "header",
        "logo_max_width": "150px",
        "watermark_text": "Confidential",
        "chapter_numbering": True
    }
    
    theme = builder.build_theme(options)
    return theme
```

## Theme Inheritance and Composition

### Extending Existing Themes

```yaml
# academic-extended.yaml
name: "Academic Extended"
extends: "academic"  # Inherit from academic theme

# Override specific styles
overrides:
  colors:
    accent: "#d35400"  # Change accent color
  
  typography:
    heading_font: "Crimson Text, serif"  # Different heading font

# Add new CSS
additional_css: |
  .theorem {
    border-left: 4px solid var(--accent-color);
    background-color: #f8f9fa;
    padding: 1rem;
    margin: 1.5rem 0;
  }
  
  .proof::before {
    content: "Proof: ";
    font-weight: bold;
  }
  
  .proof::after {
    content: " ∎";
    float: right;
  }

# Add new templates
templates:
  theorem: |
    <div class="theorem">
      <div class="theorem-title">{{ theorem.type }} {{ theorem.number }}</div>
      <div class="theorem-content">{{ theorem.content }}</div>
    </div>
```

### Responsive Theme Development

```css
/* responsive.css */
/* Mobile-first approach */
:root {
  --base-font-size: 14px;
  --margin: 1rem;
  --max-width: 100%;
}

/* Tablet styles */
@media screen and (min-width: 768px) {
  :root {
    --base-font-size: 15px;
    --margin: 1.5rem;
    --max-width: 90%;
  }
}

/* Desktop styles */
@media screen and (min-width: 1024px) {
  :root {
    --base-font-size: 16px;
    --margin: 2rem;
    --max-width: 800px;
  }
}

/* Large desktop styles */
@media screen and (min-width: 1200px) {
  :root {
    --base-font-size: 17px;
    --margin: 2.5rem;
    --max-width: 900px;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --theme-background: #1a1a1a;
    --theme-text: #e0e0e0;
    --theme-muted: #888;
  }
  
  img {
    filter: brightness(0.8);
  }
}

/* Print styles */
@media print {
  :root {
    --base-font-size: 12pt;
    --line-height: 1.4;
  }
  
  .chapter {
    page-break-before: always;
  }
  
  .chapter-header {
    page-break-after: avoid;
  }
  
  a {
    color: inherit !important;
    text-decoration: none !important;
  }
  
  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 0.8em;
    color: #666;
  }
}
```

## Theme Testing and Validation

### Theme Test Suite

```python
import unittest
from pathlib import Path
from bookforge import BookForge
from bookforge.themes import ThemeValidator

class TestCustomTheme(unittest.TestCase):
    """Test suite for custom theme."""
    
    def setUp(self):
        self.theme_path = Path("./my-custom-theme")
        self.validator = ThemeValidator()
        self.bf = BookForge()
    
    def test_theme_structure(self):
        """Test theme has required structure."""
        required_files = [
            "theme.yaml",
            "styles/base.css",
            "templates/chapter.html"
        ]
        
        for required_file in required_files:
            file_path = self.theme_path / required_file
            self.assertTrue(
                file_path.exists(),
                f"Required file missing: {required_file}"
            )
    
    def test_theme_validation(self):
        """Test theme passes validation."""
        validation_result = self.validator.validate(self.theme_path)
        self.assertTrue(
            validation_result.is_valid,
            f"Theme validation failed: {validation_result.errors}"
        )
    
    def test_theme_rendering(self):
        """Test theme renders correctly."""
        # Create test content
        test_content = self._create_test_content()
        
        # Generate EPUB with custom theme
        epub_path = self.bf.generate_from_directory(
            input_dir=test_content,
            theme_path=self.theme_path,
            title="Theme Test Book",
            author="Test Author"
        )
        
        # Verify EPUB was created
        self.assertTrue(Path(epub_path).exists())
        
        # Validate EPUB structure
        validation_result = self.bf.validate_epub(epub_path)
        self.assertTrue(validation_result.is_valid)
    
    def test_theme_options(self):
        """Test theme options work correctly."""
        options = {
            "color_scheme": "green",
            "chapter_numbering": True,
            "watermark_text": "Test Watermark"
        }
        
        # Apply theme with options
        theme = self.bf.load_theme(self.theme_path, options)
        
        # Verify options are applied
        self.assertIn("--theme-primary: #27ae60", theme.css)
        self.assertIn("Test Watermark", theme.css)
    
    def _create_test_content(self):
        """Create test content for theme testing."""
        # Implementation to create test markdown files
        pass

if __name__ == "__main__":
    unittest.main()
```

## Publishing and Sharing Themes

### Package Theme for Distribution

```python
# setup.py for theme package
from setuptools import setup, find_packages

setup(
    name="bookforge-theme-corporate",
    version="1.0.0",
    description="Corporate Professional theme for BookForge",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    package_data={
        "bookforge_theme_corporate": [
            "theme.yaml",
            "styles/*.css",
            "templates/*.html",
            "assets/**/*"
        ]
    },
    install_requires=[
        "bookforge>=1.0.0"
    ],
    entry_points={
        "bookforge.themes": [
            "corporate-professional = bookforge_theme_corporate:CorporateTheme"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8+",
    ]
)
```

### Theme Registry

```python
# Register theme with BookForge
from bookforge.themes import register_theme

@register_theme("corporate-professional")
class CorporateTheme:
    """Corporate Professional theme."""
    
    def __init__(self):
        self.name = "corporate-professional"
        self.version = "1.0.0"
        self.path = Path(__file__).parent
    
    def load(self, options=None):
        """Load theme with options."""
        builder = CorporateThemeBuilder()
        return builder.build_theme(options or {})
```

### Theme Gallery Submission

Submit your theme to the BookForge theme gallery:

```yaml
# theme-gallery-submission.yaml
theme:
  name: "Corporate Professional"
  author: "Your Name"
  version: "1.0.0"
  description: "Professional theme for corporate documentation"
  
gallery:
  category: "Business"
  tags: ["professional", "corporate", "clean", "modern"]
  preview_images:
    - "preview-1.png"
    - "preview-2.png"
    - "preview-3.png"
  
demo:
  epub_url: "https://example.com/demo.epub"
  source_url: "https://github.com/username/bookforge-theme-corporate"
  
installation:
  method: "pip"
  command: "pip install bookforge-theme-corporate"
  
documentation:
  readme_url: "https://github.com/username/bookforge-theme-corporate/README.md"
  examples_url: "https://github.com/username/bookforge-theme-corporate/examples"
```