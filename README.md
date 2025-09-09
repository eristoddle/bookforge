# BookForge 📚

**Beautiful EPUB generation service** - The cloud-based alternative to Vellum

Transform your markdown files into professional ebooks with just an API call or command-line tool.

## ✨ Features

- 🚀 **GitHub Integration** - Fetch markdown files directly from repositories
- 🎨 **Beautiful Themes** - Modern, Classic, and Minimal styling options
- ✅ **EPUB 3 Compliant** - Validated output that works everywhere
- ⚡ **Async Processing** - Handle large books without blocking
- 🌐 **RESTful API** - Easy integration with any platform
- 💻 **CLI Support** - Command-line tool for developers
- 📱 **Cross-platform** - Works on any device or platform

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/bookforge/bookforge.git
cd bookforge

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Generate Your First EPUB

#### Using the Command Line

```bash
# From a directory of markdown files
bookforge generate ./examples/sample_book --title "My Book" --author "Your Name"

# From a GitHub repository
bookforge github https://github.com/username/my-book

# Preview book structure
bookforge preview ./examples/sample_book
```

#### Using the API

```bash
# Start the server
python -m bookforge.main
# or
bookforge serve

# Generate from GitHub
curl -X POST "http://localhost:8000/api/v1/generate/github" \
     -H "Content-Type: application/json" \
     -d '{
       "github_url": "https://github.com/username/my-book",
       "title": "My Amazing Book",
       "author": "Your Name",
       "theme": "modern"
     }'

# Check status
curl "http://localhost:8000/api/v1/status/{job_id}"

# Download EPUB
curl -O "http://localhost:8000/api/v1/download/{job_id}"
```

## 🎨 Available Themes

- **Modern** - Clean, contemporary design with sans-serif fonts
- **Classic** - Traditional book styling with serif fonts  
- **Minimal** - Ultra-clean, distraction-free layout

## 📖 API Documentation

Once the server is running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key settings:
- `GITHUB_TOKEN` - For private repository access
- `REDIS_URL` - For job queue (optional)
- `DEFAULT_THEME` - Default book theme
- `EPUB_VALIDATION` - Enable/disable validation

## 📚 Use Cases

- **Documentation** - Convert GitHub wikis or docs to ebooks
- **Self-Publishing** - Professional ebook generation for authors
- **CI/CD Integration** - Automatic ebook builds on content updates
- **Educational Content** - Course materials and textbooks
- **Technical Writing** - Programming books and tutorials

## 🛠️ Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black bookforge/
isort bookforge/

# Type checking
mypy bookforge/
```

## 🔄 Comparison with Vellum

| Feature | Vellum | BookForge |
|---------|--------|-----------|
| Platform | Mac only | Cross-platform |
| Access | Desktop app | API + CLI + Web |
| Integration | Manual | GitHub, CI/CD |
| Themes | Many | Growing (extensible) |
| Formats | EPUB, Print | EPUB 3 (more coming) |
| Pricing | One-time purchase | Open source |

## 🗺️ Roadmap

### MVP (Current)
- ✅ EPUB 3 generation
- ✅ GitHub integration  
- ✅ Basic themes
- ✅ CLI tool
- ✅ REST API

### Future Releases
- 📄 DOCX and TXT input support
- 🤖 AI cover generation
- 🎨 More themes and customization
- 📖 PDF and print formats
- 🔗 Google Docs integration
- 🎯 Advanced typography options

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by [Vellum](https://vellum.pub) - the gold standard for ebook creation on Mac.

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [Markdown](https://python-markdown.github.io/) - Markdown processing
- [Click](https://click.palletsprojects.com/) - CLI framework

---

**BookForge** - Making beautiful ebooks accessible to everyone, everywhere.