# Release Management Guide

This guide covers the complete release process for BookForge, including automated version management, publishing, and deployment.

## Quick Release

For most releases, use the automated script:

```bash
# Release a new version
python release.py 0.1.1

# Test the release process without publishing
python release.py 0.1.1 --dry-run

# Publish to Test PyPI first
python release.py 0.1.1 --test-pypi
```

## Automated Release Script

The `release.py` script automates the entire release workflow:

### What it does:
1. ✅ **Version Validation** - Ensures semantic versioning format
2. ✅ **Git Status Check** - Verifies clean working directory
3. ✅ **Version Updates** - Updates version in all relevant files
4. ✅ **Git Operations** - Commits changes and creates release tag
5. ✅ **Package Building** - Creates source and wheel distributions
6. ✅ **Quality Checks** - Runs twine check for package validation
7. ✅ **PyPI Publishing** - Uploads to PyPI or Test PyPI
8. ✅ **GitHub Push** - Pushes commits and tags to remote

### Usage Examples:

```bash
# Standard release
python release.py 0.1.1

# Test release process (no changes made)
python release.py 0.1.1 --dry-run

# Upload to Test PyPI for testing
python release.py 0.1.1 --test-pypi

# Pre-release versions
python release.py 0.1.1-beta.1
python release.py 0.1.1-rc.1
```

## Prerequisites

### 1. Install Required Tools

```bash
# Install build and publishing tools
pip install build twine

# Ensure you have git configured
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. PyPI Configuration

Create `~/.pypirc` for PyPI authentication:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

**Security Note**: Use API tokens instead of passwords. Generate tokens at:
- PyPI: https://pypi.org/manage/account/token/
- Test PyPI: https://test.pypi.org/manage/account/token/

### 3. GitHub Setup

Ensure your repository is connected to GitHub:

```bash
# Check remote
git remote -v

# Add remote if needed
git remote add origin https://github.com/yourusername/bookforge.git
```

## Manual Release Process

If you need to release manually or understand the steps:

### 1. Prepare the Release

```bash
# Ensure clean working directory
git status

# Update version numbers manually
# Edit: pyproject.toml, bookforge/__init__.py
```

### 2. Create Release Commit

```bash
# Add and commit version changes
git add pyproject.toml bookforge/__init__.py
git commit -m "Release version 0.1.1"

# Create release tag
git tag -a v0.1.1 -m "Version 0.1.1"
```

### 3. Build Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build distributions
python -m build

# Check package
python -m twine check dist/*
```

### 4. Publish

```bash
# Upload to Test PyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install -i https://test.pypi.org/simple/ bookforge

# Upload to PyPI
python -m twine upload dist/*
```

### 5. Push to GitHub

```bash
# Push commits and tags
git push
git push --tags
```

## Version Management

### Version Files

The following files contain version information:
- `pyproject.toml` - Main package version
- `bookforge/__init__.py` - Python module version

### Semantic Versioning

Follow semantic versioning (semver.org):
- `MAJOR.MINOR.PATCH` (e.g., 1.0.0)
- `MAJOR.MINOR.PATCH-PRERELEASE` (e.g., 1.0.0-beta.1)

Examples:
- `0.1.1` - Patch release (bug fixes)
- `0.2.0` - Minor release (new features, backward compatible)
- `1.0.0` - Major release (breaking changes)
- `1.0.0-beta.1` - Pre-release

## Release Checklist

### Before Release
- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated (if you have one)
- [ ] Version numbers are correct
- [ ] Git working directory is clean

### Testing
- [ ] Test on Test PyPI first
- [ ] Verify installation works
- [ ] Test CLI commands
- [ ] Check package contents

### After Release
- [ ] Verify package on PyPI
- [ ] Test installation: `pip install bookforge`
- [ ] Update documentation if needed
- [ ] Announce release (if applicable)

## Troubleshooting

### Common Issues

**"Package already exists"**
```bash
# Version already published - increment version number
python release.py 0.1.2
```

**"Git working directory not clean"**
```bash
# Commit or stash changes first
git add .
git commit -m "Prepare for release"
```

**"Authentication failed"**
```bash
# Check PyPI credentials in ~/.pypirc
# Regenerate API tokens if needed
```

**"Package check failed"**
```bash
# Fix package issues first
python -m twine check dist/*
```

### Recovery from Failed Release

If a release fails partway through:

```bash
# Reset to previous state
git reset --hard HEAD~1  # Remove release commit
git tag -d v0.1.1        # Remove release tag

# Clean build artifacts
rm -rf build/ dist/ *.egg-info/

# Fix issues and try again
python release.py 0.1.1
```

## Automation with GitHub Actions

For fully automated releases, consider adding GitHub Actions:

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Best Practices

1. **Always test first** - Use Test PyPI before production
2. **Use semantic versioning** - Follow semver standards
3. **Keep releases small** - Frequent, incremental releases
4. **Document changes** - Maintain a changelog
5. **Test thoroughly** - Verify functionality before release
6. **Backup tokens** - Store API tokens securely

## Emergency Procedures

### Yanking a Bad Release

If you need to remove a problematic release:

```bash
# Yank release from PyPI (makes it unavailable for new installs)
twine upload --repository pypi --skip-existing dist/*
# Then use PyPI web interface to yank the version
```

### Hotfix Release

For critical bug fixes:

```bash
# Create hotfix branch from tag
git checkout -b hotfix/0.1.2 v0.1.1

# Fix the issue
# ... make changes ...

# Release hotfix
python release.py 0.1.2

# Merge back to main
git checkout main
git merge hotfix/0.1.2
git branch -d hotfix/0.1.2
```