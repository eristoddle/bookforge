# BookForge Documentation

Welcome to the BookForge documentation! BookForge is a cloud-based EPUB generation service that transforms your markdown files into beautiful, professional ebooks.

## 📚 Table of Contents

### Getting Started
- [Quick Start Guide](user-guide/quick-start.md)
- [Installation](user-guide/installation.md)
- [Configuration](user-guide/configuration.md)

### User Guides
- [Command Line Interface](user-guide/cli.md)
- [Web Interface](user-guide/web-interface.md)
- [GitHub Integration](user-guide/github-integration.md)
- [Themes and Styling](user-guide/themes.md)

### API Documentation
- [REST API Reference](api/rest-api.md)
- [Python API](api/python-api.md)
- [Authentication](api/authentication.md)

### Developer Documentation
- [Architecture Overview](developer/architecture.md)
- [Contributing Guide](developer/contributing.md)
- [Plugin Development](developer/plugins.md)
- [Deployment](developer/deployment.md)

### Examples
- [Basic Usage Examples](examples/basic-usage.md)
- [Advanced Use Cases](examples/advanced-usage.md)
- [CI/CD Integration](examples/cicd-integration.md)
- [Custom Themes](examples/custom-themes.md)

## 🚀 Quick Start

### Generate Your First EPUB

```bash
# Install BookForge
pip install bookforge

# Generate from markdown files
bookforge generate ./my-book --title "My Amazing Book" --author "Your Name"

# Or from GitHub
bookforge github https://github.com/username/my-book

# Start the web interface
bookforge serve
```

Visit http://localhost:8000 for the web interface or http://localhost:8000/docs for the API documentation.

## 🎨 Key Features

- **📖 EPUB 3 Generation** - Standards-compliant ebooks that work everywhere
- **🌐 GitHub Integration** - Generate directly from your repositories
- **🎨 Beautiful Themes** - Professional styling with minimal configuration
- **🚀 REST API** - Integrate with any platform or service
- **💻 CLI Tool** - Perfect for developers and automation
- **🌍 Web Interface** - User-friendly drag-and-drop interface
- **✅ Validation** - Built-in EPUB validation ensures quality output

## 🆚 BookForge vs. Vellum

| Feature | Vellum | BookForge |
|---------|--------|-----------|
| **Platform** | Mac only | Cross-platform (Web, CLI, API) |
| **Integration** | Manual import | GitHub, CI/CD, API |
| **Collaboration** | Single user | Team-friendly, version control |
| **Deployment** | Desktop app | Cloud service, self-hostable |
| **Automation** | Manual | Full automation support |
| **Extensibility** | Fixed features | Plugin system, open source |
| **Cost** | One-time purchase | Free, open source |

## 📖 Use Cases

- **📚 Self-Publishing** - Authors creating professional ebooks
- **📖 Documentation** - Converting technical docs to ebooks
- **🎓 Education** - Course materials and textbooks
- **🏢 Enterprise** - Internal documentation and training materials
- **🤖 Automation** - CI/CD pipelines for content publishing

## 🛠️ Support & Community

- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Community support and ideas
- **Documentation** - Comprehensive guides and examples
- **Examples** - Real-world usage patterns

## 📄 License

BookForge is open source software licensed under the MIT License.