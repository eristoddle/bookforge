from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

from .models import BookMetadata, BookStructure, Chapter
from .markdown_processor import MarkdownProcessor
from .epub_generator import EPUBGenerator
from .github_integration import GitHubIntegration
from .validator import EPUBValidator
from ..config import get_settings


class BookService:
    """High-level service for book generation operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.markdown_processor = MarkdownProcessor()
        self.epub_generator = EPUBGenerator()
        self.github_integration = GitHubIntegration()
        self.validator = EPUBValidator()
    
    async def generate_from_github(
        self,
        github_url: str,
        folder_path: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        theme: str = "modern",
        language: str = "en",
        description: Optional[str] = None,
        publisher: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate EPUB from GitHub repository
        Returns (output_path, validation_results)
        """
        # Fetch markdown files from GitHub
        markdown_files = self.github_integration.fetch_markdown_files(
            github_url, folder_path
        )
        
        if not markdown_files:
            raise ValueError("No markdown files found in the specified repository/path")
        
        # Get repository metadata if title/author not provided
        if not title or not author:
            repo_metadata = self.github_integration.get_repository_metadata(github_url)
            title = title or repo_metadata.get('title', 'Untitled Book')
            author = author or repo_metadata.get('author', 'Unknown Author')
            description = description or repo_metadata.get('description')
        
        return await self.generate_from_files(
            markdown_files=markdown_files,
            title=title,
            author=author,
            theme=theme,
            language=language,
            description=description,
            publisher=publisher
        )
    
    async def generate_from_files(
        self,
        markdown_files: List[Tuple[str, str]],
        title: str,
        author: str,
        theme: str = "modern",
        language: str = "en",
        description: Optional[str] = None,
        publisher: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate EPUB from markdown files
        Returns (output_path, validation_results)
        """
        # Create book metadata
        metadata = BookMetadata(
            title=title,
            author=author,
            language=language,
            description=description,
            publisher=publisher,
            theme=theme,
            publication_date=datetime.now()
        )
        
        # Process markdown files into chapters
        chapters = self.markdown_processor.extract_chapters_from_directory(
            markdown_files
        )
        
        if not chapters:
            raise ValueError("No valid chapters found in markdown files")
        
        # Create book structure
        book_structure = BookStructure(
            metadata=metadata,
            chapters=chapters
        )
        
        # Generate EPUB
        output_path = self.epub_generator.generate_epub(book_structure)
        
        # Validate EPUB if enabled
        validation_results = {}
        if self.settings.epub_validation:
            validation_results = self.validator.validate_epub(output_path)
        
        return output_path, validation_results
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        return ["modern", "classic", "minimal"]
    
    def validate_theme(self, theme: str) -> bool:
        """Validate if theme exists"""
        return theme in self.get_available_themes()
    
    async def preview_book_structure(
        self,
        markdown_files: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Preview book structure without generating EPUB
        Returns metadata about chapters and structure
        """
        chapters = self.markdown_processor.extract_chapters_from_directory(
            markdown_files
        )
        
        return {
            'chapter_count': len(chapters),
            'chapters': [
                {
                    'title': chapter.title,
                    'filename': chapter.filename,
                    'order': chapter.order,
                    'word_count': len(chapter.content.split())
                }
                for chapter in chapters
            ],
            'total_words': sum(len(chapter.content.split()) for chapter in chapters),
            'estimated_pages': sum(len(chapter.content.split()) for chapter in chapters) // 250  # ~250 words per page
        }