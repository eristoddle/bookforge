# Installation Guide

## System Requirements

- Python 3.8 or higher
- pip package manager
- 1GB free disk space
- Internet connection for package downloads

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install bookforge
```

### Method 2: Install from Source

```bash
git clone https://github.com/username/bookforge.git
cd bookforge
pip install -e .
```

### Method 3: Using Docker

```bash
docker pull bookforge/bookforge:latest
docker run -p 8000:8000 bookforge/bookforge:latest
```

## Verify Installation

```bash
bookforge --version
```

## Platform-Specific Instructions

### Windows
1. Install Python from python.org
2. Open Command Prompt as Administrator
3. Run the installation command

### macOS
1. Install Python using Homebrew: `brew install python`
2. Install BookForge: `pip install bookforge`

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install bookforge
```

## Troubleshooting

### Common Issues

**Permission Error on macOS/Linux:**
```bash
pip install --user bookforge
```

**Python Version Issues:**
Ensure you're using Python 3.8+:
```bash
python --version
```

**Package Dependencies:**
If you encounter dependency conflicts:
```bash
pip install bookforge --force-reinstall
```