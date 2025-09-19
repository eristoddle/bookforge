# Quick Release Guide

## TL;DR - Release a New Version

```bash
# 1. Test the release process
python release.py 0.1.1 --dry-run

# 2. Release to Test PyPI
python release.py 0.1.1 --test-pypi

# 3. Test installation
pip install -i https://test.pypi.org/simple/ bookforge

# 4. Release to PyPI
python release.py 0.1.1
```

Or using Make:

```bash
# Test, then release
make release-dry-run version=0.1.1
make release-test version=0.1.1  
make release version=0.1.1
```

## What You Need (One-time Setup)

1. **PyPI Account & API Tokens**
   - Follow: `docs/PYPI_SETUP.md`

2. **Git Repository**
   - Ensure remote is set up: `git remote -v`

3. **Clean Working Directory**
   - Commit all changes before releasing

## Version Numbers

Use [Semantic Versioning](https://semver.org/):
- `0.1.1` - Bug fixes
- `0.2.0` - New features (backward compatible)  
- `1.0.0` - Major changes (may break compatibility)
- `1.0.0-beta.1` - Pre-release versions

## Files Updated Automatically

- `pyproject.toml` - Package metadata
- `bookforge/__init__.py` - Python module version

## What Gets Created

- Git commit with version changes
- Git tag (e.g., `v0.1.1`)
- PyPI package upload
- GitHub push (commits + tags)

## Troubleshooting

**Common fixes:**
```bash
# Clean working directory
git add . && git commit -m "Prepare for release"

# Install missing tools
pip install build twine

# Reset failed release
git reset --hard HEAD~1  # Remove commit
git tag -d v0.1.1        # Remove tag
rm -rf build/ dist/ *.egg-info/  # Clean builds
```

See full documentation: `docs/RELEASE.md`