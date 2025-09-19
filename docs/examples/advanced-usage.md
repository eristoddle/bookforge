# Advanced Usage Examples

## Complex Project Structures

### Multi-Part Book Series

Organize a book series with shared resources:

```
book-series/
├── bookforge.yaml
├── shared/
│   ├── styles.css
│   ├── images/
│   └── templates/
├── book-1/
│   ├── bookforge.yaml
│   ├── content/
│   │   ├── 01-introduction.md
│   │   ├── 02-chapter-one.md
│   │   └── 03-conclusion.md
│   └── cover.jpg
├── book-2/
│   ├── bookforge.yaml
│   ├── content/
│   └── cover.jpg
└── scripts/
    ├── generate-all.py
    └── validate-series.py
```

Master configuration (`bookforge.yaml`):
```yaml
series:
  name: "The Complete Guide Series"
  author: "Expert Author"
  publisher: "Tech Publications"

shared_resources:
  styles: "./shared/styles.css"
  templates: "./shared/templates/"
  images: "./shared/images/"

books:
  - path: "./book-1"
    title: "Volume 1: Fundamentals"
  - path: "./book-2"
    title: "Volume 2: Advanced Topics"

output:
  series_bundle: true
  individual_books: true
  formats: ["epub", "pdf"]
```

Generate the entire series:
```python
#!/usr/bin/env python3
"""Generate complete book series."""

from bookforge import BookForge
from pathlib import Path
import yaml

def generate_series():
    """Generate all books in the series."""
    with open("bookforge.yaml") as f:
        config = yaml.safe_load(f)
    
    bf = BookForge()
    generated_books = []
    
    for book_config in config["books"]:
        book_path = Path(book_config["path"])
        
        print(f"Generating {book_config['title']}...")
        
        epub_path = bf.generate_from_directory(
            input_dir=book_path / "content",
            title=book_config["title"],
            author=config["series"]["author"],
            publisher=config["series"]["publisher"],
            theme_config={
                "custom_css": Path(config["shared_resources"]["styles"]),
                "templates": Path(config["shared_resources"]["templates"])
            }
        )
        
        generated_books.append(epub_path)
        print(f"✓ Generated: {epub_path}")
    
    return generated_books

if __name__ == "__main__":
    books = generate_series()
    print(f"\nSeries complete! Generated {len(books)} books.")
```

## Advanced Content Processing

### Custom Preprocessor

Create a custom content preprocessor:

```python
from bookforge import BookForge
from bookforge.processors import Processor
import re
from typing import Dict, Any

class AcademicPreprocessor(Processor):
    """Preprocessor for academic content."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.citation_style = config.get("citation_style", "apa")
        self.auto_number_sections = config.get("auto_number_sections", True)
        
    def process(self, content: str, metadata: Dict[str, Any]) -> str:
        """Process academic content with special formatting."""
        # Auto-number sections
        if self.auto_number_sections:
            content = self._number_sections(content)
        
        # Process citations
        content = self._process_citations(content)
        
        # Generate cross-references
        content = self._process_cross_references(content)
        
        # Add figure numbering
        content = self._number_figures(content)
        
        return content
    
    def _number_sections(self, content: str) -> str:
        """Auto-number sections."""
        chapter_num = 1
        section_num = 1
        subsection_num = 1
        
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            if line.startswith('# '):
                line = f"# {chapter_num}. {line[2:]}"
                chapter_num += 1
                section_num = 1
                subsection_num = 1
            elif line.startswith('## '):
                line = f"## {chapter_num-1}.{section_num} {line[3:]}"
                section_num += 1
                subsection_num = 1
            elif line.startswith('### '):
                line = f"### {chapter_num-1}.{section_num-1}.{subsection_num} {line[4:]}"
                subsection_num += 1
                
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _process_citations(self, content: str) -> str:
        """Process citation markers."""
        # Convert [@author2023] to proper citations
        citation_pattern = r'\[@([^\]]+)\]'
        
        def replace_citation(match):
            citation_key = match.group(1)
            return f'<cite data-cite="{citation_key}">{citation_key}</cite>'
        
        return re.sub(citation_pattern, replace_citation, content)
    
    def _process_cross_references(self, content: str) -> str:
        """Process cross-references."""
        # Convert [@fig:figure1] to figure references
        ref_pattern = r'\[@(fig|tbl|sec):([^\]]+)\]'
        
        def replace_reference(match):
            ref_type = match.group(1)
            ref_id = match.group(2)
            
            ref_names = {
                'fig': 'Figure',
                'tbl': 'Table',
                'sec': 'Section'
            }
            
            return f'<a href="#{ref_id}" class="cross-ref">{ref_names[ref_type]} {ref_id}</a>'
        
        return re.sub(ref_pattern, replace_reference, content)
    
    def _number_figures(self, content: str) -> str:
        """Auto-number figures."""
        figure_num = 1
        
        def replace_figure(match):
            nonlocal figure_num
            alt_text = match.group(1)
            src = match.group(2)
            
            result = f'<figure id="fig{figure_num}">\n'
            result += f'  <img src="{src}" alt="{alt_text}" />\n'
            result += f'  <figcaption>Figure {figure_num}: {alt_text}</figcaption>\n'
            result += '</figure>'
            
            figure_num += 1
            return result
        
        # Match ![alt text](image.jpg)
        figure_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        return re.sub(figure_pattern, replace_figure, content)

# Usage
def generate_academic_book():
    bf = BookForge()
    
    # Add custom preprocessor
    academic_processor = AcademicPreprocessor({
        "citation_style": "apa",
        "auto_number_sections": True
    })
    
    bf.add_processor(academic_processor)
    
    return bf.generate_from_directory(
        input_dir="./academic-content",
        title="Research Methods in Computer Science",
        author="Dr. Academic",
        theme="academic"
    )
```

## Multi-Language Support

### Generating Books in Multiple Languages

```python
from bookforge import BookForge
from pathlib import Path
import yaml

class MultiLanguageGenerator:
    """Generate books in multiple languages."""
    
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
    
    def generate_all_languages(self):
        """Generate book in all configured languages."""
        results = {}
        
        for lang_config in self.config["languages"]:
            lang_code = lang_config["code"]
            print(f"Generating {lang_config['name']} version...")
            
            bf = BookForge()
            
            # Configure language-specific settings
            epub_path = bf.generate_from_directory(
                input_dir=f"./content/{lang_code}",
                title=lang_config["title"],
                author=lang_config["author"],
                language=lang_code,
                output_path=f"./dist/book-{lang_code}.epub",
                theme_config={
                    "fonts": lang_config.get("fonts", {}),
                    "text_direction": lang_config.get("text_direction", "ltr")
                }
            )
            
            results[lang_code] = epub_path
            print(f"✓ Generated: {epub_path}")
        
        return results

# Configuration file (multilang-config.yaml)
"""
languages:
  - code: "en"
    name: "English"
    title: "The Complete Guide"
    author: "Author Name"
    fonts:
      body: "Georgia, serif"
  - code: "es"
    name: "Spanish"
    title: "La Guía Completa"
    author: "Nombre del Autor"
    fonts:
      body: "Times New Roman, serif"
  - code: "ar"
    name: "Arabic"
    title: "الدليل الكامل"
    author: "اسم المؤلف"
    text_direction: "rtl"
    fonts:
      body: "Amiri, serif"
"""

# Usage
generator = MultiLanguageGenerator("multilang-config.yaml")
generated_books = generator.generate_all_languages()
```

## Advanced GitHub Integration

### Automated Publishing Pipeline

```python
#!/usr/bin/env python3
"""Advanced GitHub integration with automated publishing."""

import os
import requests
from bookforge import BookForge
from github import Github
from pathlib import Path

class GitHubPublisher:
    """Advanced GitHub integration for book publishing."""
    
    def __init__(self, github_token: str, repo_name: str):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
        self.bf = BookForge()
    
    def publish_on_release(self, tag_name: str):
        """Publish book when GitHub release is created."""
        try:
            release = self.repo.get_release(tag_name)
        except:
            print(f"Release {tag_name} not found")
            return
        
        # Generate EPUB from repository
        epub_path = self.bf.generate_from_github(
            repo_url=self.repo.clone_url,
            branch=release.target_commitish,
            title=f"{self.repo.name} - {tag_name}",
            version=tag_name
        )
        
        # Upload EPUB as release asset
        with open(epub_path, 'rb') as f:
            release.upload_asset(
                path=epub_path,
                content_type='application/epub+zip',
                name=f"{self.repo.name}-{tag_name}.epub"
            )
        
        print(f"✓ Published {epub_path} to release {tag_name}")
        return epub_path
    
    def auto_update_on_push(self, branch: str = "main"):
        """Automatically update book on push to branch."""
        # Get latest commit
        commits = self.repo.get_commits(sha=branch)
        latest_commit = commits[0]
        
        # Check if commit contains content changes
        content_changed = any(
            file.filename.startswith(('content/', 'docs/'))
            for file in latest_commit.files
        )
        
        if not content_changed:
            print("No content changes detected")
            return
        
        print(f"Content changes detected in {latest_commit.sha[:8]}")
        
        # Generate updated EPUB
        epub_path = self.bf.generate_from_github(
            repo_url=self.repo.clone_url,
            branch=branch,
            title=self.repo.name,
            commit_sha=latest_commit.sha
        )
        
        # Upload to releases or artifacts
        self._upload_development_build(epub_path, latest_commit)
        
        return epub_path
    
    def _upload_development_build(self, epub_path: str, commit):
        """Upload development build."""
        # Create development release
        release_name = f"Development Build - {commit.sha[:8]}"
        
        try:
            release = self.repo.create_git_release(
                tag=f"dev-{commit.sha[:8]}",
                name=release_name,
                message=f"Automated build from commit {commit.sha}",
                draft=True,
                prerelease=True
            )
            
            with open(epub_path, 'rb') as f:
                release.upload_asset(
                    path=epub_path,
                    content_type='application/epub+zip'
                )
                
        except Exception as e:
            print(f"Failed to create release: {e}")

# GitHub Actions workflow integration
def github_actions_integration():
    """Integration with GitHub Actions."""
    # Environment variables from GitHub Actions
    github_token = os.environ['GITHUB_TOKEN']
    repo_name = os.environ['GITHUB_REPOSITORY']
    event_name = os.environ['GITHUB_EVENT_NAME']
    
    publisher = GitHubPublisher(github_token, repo_name)
    
    if event_name == 'release':
        tag_name = os.environ['GITHUB_REF'].replace('refs/tags/', '')
        publisher.publish_on_release(tag_name)
    elif event_name == 'push':
        branch = os.environ['GITHUB_REF'].replace('refs/heads/', '')
        publisher.auto_update_on_push(branch)

if __name__ == "__main__":
    github_actions_integration()
```

## Performance Optimization

### Parallel Processing

```python
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from bookforge import BookForge
from pathlib import Path

class OptimizedGenerator:
    """High-performance EPUB generation."""
    
    def __init__(self, max_workers: int = 4):
        self.bf = BookForge()
        self.max_workers = max_workers
    
    async def generate_multiple_books(self, book_configs: list):
        """Generate multiple books in parallel."""
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def generate_single_book(config):
            async with semaphore:
                return await self._async_generate(config)
        
        tasks = [generate_single_book(config) for config in book_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def _async_generate(self, config):
        """Generate single book asynchronously."""
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor,
                self._sync_generate,
                config
            )
    
    def _sync_generate(self, config):
        """Synchronous generation wrapper."""
        return self.bf.generate_from_directory(
            input_dir=config["input_dir"],
            title=config["title"],
            author=config["author"],
            output_path=config["output_path"]
        )

# Usage
async def bulk_generation():
    generator = OptimizedGenerator(max_workers=8)
    
    book_configs = [
        {
            "input_dir": "./book1/content",
            "title": "Book 1",
            "author": "Author 1",
            "output_path": "./dist/book1.epub"
        },
        {
            "input_dir": "./book2/content",
            "title": "Book 2", 
            "author": "Author 2",
            "output_path": "./dist/book2.epub"
        },
        # ... more books
    ]
    
    results = await generator.generate_multiple_books(book_configs)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Failed to generate book {i}: {result}")
        else:
            print(f"Generated: {result}")

# Run the async generation
asyncio.run(bulk_generation())
```