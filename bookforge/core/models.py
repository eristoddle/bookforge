from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class BookMetadata:
    """Book metadata for EPUB generation"""
    title: str
    author: str
    language: str = "en"
    description: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[datetime] = None
    isbn: Optional[str] = None
    cover_image: Optional[str] = None
    theme: str = "modern"
    
    def __post_init__(self):
        if self.publication_date is None:
            self.publication_date = datetime.now()


@dataclass
class Chapter:
    """Represents a chapter in the book"""
    title: str
    content: str
    filename: str
    order: int = 0
    
    def __post_init__(self):
        if not self.filename.endswith('.xhtml'):
            self.filename = f"{self.filename}.xhtml"


@dataclass
class BookStructure:
    """Complete book structure for EPUB generation"""
    metadata: BookMetadata
    chapters: List[Chapter]
    table_of_contents: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        # Auto-generate TOC if not provided
        if self.table_of_contents is None:
            self.table_of_contents = [
                {
                    "title": chapter.title,
                    "filename": chapter.filename,
                    "order": chapter.order
                }
                for chapter in sorted(self.chapters, key=lambda c: c.order)
            ]


@dataclass
class GenerationJob:
    """Represents an EPUB generation job"""
    id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    book_structure: Optional[BookStructure] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()