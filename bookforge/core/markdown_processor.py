import markdown
from markdown.extensions import codehilite, toc, tables, fenced_code
from bs4 import BeautifulSoup
import re
from typing import List, Tuple
from .models import Chapter


FRONTMATTER_FENCE = re.compile(r'^(---|\.\.\.)\s*$')


def strip_frontmatter(content: str) -> str:
    """Remove a leading YAML frontmatter block (a first line of ---, closed by --- or ...)."""
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        return content
    for i in range(1, len(lines)):
        if FRONTMATTER_FENCE.match(lines[i]):
            return '\n'.join(lines[i + 1:]).lstrip('\n')
    return content


MARKDOWN_EXTENSION = re.compile(r'\.(md|markdown)$', re.IGNORECASE)


def chapter_stem(filename: str) -> str:
    """The chapter's file name without its folder or markdown extension: 01_one.md -> 01_one."""
    return MARKDOWN_EXTENSION.sub('', filename.replace('\\', '/').split('/')[-1])


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
        content = strip_frontmatter(content)

        # Extract title from first H1 or use filename
        title = self._extract_title(content)
        if not title:
            # Without a heading the name stands in, less any order number: 01_the_storm -> The Storm
            stem = re.sub(r'^\d+[_\-. ]+', '', chapter_stem(filename)) or chapter_stem(filename)
            title = stem.replace('_', ' ').replace('-', ' ').title()
        
        # Convert markdown to HTML. One Markdown instance serves every chapter, so
        # reset it first: otherwise footnotes and heading ids carry over.
        self.md.reset()
        html_content = self.md.convert(content)
        
        # Clean and structure the HTML
        html_content = self._clean_html(html_content)
        
        return Chapter(
            title=title,
            content=html_content,
            filename=chapter_stem(filename)
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
    
    def extract_chapters_from_directory(
        self,
        markdown_files: List[Tuple[str, str]],
        keep_order: bool = False
    ) -> List[Chapter]:
        """
        Extract chapters from a list of (filename, content) tuples.
        With keep_order the chapters stay in the given order; otherwise they are
        sorted by a number in the filename, then by filename.
        """
        chapters = []

        for filename, content in markdown_files:
            chapter = self.process_markdown_file(content, filename)
            chapter.order = 0 if keep_order else self._extract_order_from_filename(filename)
            chapters.append(chapter)

        if not keep_order:
            chapters.sort(key=lambda c: (c.order, c.filename))

        # Reassign sequential order numbers
        for i, chapter in enumerate(chapters):
            chapter.order = i + 1

        self._rewrite_chapter_links(chapters)
        return chapters

    def _rewrite_chapter_links(self, chapters: List[Chapter]) -> None:
        """Point links to another uploaded markdown file at that chapter's XHTML file."""
        # Chapter.filename already carries .xhtml
        targets = {c.filename[:-len('.xhtml')] for c in chapters}
        for chapter in chapters:
            soup = BeautifulSoup(chapter.content, 'html.parser')
            changed = False
            for link in soup.find_all('a', href=True):
                href = link['href']
                path, _, fragment = href.partition('#')
                if '://' in path or not MARKDOWN_EXTENSION.search(path):
                    continue
                stem = chapter_stem(path)
                if stem not in targets:
                    continue
                link['href'] = f"{stem}.xhtml" + (f"#{fragment}" if fragment else '')
                changed = True
            if changed:
                chapter.content = str(soup)

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