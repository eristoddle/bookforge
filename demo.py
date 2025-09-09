#!/usr/bin/env python3
"""
BookForge API Demo - Shows how to use the BookForge API programmatically
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bookforge.core.book_service import BookService
from bookforge.core.models import BookMetadata


async def demo_api_usage():
    """Demonstrate BookForge API usage"""
    print("🚀 BookForge API Demo")
    print("=" * 50)
    
    # Initialize the book service
    book_service = BookService()
    
    # Demo 1: Generate from local files
    print("\n📚 Demo 1: Generate from local markdown files")
    
    # Read sample files
    sample_dir = Path("examples/sample_book")
    markdown_files = []
    
    for md_file in sorted(sample_dir.glob("*.md")):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        markdown_files.append((md_file.name, content))
    
    print(f"📄 Found {len(markdown_files)} markdown files")
    
    # Generate EPUB
    try:
        output_path, validation_results = await book_service.generate_from_files(
            markdown_files=markdown_files,
            title="API Demo Book",
            author="BookForge Demo",
            theme="classic",
            description="A demonstration book generated via the BookForge API"
        )
        
        print(f"✅ EPUB generated: {output_path}")
        print(f"📊 Validation: {'✅ Valid' if validation_results.get('valid') else '❌ Invalid'}")
        
        if validation_results.get('warnings'):
            print(f"⚠️  Warnings: {len(validation_results['warnings'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Demo 2: Preview book structure
    print("\n📋 Demo 2: Preview book structure")
    
    try:
        preview = await book_service.preview_book_structure(markdown_files)
        
        print(f"📖 Chapters: {preview['chapter_count']}")
        print(f"📝 Words: {preview['total_words']:,}")
        print(f"📄 Est. pages: {preview['estimated_pages']}")
        
        print("\n📋 Chapter breakdown:")
        for i, chapter in enumerate(preview['chapters'], 1):
            print(f"  {i}. {chapter['title']} ({chapter['word_count']} words)")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Demo 3: Available themes
    print("\n🎨 Demo 3: Available themes")
    themes = book_service.get_available_themes()
    for theme in themes:
        print(f"  • {theme}")
    
    print("\n🎉 Demo completed!")


async def demo_github_integration():
    """Demonstrate GitHub integration (requires internet)"""
    print("\n🌐 GitHub Integration Demo")
    print("=" * 30)
    print("(This would fetch from a real GitHub repository)")
    print("Example usage:")
    print("  bookforge github https://github.com/user/repo")
    print("  or via API:")
    print("  POST /api/v1/generate/github")
    print("  {")
    print("    'github_url': 'https://github.com/user/repo',")
    print("    'title': 'My Book',")
    print("    'author': 'Author Name'")
    print("  }")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_api_usage())
    asyncio.run(demo_github_integration())
    
    print("\n📖 For more examples, see:")
    print("  • README.md")
    print("  • python -m bookforge.cli --help")
    print("  • http://localhost:8000/docs (when server is running)")