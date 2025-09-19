#!/usr/bin/env python3
"""
BookForge Release Automation Script

This script automates the entire release process:
1. Updates version numbers in all relevant files
2. Commits and tags the release
3. Builds the package
4. Publishes to PyPI
5. Pushes to GitHub

Usage:
    python release.py <version> [--dry-run] [--test-pypi]

Examples:
    python release.py 0.1.1           # Release version 0.1.1
    python release.py 0.2.0 --dry-run # Test without actually releasing
    python release.py 0.1.1 --test-pypi # Upload to test PyPI
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], check: bool = True, capture: bool = False) -> Tuple[int, str]:
    """Run a command and return exit code and output."""
    print(f"Running: {' '.join(cmd)}")
    
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout.strip()
    else:
        result = subprocess.run(cmd, check=False)
        return result.returncode, ""


def validate_version(version: str) -> bool:
    """Validate semantic version format."""
    pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?$'
    return bool(re.match(pattern, version))


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    
    return match.group(1)


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> bool:
    """Update version in a specific file. Returns True if file was modified."""
    if not file_path.exists():
        print(f"Warning: {file_path} not found, skipping")
        return False
    
    content = file_path.read_text()
    original_content = content
    
    # Update version patterns
    patterns = [
        (rf'version = "{re.escape(old_version)}"', f'version = "{new_version}"'),
        (rf'__version__ = "{re.escape(old_version)}"', f'__version__ = "{new_version}"'),
        (rf'version="{re.escape(old_version)}"', f'version="{new_version}"'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        file_path.write_text(content)
        print(f"Updated version in {file_path}")
        return True
    
    return False


def update_all_versions(old_version: str, new_version: str) -> List[Path]:
    """Update version in all relevant files."""
    files_to_update = [
        Path("pyproject.toml"),
        Path("bookforge/__init__.py"),
    ]
    
    # Also check for version in README or other common files
    additional_files = [
        Path("README.md"),
        Path("docs/README.md"),
    ]
    
    modified_files = []
    
    for file_path in files_to_update:
        if update_version_in_file(file_path, old_version, new_version):
            modified_files.append(file_path)
    
    # Check additional files for version references
    for file_path in additional_files:
        if file_path.exists():
            content = file_path.read_text()
            if old_version in content:
                print(f"Warning: Found version {old_version} in {file_path} - may need manual update")
    
    return modified_files


def check_git_status() -> bool:
    """Check if git working directory is clean."""
    code, output = run_command(["git", "status", "--porcelain"], capture=True)
    if code != 0:
        print("Error: Not in a git repository")
        return False
    
    if output:
        print("Error: Git working directory is not clean:")
        print(output)
        print("Please commit or stash your changes first.")
        return False
    
    return True


def create_release_commit(version: str, modified_files: List[Path]) -> bool:
    """Create release commit and tag."""
    # Add modified files
    for file_path in modified_files:
        code, _ = run_command(["git", "add", str(file_path)])
        if code != 0:
            return False
    
    # Create commit
    commit_msg = f"Release version {version}"
    code, _ = run_command(["git", "commit", "-m", commit_msg])
    if code != 0:
        return False
    
    # Create tag
    tag_msg = f"Version {version}"
    code, _ = run_command(["git", "tag", "-a", f"v{version}", "-m", tag_msg])
    if code != 0:
        return False
    
    return True


def build_package() -> bool:
    """Build the package distributions."""
    # Clean previous builds
    for pattern in ["build", "dist", "*.egg-info"]:
        code, _ = run_command(["rm", "-rf", pattern])
    
    # Build package
    code, _ = run_command(["python", "-m", "build"])
    return code == 0


def check_package() -> bool:
    """Check package with twine."""
    code, _ = run_command(["python", "-m", "twine", "check", "dist/*"])
    return code == 0


def publish_package(test_pypi: bool = False) -> bool:
    """Publish package to PyPI."""
    if test_pypi:
        print("Publishing to Test PyPI...")
        code, _ = run_command([
            "python", "-m", "twine", "upload", 
            "--repository", "testpypi",
            "dist/*"
        ])
    else:
        print("Publishing to PyPI...")
        code, _ = run_command(["python", "-m", "twine", "upload", "dist/*"])
    
    return code == 0


def push_to_github() -> bool:
    """Push commits and tags to GitHub."""
    # Push commits
    code, _ = run_command(["git", "push"])
    if code != 0:
        return False
    
    # Push tags
    code, _ = run_command(["git", "push", "--tags"])
    return code == 0


def main():
    parser = argparse.ArgumentParser(description="Release BookForge")
    parser.add_argument("version", help="Version to release (e.g., 0.1.1)")
    parser.add_argument("--dry-run", action="store_true", help="Test without actually releasing")
    parser.add_argument("--test-pypi", action="store_true", help="Upload to Test PyPI instead")
    
    args = parser.parse_args()
    
    # Validate version format
    if not validate_version(args.version):
        print(f"Error: Invalid version format: {args.version}")
        print("Please use semantic versioning (e.g., 1.0.0, 0.1.1, 1.0.0-beta.1)")
        sys.exit(1)
    
    print(f"Starting release process for version {args.version}")
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
    
    try:
        # Get current version
        current_version = get_current_version()
        print(f"Current version: {current_version}")
        
        if current_version == args.version:
            print(f"Error: Version {args.version} is already the current version")
            sys.exit(1)
        
        # Check git status
        if not args.dry_run and not check_git_status():
            sys.exit(1)
        
        # Update version numbers
        print("Updating version numbers...")
        modified_files = update_all_versions(current_version, args.version)
        
        if not modified_files:
            print("No files were modified")
            sys.exit(1)
        
        print(f"Modified files: {[str(f) for f in modified_files]}")
        
        if args.dry_run:
            print("DRY RUN: Would commit, tag, build, and publish")
            # Restore files
            for file_path in modified_files:
                run_command(["git", "checkout", str(file_path)], check=False)
            return
        
        # Create release commit and tag
        print("Creating release commit and tag...")
        if not create_release_commit(args.version, modified_files):
            print("Error: Failed to create release commit")
            sys.exit(1)
        
        # Build package
        print("Building package...")
        if not build_package():
            print("Error: Failed to build package")
            sys.exit(1)
        
        # Check package
        print("Checking package...")
        if not check_package():
            print("Error: Package check failed")
            sys.exit(1)
        
        # Publish to PyPI
        if not publish_package(args.test_pypi):
            print("Error: Failed to publish package")
            sys.exit(1)
        
        # Push to GitHub
        print("Pushing to GitHub...")
        if not push_to_github():
            print("Error: Failed to push to GitHub")
            sys.exit(1)
        
        print(f"✅ Successfully released version {args.version}!")
        
        if args.test_pypi:
            print("📦 Published to Test PyPI")
            print("To install: pip install -i https://test.pypi.org/simple/ bookforge")
        else:
            print("📦 Published to PyPI")
            print("To install: pip install bookforge")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()