import zipfile
import os
import uuid
from pathlib import Path
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

from .models import BookStructure, Chapter, BookMetadata
from ..config import get_settings


class EPUBGenerator:
    """Core EPUB 3 generation engine"""
    
    def __init__(self):
        self.settings = get_settings()
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    def generate_epub(self, book_structure: BookStructure) -> str:
        """Generate EPUB file from book structure"""
        # Create temporary directory for EPUB contents
        temp_id = str(uuid.uuid4())
        temp_dir = Path(self.settings.temp_dir) / temp_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build EPUB structure
            self._create_epub_structure(temp_dir, book_structure)
            
            # Create EPUB file
            output_filename = f"{book_structure.metadata.title.replace(' ', '_')}_{temp_id[:8]}.epub"
            output_path = Path(self.settings.output_dir) / output_filename
            
            self._create_epub_file(temp_dir, output_path)
            
            return str(output_path)
            
        finally:
            # Clean up temporary directory
            self._cleanup_directory(temp_dir)
    
    def _create_epub_structure(self, base_dir: Path, book: BookStructure):
        """Create the complete EPUB directory structure"""
        # Create required directories
        meta_inf_dir = base_dir / "META-INF"
        oebps_dir = base_dir / "OEBPS"
        text_dir = oebps_dir / "Text"
        css_dir = oebps_dir / "Styles"
        images_dir = oebps_dir / "Images"
        
        for dir_path in [meta_inf_dir, oebps_dir, text_dir, css_dir, images_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create mimetype file
        with open(base_dir / "mimetype", "w") as f:
            f.write("application/epub+zip")
        
        # Create META-INF/container.xml
        self._create_container_xml(meta_inf_dir)
        
        # Create content.opf (package document)
        self._create_content_opf(oebps_dir, book)
        
        # Create table of contents (toc.ncx and nav.xhtml)
        self._create_toc_files(oebps_dir, book)
        
        # Create chapter files
        self._create_chapter_files(text_dir, book.chapters)
        
        # Create CSS files
        self._create_css_files(css_dir, book.metadata.theme)
        
        # Copy cover image if provided
        if book.metadata.cover_image:
            self._copy_cover_image(images_dir, book.metadata.cover_image)
    
    def _create_container_xml(self, meta_inf_dir: Path):
        """Create META-INF/container.xml"""
        template = self.jinja_env.get_template("container.xml")
        content = template.render()
        
        with open(meta_inf_dir / "container.xml", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _create_content_opf(self, oebps_dir: Path, book: BookStructure):
        """Create content.opf package document"""
        template = self.jinja_env.get_template("content.opf")
        
        # Generate unique identifier
        book_id = f"urn:uuid:{uuid.uuid4()}"
        
        content = template.render(
            book_id=book_id,
            metadata=book.metadata,
            chapters=book.chapters,
            has_cover=book.metadata.cover_image is not None
        )
        
        with open(oebps_dir / "content.opf", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _create_toc_files(self, oebps_dir: Path, book: BookStructure):
        """Create both toc.ncx and nav.xhtml for navigation"""
        # Create toc.ncx (EPUB 2 compatibility)
        ncx_template = self.jinja_env.get_template("toc.ncx")
        ncx_content = ncx_template.render(
            metadata=book.metadata,
            chapters=book.chapters
        )
        
        with open(oebps_dir / "toc.ncx", "w", encoding="utf-8") as f:
            f.write(ncx_content)
        
        # Create nav.xhtml (EPUB 3)
        nav_template = self.jinja_env.get_template("nav.xhtml")
        nav_content = nav_template.render(
            metadata=book.metadata,
            chapters=book.chapters
        )
        
        with open(oebps_dir / "nav.xhtml", "w", encoding="utf-8") as f:
            f.write(nav_content)
    
    def _create_chapter_files(self, text_dir: Path, chapters: List[Chapter]):
        """Create XHTML files for each chapter"""
        chapter_template = self.jinja_env.get_template("chapter.xhtml")
        
        for chapter in chapters:
            content = chapter_template.render(
                title=chapter.title,
                content=chapter.content
            )
            
            with open(text_dir / chapter.filename, "w", encoding="utf-8") as f:
                f.write(content)
    
    def _create_css_files(self, css_dir: Path, theme: str):
        """Create CSS files based on theme"""
        css_template = self.jinja_env.get_template(f"themes/{theme}.css")
        css_content = css_template.render()
        
        with open(css_dir / "styles.css", "w", encoding="utf-8") as f:
            f.write(css_content)
    
    def _copy_cover_image(self, images_dir: Path, cover_path: str):
        """Copy cover image to EPUB structure"""
        # This would copy the cover image file
        # Implementation depends on where cover images are stored
        pass
    
    def _create_epub_file(self, temp_dir: Path, output_path: Path):
        """Create the final EPUB zip file"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub_file:
            # Add mimetype first (uncompressed)
            epub_file.write(
                temp_dir / "mimetype", 
                "mimetype", 
                compress_type=zipfile.ZIP_STORED
            )
            
            # Add all other files
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == "mimetype":
                        continue  # Already added
                    
                    file_path = Path(root) / file
                    archive_path = file_path.relative_to(temp_dir)
                    epub_file.write(file_path, archive_path)
    
    def _cleanup_directory(self, directory: Path):
        """Clean up temporary directory"""
        import shutil
        if directory.exists():
            shutil.rmtree(directory)