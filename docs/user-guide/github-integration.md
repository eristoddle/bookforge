# GitHub Integration

## Overview

BookForge seamlessly integrates with GitHub repositories to automatically generate EPUBs from your markdown content.

## Setup GitHub Integration

### 1. Repository Structure

Organize your repository for optimal EPUB generation:

```
my-book/
├── bookforge.yaml          # Configuration file
├── README.md              # Repository description
├── content/               # Book content
│   ├── 01-introduction.md
│   ├── 02-chapter-one.md
│   └── 03-chapter-two.md
├── assets/                # Images and resources
│   ├── cover.jpg
│   └── images/
└── .github/
    └── workflows/
        └── publish.yml    # GitHub Actions workflow
```

### 2. Configuration for GitHub

Update your `bookforge.yaml`:

```yaml
book:
  title: "My GitHub Book"
  author: "GitHub User"

source:
  input_dir: "./content"
  include_patterns:
    - "*.md"
  exclude_patterns:
    - "README.md"
    - "CHANGELOG.md"

github:
  auto_publish: true
  release_on_tag: true
  artifact_name: "book.epub"
```

## GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish Book

on:
  push:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install BookForge
      run: |
        pip install bookforge
    
    - name: Generate EPUB
      run: |
        bookforge generate ./content --output ./dist/book.epub
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: book-epub
        path: ./dist/book.epub
    
    - name: Release
      if: github.event_name == 'release'
      uses: softprops/action-gh-release@v1
      with:
        files: ./dist/book.epub
```

## Command Line GitHub Integration

### Generate from GitHub Repository

```bash
# Generate from public repository
bookforge github https://github.com/username/my-book

# Generate from private repository (requires token)
bookforge github https://github.com/username/private-book --token $GITHUB_TOKEN

# Generate from specific branch
bookforge github https://github.com/username/my-book --branch develop

# Generate from subdirectory
bookforge github https://github.com/username/mono-repo --path docs/book
```

### Authentication

Set up GitHub authentication:

```bash
# Using personal access token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Using GitHub CLI
gh auth login
bookforge github --use-gh-auth https://github.com/username/my-book
```

## Webhook Integration

### Setting up Webhooks

1. Go to your repository settings
2. Navigate to "Webhooks"
3. Add webhook with:
   - Payload URL: `https://your-bookforge-instance.com/webhooks/github`
   - Content type: `application/json`
   - Secret: Your webhook secret
   - Events: Push, Release

### Webhook Configuration

```yaml
webhooks:
  github:
    secret: "your-webhook-secret"
    auto_generate: true
    branches:
      - main
      - release
    events:
      - push
      - release
```

## Best Practices

### 1. Content Organization

- Use numbered prefixes for chapter ordering: `01-intro.md`, `02-chapter1.md`
- Keep images in an `assets/` or `images/` directory
- Use relative paths for image references

### 2. Automated Publishing

- Tag releases for stable versions
- Use semantic versioning: `v1.0.0`, `v1.1.0`
- Include release notes in GitHub releases

### 3. Collaboration

- Use pull requests for content review
- Set up branch protection rules
- Use GitHub Issues for tracking book improvements