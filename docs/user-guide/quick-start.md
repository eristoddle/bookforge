# Quick Start Guide

Get up and running with BookForge in minutes! This guide will walk you through generating your first EPUB.

## 📦 Installation

### Option 1: Using pip (Recommended)

```bash
pip install bookforge
```

### Option 2: From Source

```bash
git clone https://github.com/bookforge/bookforge.git
cd bookforge
pip install -e .
```

### Option 3: Using Docker

```bash
docker run -p 8000:8000 bookforge/bookforge
```

## 🚀 Your First EPUB

### Method 1: Command Line (Fastest)

1. **Prepare your content** - Create a folder with markdown files:
   ```
   my-book/
   ├── 01-introduction.md
   ├── 02-chapter-one.md
   ├── 03-chapter-two.md
   └── 04-conclusion.md
   ```

2. **Generate the EPUB**:
   ```bash
   bookforge generate ./my-book \
     --title "My Amazing Book" \
     --author "Your Name" \
     --theme modern
   ```

3. **Find your EPUB** in the `generated_epubs/` directory!

### Method 2: Web Interface (Easiest)

1. **Start the web server**:
   ```bash
   bookforge serve
   ```

2. **Open your browser** to http://localhost:8000

3. **Upload your markdown files** using the drag-and-drop interface

4. **Fill in book details** and click "Generate EPUB"

5. **Download your book** when generation is complete!

### Method 3: GitHub Integration (Most Powerful)

1. **Organize your book** in a GitHub repository:
   ```
   https://github.com/yourusername/my-book/
   ├── docs/
   │   ├── 01-introduction.md
   │   ├── 02-chapter-one.md
   │   └── 03-chapter-two.md
   └── README.md
   ```

2. **Generate from command line**:
   ```bash
   bookforge github https://github.com/yourusername/my-book/tree/main/docs
   ```

3. **Or use the API**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/generate/github" \
        -H "Content-Type: application/json" \
        -d '{
          "github_url": "https://github.com/yourusername/my-book",
          "folder_path": "docs",
          "title": "My Amazing Book",
          "author": "Your Name",
          "theme": "modern"
        }'
   ```

## 🎨 Choosing a Theme

BookForge includes three beautiful themes:

- **Modern** - Clean, contemporary design perfect for technical books
- **Classic** - Traditional typography ideal for fiction and literature  
- **Minimal** - Ultra-clean layout for distraction-free reading

Preview themes:
```bash
bookforge themes
```

## 📖 Markdown Tips

### Chapter Structure
Start each chapter with an H1 heading:
```markdown
# Chapter Title

Your chapter content here...
```

### Supported Elements
- **Headers** (H1-H6)
- **Bold** and *italic* text
- Lists (ordered and unordered)
- Links and images
- Code blocks and inline code
- Tables
- Blockquotes

### Example Chapter
```markdown
# The Digital Revolution

In the early days of computing, few could have imagined the profound impact that digital technology would have on every aspect of human life.

## Key Innovations

1. **The Transistor** - Made modern computing possible
2. **The Microprocessor** - Put computers in every home
3. **The Internet** - Connected the world

> "The best way to predict the future is to invent it." — Alan Kay

### Technical Details

Here's how a simple computer program works:

```python
def hello_world():
    print("Hello, World!")

hello_world()
```

For more information, visit [our website](https://example.com).
```

## ✅ Validation and Quality

BookForge automatically validates your EPUB to ensure it works across all devices:

- **EPUB 3 compliance** - Works on all modern e-readers
- **Structure validation** - Proper file organization
- **Content validation** - Valid HTML and CSS
- **Accessibility** - Screen reader compatible

Check validation results:
```bash
bookforge generate ./my-book --validate
```

## 🔧 Next Steps

Now that you've created your first EPUB, explore these advanced features:

1. **[GitHub Integration](github-integration.md)** - Automate builds from your repositories
2. **[Custom Themes](../examples/custom-themes.md)** - Create your own styling
3. **[API Integration](../api/rest-api.md)** - Embed in your applications
4. **[CI/CD Setup](../examples/cicd-integration.md)** - Automatic publishing

## 🆘 Troubleshooting

### Common Issues

**"No markdown files found"**
- Check that your files have `.md` or `.markdown` extensions
- Ensure the directory path is correct

**"EPUB validation failed"**
- Check for malformed markdown syntax
- Ensure all links and images are valid

**"Permission denied"**
- Make sure you have write access to the output directory
- Try running with `sudo` if needed (not recommended)

### Getting Help

- Check the [full documentation](../README.md)
- Search [GitHub Issues](https://github.com/bookforge/bookforge/issues)
- Ask in [GitHub Discussions](https://github.com/bookforge/bookforge/discussions)

## 🎉 Success!

Congratulations! You've successfully generated your first EPUB with BookForge. Your book is ready to be shared with the world! 

Consider uploading to platforms like:
- Amazon Kindle Direct Publishing
- Apple Books
- Google Play Books
- Kobo Writing Life