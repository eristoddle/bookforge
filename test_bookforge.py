#!/usr/bin/env python3
"""
Simple test script to verify BookForge functionality
"""
import os
import sys
import json
import subprocess
from pathlib import Path

def test_cli():
    """Test CLI functionality"""
    print("🧪 Testing CLI functionality...")
    
    # Test preview
    result = subprocess.run([
        sys.executable, "-m", "bookforge.cli", "preview", "examples/sample_book"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Preview failed: {result.stderr}")
        return False
    
    if "Total chapters: 4" not in result.stdout:
        print(f"❌ Preview output unexpected: {result.stdout}")
        return False
    
    print("✅ CLI preview works")
    
    # Test generation
    result = subprocess.run([
        sys.executable, "-m", "bookforge.cli", "generate", "examples/sample_book",
        "--title", "Test Book",
        "--author", "Test Author",
        "--theme", "minimal",
        "--output", "test_output.epub"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Generation failed: {result.stderr}")
        return False
    
    if not os.path.exists("test_output.epub"):
        print("❌ Output file not created")
        return False
    
    # Clean up
    os.remove("test_output.epub")
    print("✅ CLI generation works")
    
    return True

def test_import():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from bookforge.core.book_service import BookService
        from bookforge.core.epub_generator import EPUBGenerator
        from bookforge.core.markdown_processor import MarkdownProcessor
        from bookforge.core.github_integration import GitHubIntegration
        from bookforge.core.validator import EPUBValidator
        from bookforge.main import app
        print("✅ All modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_epub_structure():
    """Test that generated EPUB has correct structure"""
    print("🧪 Testing EPUB structure...")
    
    # Generate a test EPUB
    result = subprocess.run([
        sys.executable, "-m", "bookforge.cli", "generate", "examples/sample_book",
        "--title", "Structure Test",
        "--author", "Test Author",
        "--output", "structure_test.epub"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to generate test EPUB: {result.stderr}")
        return False
    
    # Check ZIP structure
    result = subprocess.run([
        "unzip", "-l", "structure_test.epub"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to read EPUB structure: {result.stderr}")
        return False
    
    required_files = [
        "mimetype",
        "META-INF/container.xml",
        "OEBPS/content.opf",
        "OEBPS/nav.xhtml",
        "OEBPS/toc.ncx",
        "OEBPS/Styles/styles.css"
    ]
    
    for required_file in required_files:
        if required_file not in result.stdout:
            print(f"❌ Missing required file: {required_file}")
            return False
    
    # Clean up
    os.remove("structure_test.epub")
    print("✅ EPUB structure is correct")
    return True

def main():
    """Run all tests"""
    print("🚀 BookForge Test Suite")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("Module Imports", test_import),
        ("CLI Functionality", test_cli),
        ("EPUB Structure", test_epub_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! BookForge is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())