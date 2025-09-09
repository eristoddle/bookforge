import click
import os
import sys
from pathlib import Path
from typing import List, Optional
import asyncio

from .core.book_service import BookService
from .core.models import BookMetadata
from .config import get_settings


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    BookForge CLI - Generate beautiful EPUBs from markdown files
    
    The cloud-based alternative to Vellum, now available as a command-line tool.
    """
    pass


@main.command()
@click.argument('source', type=click.Path(exists=True))
@click.option('--title', '-t', help='Book title')
@click.option('--author', '-a', help='Book author')
@click.option('--theme', '-T', default='modern', type=click.Choice(['modern', 'classic', 'minimal']), help='Book theme')
@click.option('--language', '-l', default='en', help='Book language (ISO 639-1 code)')
@click.option('--description', '-d', help='Book description')
@click.option('--publisher', '-p', help='Publisher name')
@click.option('--output', '-o', type=click.Path(), help='Output EPUB file path')
@click.option('--validate/--no-validate', default=True, help='Validate generated EPUB')
def generate(
    source: str,
    title: Optional[str],
    author: Optional[str],
    theme: str,
    language: str,
    description: Optional[str],
    publisher: Optional[str],
    output: Optional[str],
    validate: bool
):
    """
    Generate EPUB from markdown files in a directory or single file
    
    SOURCE can be:
    - A directory containing markdown files
    - A single markdown file
    - A GitHub repository URL
    """
    click.echo(f"📚 BookForge EPUB Generator")
    click.echo(f"🔄 Processing: {source}")
    
    try:
        # Determine source type and collect files
        markdown_files = []
        
        if source.startswith(('http://', 'https://')) and 'github.com' in source:
            # GitHub URL
            from .core.github_integration import GitHubIntegration
            github = GitHubIntegration()
            
            click.echo("🌐 Fetching from GitHub...")
            markdown_files = github.fetch_markdown_files(source)
            
            # Auto-detect metadata from repo if not provided
            if not title or not author:
                repo_metadata = github.get_repository_metadata(source)
                title = title or repo_metadata.get('title', 'Untitled Book')
                author = author or repo_metadata.get('author', 'Unknown Author')
                description = description or repo_metadata.get('description')
            
        else:
            # Local files
            source_path = Path(source)
            
            if source_path.is_file():
                # Single file
                if not source_path.suffix.lower() in ['.md', '.markdown']:
                    click.echo("❌ Error: File must be a markdown file (.md, .markdown)", err=True)
                    sys.exit(1)
                
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                markdown_files = [(source_path.name, content)]
                
                # Auto-detect title from filename if not provided
                if not title:
                    title = source_path.stem.replace('_', ' ').replace('-', ' ').title()
            
            elif source_path.is_dir():
                # Directory
                click.echo("📁 Scanning directory for markdown files...")
                
                for md_file in source_path.rglob('*.md'):
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        markdown_files.append((md_file.name, content))
                    except UnicodeDecodeError:
                        click.echo(f"⚠️  Warning: Could not read {md_file} (encoding issue)")
                
                # Also check for .markdown files
                for md_file in source_path.rglob('*.markdown'):
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        markdown_files.append((md_file.name, content))
                    except UnicodeDecodeError:
                        click.echo(f"⚠️  Warning: Could not read {md_file} (encoding issue)")
                
                if not title:
                    title = source_path.name.replace('_', ' ').replace('-', ' ').title()
            
            else:
                click.echo("❌ Error: Source must be a file, directory, or GitHub URL", err=True)
                sys.exit(1)
        
        if not markdown_files:
            click.echo("❌ Error: No markdown files found", err=True)
            sys.exit(1)
        
        click.echo(f"📄 Found {len(markdown_files)} markdown file(s)")
        
        # Validate required metadata
        if not title:
            title = click.prompt("📖 Book title")
        if not author:
            author = click.prompt("✍️  Author name")
        
        # Generate EPUB
        click.echo("🔨 Generating EPUB...")
        
        book_service = BookService()
        output_path, validation_results = asyncio.run(
            book_service.generate_from_files(
                markdown_files=markdown_files,
                title=title,
                author=author,
                theme=theme,
                language=language,
                description=description,
                publisher=publisher
            )
        )
        
        # Move to specified output location if provided
        if output:
            output = Path(output)
            if not output.suffix:
                output = output / f"{title.replace(' ', '_')}.epub"
            
            output.parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).rename(output)
            output_path = str(output)
        
        click.echo(f"✅ EPUB generated: {output_path}")
        
        # Show validation results
        if validate and validation_results:
            if validation_results['valid']:
                click.echo("✅ EPUB validation passed!")
            else:
                click.echo("⚠️  EPUB validation issues found:")
                for error in validation_results.get('errors', []):
                    click.echo(f"   ❌ {error}")
                for warning in validation_results.get('warnings', []):
                    click.echo(f"   ⚠️  {warning}")
        
        # Show file info
        file_size = os.path.getsize(output_path)
        size_mb = file_size / (1024 * 1024)
        click.echo(f"📊 File size: {size_mb:.1f} MB")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('github_url')
@click.option('--folder', '-f', help='Specific folder path in repository')
@click.option('--title', '-t', help='Book title (auto-detected if not provided)')
@click.option('--author', '-a', help='Book author (auto-detected if not provided)')
@click.option('--theme', '-T', default='modern', type=click.Choice(['modern', 'classic', 'minimal']), help='Book theme')
@click.option('--output', '-o', type=click.Path(), help='Output EPUB file path')
def github(
    github_url: str,
    folder: Optional[str],
    title: Optional[str],
    author: Optional[str],
    theme: str,
    output: Optional[str]
):
    """
    Generate EPUB from GitHub repository
    
    GITHUB_URL should be a GitHub repository URL like:
    https://github.com/username/repository
    """
    click.echo(f"📚 BookForge GitHub Generator")
    click.echo(f"🌐 Repository: {github_url}")
    
    try:
        book_service = BookService()
        
        output_path, validation_results = asyncio.run(
            book_service.generate_from_github(
                github_url=github_url,
                folder_path=folder,
                title=title,
                author=author,
                theme=theme
            )
        )
        
        # Move to specified output location if provided
        if output:
            output = Path(output)
            if not output.suffix:
                # Auto-generate filename from title
                filename = f"{title or 'book'}.epub".replace(' ', '_')
                output = output / filename
            
            output.parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).rename(output)
            output_path = str(output)
        
        click.echo(f"✅ EPUB generated: {output_path}")
        
        # Show validation results
        if validation_results:
            if validation_results['valid']:
                click.echo("✅ EPUB validation passed!")
            else:
                click.echo("⚠️  EPUB validation issues found:")
                for error in validation_results.get('errors', []):
                    click.echo(f"   ❌ {error}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('source', type=click.Path(exists=True))
def preview(source: str):
    """
    Preview book structure without generating EPUB
    
    Shows chapter organization, word counts, and estimated page counts.
    """
    click.echo(f"📚 BookForge Preview")
    click.echo(f"🔍 Analyzing: {source}")
    
    try:
        # Collect markdown files
        markdown_files = []
        source_path = Path(source)
        
        if source_path.is_file():
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            markdown_files = [(source_path.name, content)]
        elif source_path.is_dir():
            for md_file in source_path.rglob('*.md'):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    markdown_files.append((md_file.name, content))
                except UnicodeDecodeError:
                    continue
        
        if not markdown_files:
            click.echo("❌ No markdown files found", err=True)
            sys.exit(1)
        
        book_service = BookService()
        preview_data = asyncio.run(
            book_service.preview_book_structure(markdown_files)
        )
        
        click.echo(f"\n📖 Book Structure Preview")
        click.echo(f"{'='*50}")
        click.echo(f"📄 Total chapters: {preview_data['chapter_count']}")
        click.echo(f"📝 Total words: {preview_data['total_words']:,}")
        click.echo(f"📚 Estimated pages: {preview_data['estimated_pages']}")
        click.echo(f"\n📋 Chapter Breakdown:")
        click.echo(f"{'='*50}")
        
        for i, chapter in enumerate(preview_data['chapters'], 1):
            click.echo(f"{i:2d}. {chapter['title']}")
            click.echo(f"     📄 {chapter['word_count']:,} words")
            click.echo(f"     📁 {chapter['filename']}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
def themes():
    """List available themes"""
    click.echo("🎨 Available Themes:")
    click.echo("="*30)
    
    themes_info = {
        'modern': 'Clean, contemporary design with sans-serif fonts',
        'classic': 'Traditional book styling with serif fonts',
        'minimal': 'Ultra-clean, distraction-free layout'
    }
    
    for theme, description in themes_info.items():
        click.echo(f"📖 {theme.capitalize()}")
        click.echo(f"   {description}")
        click.echo()


@main.command()
@click.option('--port', '-p', default=8000, help='Port to run the server on')
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind the server to')
def serve(port: int, host: str):
    """Start the BookForge API server"""
    click.echo(f"🚀 Starting BookForge API server...")
    click.echo(f"🌐 Server will be available at: http://{host}:{port}")
    click.echo(f"📖 API docs: http://{host}:{port}/docs")
    
    try:
        import uvicorn
        from .main import app
        
        uvicorn.run(app, host=host, port=port, reload=False)
    except ImportError:
        click.echo("❌ Error: uvicorn is required to run the server", err=True)
        click.echo("Install with: pip install uvicorn", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error starting server: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()