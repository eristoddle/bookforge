# Command Line Interface

The BookForge CLI provides a powerful command-line interface for generating EPUBs. It's perfect for developers, automation scripts, and CI/CD pipelines.

## 📦 Installation

```bash
pip install bookforge
```

## 🚀 Basic Usage

```bash
bookforge [OPTIONS] COMMAND [ARGS]...
```

## 📋 Commands Overview

| Command | Description |
|---------|-------------|
| `generate` | Generate EPUB from local files |
| `github` | Generate EPUB from GitHub repository |
| `preview` | Preview book structure without generating |
| `themes` | List available themes |
| `serve` | Start the API server |

## 📖 Command Reference

### generate

Generate EPUB from markdown files in a directory or single file.

```bash
bookforge generate SOURCE [OPTIONS]
```

**Arguments:**
- `SOURCE`: Path to directory with markdown files, single markdown file, or GitHub URL

**Options:**
- `--title, -t TEXT`: Book title
- `--author, -a TEXT`: Book author  
- `--theme, -T [modern|classic|minimal]`: Book theme (default: modern)
- `--language, -l TEXT`: Book language code (default: en)
- `--description, -d TEXT`: Book description
- `--publisher, -p TEXT`: Publisher name
- `--output, -o PATH`: Output EPUB file path
- `--validate/--no-validate`: Validate generated EPUB (default: validate)

**Examples:**

```bash
# Generate from directory
bookforge generate ./my-book --title "My Book" --author "John Doe"

# Generate from single file
bookforge generate chapter1.md --title "Chapter One" --author "Jane Smith"

# Specify output location
bookforge generate ./docs --title "Documentation" --output ./build/docs.epub

# Use different theme
bookforge generate ./novel --title "My Novel" --theme classic

# Skip validation (faster)
bookforge generate ./quick-test --title "Test" --no-validate
```

### github

Generate EPUB from GitHub repository.

```bash
bookforge github GITHUB_URL [OPTIONS]
```

**Arguments:**
- `GITHUB_URL`: GitHub repository URL

**Options:**
- `--folder, -f TEXT`: Specific folder path in repository
- `--title, -t TEXT`: Book title (auto-detected if not provided)
- `--author, -a TEXT`: Author name (auto-detected if not provided)
- `--theme, -T [modern|classic|minimal]`: Book theme (default: modern)
- `--output, -o PATH`: Output EPUB file path

**Examples:**

```bash
# Generate from entire repository
bookforge github https://github.com/username/my-book

# Generate from specific folder
bookforge github https://github.com/username/docs --folder documentation

# Override auto-detected metadata
bookforge github https://github.com/username/book \
  --title "Custom Title" \
  --author "Custom Author"

# Save to specific location
bookforge github https://github.com/username/book --output ./books/
```

### preview

Preview book structure without generating EPUB. Shows chapter organization, word counts, and estimated page counts.

```bash
bookforge preview SOURCE
```

**Arguments:**
- `SOURCE`: Path to directory with markdown files or single file

**Example:**

```bash
bookforge preview ./my-book
```

**Output:**
```
📚 BookForge Preview
🔍 Analyzing: ./my-book

📖 Book Structure Preview
==================================================
📄 Total chapters: 3
📝 Total words: 2,150
📚 Estimated pages: 8

📋 Chapter Breakdown:
==================================================
 1. Introduction
     📄 450 words
     📁 01_introduction.xhtml

 2. Main Content
     📄 1,200 words
     📁 02_main.xhtml

 3. Conclusion
     📄 500 words
     📁 03_conclusion.xhtml
```

### themes

List available themes with descriptions.

```bash
bookforge themes
```

**Output:**
```
🎨 Available Themes:
==============================
📖 Modern
   Clean, contemporary design with sans-serif fonts

📖 Classic
   Traditional book styling with serif fonts

📖 Minimal
   Ultra-clean, distraction-free layout
```

### serve

Start the BookForge API server.

```bash
bookforge serve [OPTIONS]
```

**Options:**
- `--port, -p INTEGER`: Port to run server on (default: 8000)
- `--host, -h TEXT`: Host to bind server to (default: 127.0.0.1)

**Example:**

```bash
# Start on default port
bookforge serve

# Start on custom port
bookforge serve --port 9000

# Bind to all interfaces
bookforge serve --host 0.0.0.0 --port 8080
```

## 🎯 Advanced Usage

### Batch Processing

Process multiple books in a script:

```bash
#!/bin/bash

# Generate multiple books
for dir in books/*/; do
  book_name=$(basename "$dir")
  echo "Processing $book_name..."
  
  bookforge generate "$dir" \
    --title "$book_name" \
    --author "Your Name" \
    --output "output/${book_name}.epub"
done
```

### CI/CD Integration

Use in GitHub Actions:

```yaml
name: Generate EPUB
on:
  push:
    paths: ['docs/**']

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install BookForge
        run: pip install bookforge
      
      - name: Generate EPUB
        run: |
          bookforge generate docs/ \
            --title "Project Documentation" \
            --author "Team" \
            --output documentation.epub
      
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: epub
          path: documentation.epub
```

### Makefile Integration

Add to your project's Makefile:

```makefile
.PHONY: epub clean-epub

epub:
	bookforge generate docs/ \
		--title "$(PROJECT_NAME)" \
		--author "$(AUTHOR)" \
		--output "$(PROJECT_NAME).epub"

clean-epub:
	rm -f *.epub

book: epub
	@echo "📚 EPUB generated: $(PROJECT_NAME).epub"
```

## 🔧 Configuration

### Environment Variables

Set defaults using environment variables:

```bash
export BOOKFORGE_THEME=classic
export BOOKFORGE_AUTHOR="Your Name"
export BOOKFORGE_PUBLISHER="Your Publisher"

# Now these will be used as defaults
bookforge generate ./my-book --title "My Book"
```

### Config File

Create a `.bookforge.yml` config file in your project:

```yaml
# .bookforge.yml
title: "My Project Documentation"
author: "Development Team"
theme: modern
language: en
publisher: "ACME Corp"
description: "Comprehensive project documentation"

# GitHub settings
github:
  folder: docs
  auto_detect: true

# Output settings
output:
  directory: ./build
  filename_template: "{title}_{version}.epub"
  validate: true
```

Use with:
```bash
bookforge generate . --config .bookforge.yml
```

## 📊 Output and Logging

### Verbose Output

Get detailed information during generation:

```bash
bookforge generate ./my-book --verbose
```

### Quiet Mode

Suppress all output except errors:

```bash
bookforge generate ./my-book --quiet
```

### JSON Output

Get machine-readable output:

```bash
bookforge generate ./my-book --format json
```

Output:
```json
{
  "status": "success",
  "output_path": "generated_epubs/My_Book_abc123.epub",
  "file_size": 1048576,
  "chapters": 5,
  "word_count": 25000,
  "validation": {
    "valid": true,
    "errors": 0,
    "warnings": 1
  }
}
```

## 🐛 Troubleshooting

### Common Issues

**Command not found**
```bash
# Add to PATH or use full path
python -m bookforge.cli generate ./my-book
```

**Permission denied**
```bash
# Check file permissions
chmod +x bookforge
# Or use different output directory
bookforge generate ./my-book --output ~/Books/
```

**Invalid markdown**
```bash
# Check markdown syntax
bookforge preview ./my-book  # Shows structure without generating
```

**GitHub access issues**
```bash
# Set GitHub token for private repos
export GITHUB_TOKEN=your_token_here
bookforge github https://github.com/private/repo
```

### Debug Mode

Enable debug output:

```bash
export BOOKFORGE_DEBUG=1
bookforge generate ./my-book
```

### Getting Help

```bash
# General help
bookforge --help

# Command-specific help
bookforge generate --help
bookforge github --help

# Version information
bookforge --version
```

## 💡 Tips and Best Practices

1. **File Organization**: Use numbered prefixes for chapter ordering (`01_intro.md`, `02_chapter1.md`)

2. **Validation**: Always validate EPUBs before publishing (`--validate`)

3. **Preview First**: Use `preview` to check structure before generating

4. **Automation**: Create scripts for repeated tasks

5. **Version Control**: Keep your markdown in git for collaboration

6. **Testing**: Test EPUBs on multiple devices/readers

7. **Themes**: Choose themes that match your content type (technical docs → modern, fiction → classic)