# 📚 BookForge

**Beautiful EPUB generation service**

Transform your markdown files into professional ebooks with just a few clicks, API calls, or command-line commands. BookForge makes professional ebook creation accessible to everyone, everywhere.

![BookForge Hero](https://img.shields.io/badge/BookForge-EPUB%20Generator-blue?style=for-the-badge&logo=book)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![EPUB 3](https://img.shields.io/badge/EPUB-3.0-orange.svg)](https://www.w3.org/publishing/epub3/)

---

## ✨ Features

### 🌐 **Three Ways to Create EPUBs**
- **📱 Web Interface** - Drag & drop files, fill forms, download EPUBs
- **💻 Command Line** - Perfect for developers and automation
- **🔌 REST API** - Integrate with any application or service

### 🎨 **Beautiful Themes**
- **Modern** - Clean, contemporary design for technical content
- **Classic** - Traditional book styling for literature and formal works
- **Minimal** - Ultra-clean layout for distraction-free reading

### 🚀 **Professional Features**
- ✅ **EPUB 3 Compliant** - Works on all major e-readers and platforms
- 🌐 **GitHub Integration** - Generate directly from your repositories
- ⚡ **Async Processing** - Handle large books without blocking
- 🔍 **Built-in Validation** - Ensure your EPUBs meet quality standards
- 📊 **Real-time Progress** - Watch your book generation live
- 🌍 **Cross-platform** - Works on any operating system

---

## 🚀 Quick Start

### Option 1: Web Interface (Easiest)

```bash
# Install and start the server
pip install -r requirements.txt
python -m bookforge.main

# Open your browser
open http://localhost:8000
```

Then simply drag your markdown files onto the interface and click "Generate EPUB"!

### Option 2: Command Line (Fastest)

```bash
# Install BookForge
pip install -r requirements.txt

# Generate from local files
python -m bookforge.cli generate ./my-book \
  --title "My Amazing Book" \
  --author "Your Name" \
  --theme modern

# Generate from GitHub
python -m bookforge.cli github https://github.com/username/my-book
```

### Option 3: REST API (Most Powerful)

```bash
# Start the API server
python -m bookforge.main

# Generate via API
curl -X POST "http://localhost:8000/api/v1/generate/github" \
     -H "Content-Type: application/json" \
     -d '{
       "github_url": "https://github.com/username/my-book",
       "title": "My Amazing Book",
       "author": "Your Name",
       "theme": "modern"
     }'
```

---

## 🎯 Use Cases

| Use Case | Best Method | Example |
|----------|-------------|---------|
| **📚 Self-Publishing** | Web Interface | Upload manuscript chapters → Choose classic theme → Download EPUB |
| **📖 Documentation** | GitHub Integration | Point to docs folder → Auto-generate → Distribute to team |
| **🎓 Educational Content** | Command Line | Batch process course materials → Multiple formats |
| **🏢 Corporate Publishing** | REST API | Integrate with CMS → Automated ebook generation |
| **🤖 CI/CD Automation** | API + GitHub Actions | Code docs → Auto-publish → Deploy to platforms |

---

## 🌟 Why Choose BookForge?

### 🆚 **BookForge vs. Vellum**

| Feature | Vellum | BookForge |
|---------|--------|-----------|
| **Platform** | Mac only | Cross-platform (Web, CLI, API) |
| **Access** | Desktop app | Browser, command line, API |
| **Integration** | Manual import | GitHub, CI/CD, automated |
| **Collaboration** | Single user | Team-friendly, version control |
| **Cost** | $250+ | Free, open source |
| **Deployment** | Desktop only | Self-hosted, cloud, SaaS |
| **Automation** | Manual process | Full automation support |
| **Extensibility** | Fixed features | Plugin system, customizable |

### 🎨 **Professional Quality Output**
- **Standards Compliant** - EPUB 3.0 with proper validation
- **Cross-Reader Support** - Works on Kindle, Apple Books, Kobo, Adobe Digital Editions
- **Responsive Design** - Adapts to different screen sizes and orientations
- **Accessibility** - Screen reader compatible with proper navigation
- **Professional Typography** - Carefully designed themes with proper spacing and fonts

---

## 📱 Web Interface

### **Drag & Drop Simplicity**
1. **Upload Files** - Drag markdown files onto the upload area
2. **Fill Details** - Enter title, author, and description
3. **Choose Theme** - Preview and select your preferred styling
4. **Generate** - Watch real-time progress as your EPUB is created
5. **Download** - Get your professional EPUB instantly

### **GitHub Integration**
- Enter any GitHub repository URL
- Specify folder paths for organized content
- Auto-detect book metadata from repository info
- Support for private repositories (with token)

### **Live Features**
- **Real-time Progress** - See generation status updates live
- **Validation Results** - Instant feedback on EPUB quality
- **Theme Previews** - See exactly how your book will look
- **Job History** - Track and re-download previous generations

---

## 💻 Command Line Interface

### **Basic Usage**
```bash
# Generate from directory
bookforge generate ./my-book --title "My Book" --author "Me"

# Preview before generating
bookforge preview ./my-book

# List available themes
bookforge themes

# Generate from GitHub
bookforge github https://github.com/user/repo --theme classic

# Start web server
bookforge serve --port 8080
```

### **Advanced Examples**
```bash
# Custom output location
bookforge generate ./docs --output ~/Books/documentation.epub

# Different language and publisher
bookforge generate ./novel \
  --title "Mon Livre" \
  --language fr \
  --publisher "Maison d'Édition"

# Skip validation for faster generation
bookforge generate ./quick-test --no-validate
```

---

## 🔌 REST API

### **Core Endpoints**
- `POST /api/v1/generate/github` - Generate from GitHub repository
- `POST /api/v1/generate/files` - Generate from uploaded files
- `GET /api/v1/status/{job_id}` - Check generation progress
- `GET /api/v1/download/{job_id}` - Download completed EPUB
- `GET /api/v1/jobs` - List recent jobs

### **Python Client Example**
```python
import requests

# Start generation
response = requests.post("http://localhost:8000/api/v1/generate/github", json={
    "github_url": "https://github.com/username/my-book",
    "title": "My Book",
    "author": "Author Name",
    "theme": "modern"
})

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/v1/status/{job_id}")
print(status.json())

# Download when complete
if status.json()["status"] == "completed":
    epub = requests.get(f"http://localhost:8000/api/v1/download/{job_id}")
    with open("my-book.epub", "wb") as f:
        f.write(epub.content)
```

---

## 🎨 Themes & Styling

### **Modern Theme**
- **Best for**: Technical documentation, business books, modern fiction
- **Typography**: Sans-serif fonts (System UI, Segoe UI, Roboto)
- **Layout**: Clean, spacious with clear hierarchy
- **Colors**: Blue accents with high contrast

### **Classic Theme**
- **Best for**: Literature, academic works, formal publications
- **Typography**: Serif fonts (Times New Roman, Georgia)
- **Layout**: Traditional book formatting with centered titles
- **Style**: Elegant, time-tested design patterns

### **Minimal Theme**
- **Best for**: Essays, contemplative works, focused reading
- **Typography**: Premium serif fonts (Charter, Georgia)
- **Layout**: Ultra-clean with generous whitespace
- **Philosophy**: Distraction-free, content-focused

---

## 🛠️ Installation & Setup

### **Requirements**
- Python 3.9 or higher
- 1GB RAM minimum (2GB recommended)
- 500MB disk space for application
- Additional space for generated EPUBs

### **Installation**
```bash
# Clone repository
git clone https://github.com/bookforge/bookforge.git
cd bookforge

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

### **Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
vim .env
```

### **Key Settings**
```bash
# Basic settings
DEBUG=false
DEFAULT_THEME=modern
EPUB_VALIDATION=true

# GitHub integration
GITHUB_TOKEN=your_token_here

# File storage
TEMP_DIR=./temp_books
OUTPUT_DIR=./generated_epubs
MAX_FILE_SIZE=50MB

# API settings
HOST=0.0.0.0
PORT=8000
MAX_CONCURRENT_JOBS=10
```

---

## 🐳 Docker Deployment

### **Quick Start**
```bash
# Run with Docker
docker run -p 8000:8000 bookforge/bookforge:latest

# Or with Docker Compose
curl -o docker-compose.yml https://raw.githubusercontent.com/bookforge/bookforge/main/docker-compose.yml
docker-compose up -d
```

### **Production Deployment**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  bookforge:
    image: bookforge/bookforge:latest
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - EPUB_VALIDATION=true
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - bookforge
```

---

## 🤖 CI/CD Integration

### **GitHub Actions**
```yaml
name: Generate Documentation EPUB
on:
  push:
    paths: ['docs/**']

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
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
      uses: actions/upload-artifact@v3
      with:
        name: documentation
        path: documentation.epub
```

### **Jenkins Pipeline**
```groovy
pipeline {
    agent any
    stages {
        stage('Generate EPUB') {
            steps {
                sh '''
                    pip install bookforge
                    bookforge generate docs/ \
                        --title "${JOB_NAME} Documentation" \
                        --author "DevOps Team" \
                        --output "${JOB_NAME}-docs.epub"
                '''
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: '*.epub'
            }
        }
    }
}
```

---

## 📚 Documentation

### **User Guides**
- [📖 Quick Start Guide](docs/user-guide/quick-start.md) - Get up and running in minutes
- [💻 Command Line Interface](docs/user-guide/cli.md) - Complete CLI reference
- [🌐 Web Interface Guide](docs/user-guide/web-interface.md) - Using the visual interface

### **API Documentation**
- [🔌 REST API Reference](docs/api/rest-api.md) - Complete API documentation
- [📋 Interactive API Docs](http://localhost:8000/docs) - Swagger UI (when server is running)

### **Examples & Tutorials**
- [💡 Basic Usage Examples](docs/examples/basic-usage.md) - Real-world scenarios
- [🚀 CI/CD Integration](docs/examples/cicd-integration.md) - Automation examples

### **Developer Resources**
- [🏗️ Architecture Overview](docs/developer/architecture.md) - System design
- [🚀 Deployment Guide](docs/developer/deployment.md) - Production setup
- [🤝 Contributing Guide](docs/developer/contributing.md) - How to contribute

---

## 🔧 Development

### **Local Development**
```bash
# Clone and setup
git clone https://github.com/bookforge/bookforge.git
cd bookforge
pip install -e ".[dev]"

# Run tests
pytest

# Start development server
python -m bookforge.main

# Format code
black bookforge/
isort bookforge/

# Type checking
mypy bookforge/
```

### **Project Structure**
```
bookforge/
├── api/              # FastAPI endpoints
├── core/             # Core business logic
│   ├── epub_generator.py    # EPUB generation engine
│   ├── markdown_processor.py # Markdown to HTML conversion
│   ├── github_integration.py # GitHub API integration
│   └── validator.py         # EPUB validation
├── static/           # Web interface assets
├── templates/        # EPUB and web templates
├── cli.py           # Command line interface
└── main.py          # FastAPI application

docs/                # Documentation
examples/            # Sample content
tests/               # Test suite
```

---

## 🌟 Examples

### **Technical Documentation**
```bash
# Project with organized docs
project-docs/
├── 01-introduction.md
├── 02-getting-started.md
├── 03-api-reference.md
└── 04-troubleshooting.md

bookforge generate ./project-docs \
  --title "Project Documentation" \
  --author "Development Team" \
  --theme modern
```

### **Fiction Novel**
```bash
# Novel manuscript
my-novel/
├── 00-prologue.md
├── 01-chapter-one.md
├── 02-chapter-two.md
└── 21-epilogue.md

bookforge generate ./my-novel \
  --title "The Digital Odyssey" \
  --author "Jane Author" \
  --theme classic
```

### **Corporate Handbook**
```bash
# Company policies
handbook/
├── 01-welcome.md
├── 02-policies.md
├── 03-benefits.md
└── 04-procedures.md

bookforge generate ./handbook \
  --title "Employee Handbook" \
  --author "HR Department" \
  --publisher "ACME Corporation" \
  --theme classic
```

---

## 🆘 Support & Community

### **Getting Help**
- 📖 **Documentation** - Comprehensive guides and tutorials
- 🐛 **GitHub Issues** - Bug reports and feature requests
- 💬 **GitHub Discussions** - Community support and ideas
- 📧 **Email Support** - Direct help for complex issues

### **Contributing**
We welcome contributions! See our [Contributing Guide](docs/developer/contributing.md) for details.

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🌟 Star the repository

### **Community**
- **GitHub** - Source code and issue tracking
- **Discord** - Real-time chat and support
- **Twitter** - Updates and announcements
- **Blog** - Tutorials and best practices

---

## 📄 License

BookForge is open source software licensed under the [MIT License](LICENSE).

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

BookForge is inspired by [Vellum](https://vellum.pub) - the gold standard for ebook creation on Mac. We're grateful to the open source community and the following projects:

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern web framework
- **[Jinja2](https://jinja.palletsprojects.com/)** - Template engine
- **[Markdown](https://python-markdown.github.io/)** - Markdown processing
- **[Click](https://click.palletsprojects.com/)** - CLI framework
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** - HTML parsing

---

## 🚀 What's Next?

### **Roadmap**
- 📄 **Multiple Input Formats** - DOCX, TXT, Google Docs support
- 🤖 **AI Cover Generation** - Automatic cover creation based on content
- 🎨 **Custom Themes** - Theme editor and marketplace
- 📖 **More Output Formats** - PDF, MOBI, print-ready files
- 🔗 **Enhanced Integrations** - Notion, Confluence, GitBook
- 🌍 **Internationalization** - Multi-language interface support

### **Enterprise Features** (Coming Soon)
- 👥 **Team Management** - User accounts and permissions
- 📊 **Analytics Dashboard** - Usage statistics and insights
- 🔒 **SSO Integration** - Enterprise authentication
- ☁️ **Cloud Storage** - S3, Google Drive, Dropbox integration
- 🎯 **White Label** - Custom branding and deployment

---

<div align="center">

**📚 Transform your markdown into beautiful ebooks**

[🌐 Try Web Interface](http://localhost:8000) • [📖 Read Docs](docs/) • [🐛 Report Issues](https://github.com/bookforge/bookforge/issues) • [💬 Join Discussion](https://github.com/bookforge/bookforge/discussions)

**Made with ❤️ by the BookForge team**

</div>