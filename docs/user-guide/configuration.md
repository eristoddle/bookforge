# Configuration Guide

## Configuration File

BookForge uses a `bookforge.yaml` configuration file in your project directory.

## Basic Configuration

Create a `bookforge.yaml` file in your project root:

```yaml
# Book Metadata
book:
  title: "My Amazing Book"
  author: "Your Name"
  language: "en"
  publisher: "Your Publisher"
  isbn: "978-0-123456-78-9"
  cover: "assets/cover.jpg"

# Output Settings
output:
  format: "epub3"
  filename: "my-book.epub"
  destination: "./dist"

# Source Settings
source:
  input_dir: "./content"
  markdown_extensions:
    - tables
    - codehilite
    - toc

# Styling
theme:
  name: "default"
  custom_css: "assets/styles.css"
  fonts:
    body: "Georgia, serif"
    heading: "Arial, sans-serif"
```

## Advanced Configuration

### Custom Themes

```yaml
theme:
  name: "custom"
  base_theme: "academic"
  overrides:
    primary_color: "#2c3e50"
    secondary_color: "#3498db"
    font_size: "16px"
    line_height: "1.6"
```

### Processing Options

```yaml
processing:
  validate_epub: true
  optimize_images: true
  image_quality: 85
  max_image_width: 800
  generate_toc: true
  toc_depth: 3
```

### GitHub Integration

```yaml
github:
  repository: "username/book-repo"
  branch: "main"
  path: "docs/"
  webhook_secret: "your-webhook-secret"
```

## Environment Variables

Override configuration with environment variables:

```bash
export BOOKFORGE_TITLE="My Book"
export BOOKFORGE_AUTHOR="Author Name"
export BOOKFORGE_OUTPUT_DIR="./output"
```

## Global Configuration

User-wide settings in `~/.bookforge/config.yaml`:

```yaml
defaults:
  author: "Your Default Author"
  publisher: "Your Publisher"
  theme: "professional"

api:
  base_url: "https://api.bookforge.io"
  timeout: 30

cache:
  enabled: true
  ttl: 3600
```