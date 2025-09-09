import markdown
from markdown.extensions import codehilite, toc, tables, fenced_code
from bs4 import BeautifulSoup
import re
from typing import List, Tuple
from .models import Chapter


class MarkdownProcessor:
    """Processes markdown content into HTML suitable for EPUB"""
    
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',
                'toc',
                'tables',
                'fenced_code',
                'attr_list',
                'def_list',
                'footnotes',
                'md_in_html'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                },
                'toc': {
                    'permalink': False
                }
            }
        )
    
    def process_markdown_file(self, content: str, filename: str) -> Chapter:
        """Convert markdown content to a Chapter object"""
        # Extract title from first H1 or use filename
        title = self._extract_title(content)
        if not title:
            title = filename.replace('.md', '').replace('_', ' ').title()
        
        # Convert markdown to HTML
        html_content = self.md.convert(content)
        
        # Clean and structure the HTML
        html_content = self._clean_html(html_content)
        
        return Chapter(
            title=title,
            content=html_content,
            filename=filename.replace('.md', '')
        )
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()
        return ""
    
    def _clean_html(self, html: str) -> str:
        """Clean and optimize HTML for EPUB"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove any script tags
        for script in soup.find_all('script'):
            script.decompose()
        
        # Clean up code blocks
        for code_block in soup.find_all('pre'):
            code_block['class'] = code_block.get('class', []) + ['code-block']
        
        # Ensure proper paragraph structure
        for p in soup.find_all('p'):
            if not p.get_text(strip=True):
                p.decompose()
        
        return str(soup)
    
    def extract_chapters_from_directory(self, markdown_files: List[Tuple[str, str]]) -> List[Chapter]:
        """
        Extract chapters from a list of (filename, content) tuples
        Returns sorted chapters based on filename or explicit ordering
        """
        chapters = []
        
        for filename, content in markdown_files:
            chapter = self.process_markdown_file(content, filename)
            
            # Try to extract order from filename (e.g., "01_chapter.md", "chapter_01.md")
            order = self._extract_order_from_filename(filename)
            chapter.order = order
            
            chapters.append(chapter)
        
        # Sort by order, then by filename
        chapters.sort(key=lambda c: (c.order, c.filename))
        
        # Reassign sequential order numbers
        for i, chapter in enumerate(chapters):
            chapter.order = i + 1
        
        return chapters
    
    def _extract_order_from_filename(self, filename: str) -> int:
        """Extract order number from filename"""
        # Look for patterns like "01_", "_01", "chapter01", etc.
        patterns = [
            r'^(\d+)[_\-\.]',  # Starts with number
            r'[_\-](\d+)[_\-\.]',  # Number in middle
            r'(\d+)\.md$',  # Number before .md
            r'chapter[_\-]?(\d+)',  # "chapter" followed by number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename.lower())
            if match:
                return int(match.group(1))
        
        return 999  # Default high number for files without explicit ordering