# Basic Usage Examples

This guide provides real-world examples of using BookForge for different types of projects.

## 📚 Example 1: Technical Documentation

Convert your project's documentation into a professional ebook.

### Scenario
You have a software project with documentation in markdown files that you want to distribute as an ebook.

### File Structure
```
project-docs/
├── 01-introduction.md
├── 02-getting-started.md
├── 03-configuration.md
├── 04-api-reference.md
├── 05-troubleshooting.md
└── images/
    ├── setup-diagram.png
    └── api-flow.png
```

### Using CLI
```bash
# Generate from local files
bookforge generate ./project-docs \
  --title "MyProject Documentation" \
  --author "Development Team" \
  --theme modern \
  --description "Complete guide to using MyProject" \
  --publisher "MyCompany Inc."

# Preview structure first
bookforge preview ./project-docs
```

### Using API
```bash
curl -X POST "http://localhost:8000/api/v1/generate/files" \
     -F "title=MyProject Documentation" \
     -F "author=Development Team" \
     -F "theme=modern" \
     -F "description=Complete guide to using MyProject" \
     -F "files=@01-introduction.md" \
     -F "files=@02-getting-started.md" \
     -F "files=@03-configuration.md" \
     -F "files=@04-api-reference.md" \
     -F "files=@05-troubleshooting.md"
```

### Expected Output
- Professional-looking EPUB with modern styling
- Proper table of contents
- Code syntax highlighting
- Responsive images
- ~50-100 pages depending on content

---

## 📖 Example 2: Fiction Novel

Transform your manuscript into a beautifully formatted ebook.

### Scenario
You've written a novel in markdown and want to create a publishable EPUB.

### File Structure
```
my-novel/
├── 00-prologue.md
├── 01-chapter-one.md
├── 02-chapter-two.md
├── 03-chapter-three.md
├── ...
├── 20-chapter-twenty.md
└── 21-epilogue.md
```

### Using CLI
```bash
bookforge generate ./my-novel \
  --title "The Digital Odyssey" \
  --author "Jane Author" \
  --theme classic \
  --description "A thrilling tale of technology and humanity" \
  --language en \
  --output "The_Digital_Odyssey.epub"
```

### Sample Chapter File (`01-chapter-one.md`)
```markdown
# Chapter One: The Beginning

The morning sun cast long shadows across the empty street as Sarah walked toward the office building that would change her life forever.

She had no idea what awaited her behind those glass doors—the discovery that would reshape everything she thought she knew about reality.

> Sometimes the most ordinary moments herald the most extraordinary changes.

The elevator hummed quietly as it carried her to the fifteenth floor, each passing second bringing her closer to her destiny.
```

### Expected Output
- Classic book styling with serif fonts
- Elegant chapter headings
- Proper paragraph formatting
- Professional blockquote styling
- Ready for distribution on major platforms

---

## 🎓 Example 3: Educational Course

Create course materials for students.

### Scenario
Convert your course content into an ebook for student distribution.

### Using GitHub Integration
```bash
# From GitHub repository
bookforge github https://github.com/professor/cs101-course \
  --folder course-materials \
  --title "Computer Science 101" \
  --author "Prof. Smith" \
  --theme modern \
  --description "Introduction to Computer Science"
```

### Repository Structure
```
cs101-course/
├── README.md
├── course-materials/
│   ├── 01-introduction.md
│   ├── 02-programming-basics.md
│   ├── 03-data-structures.md
│   ├── 04-algorithms.md
│   ├── 05-final-project.md
│   └── exercises/
│       ├── exercise-1.md
│       └── exercise-2.md
└── assignments/
```

### Using Web Interface
1. Go to http://localhost:8000
2. Click "From GitHub" tab
3. Enter: `https://github.com/professor/cs101-course`
4. Set folder: `course-materials`
5. Let auto-detection fill title/author
6. Choose "Modern" theme
7. Click "Generate from GitHub"

---

## 📋 Example 4: Corporate Handbook

Create an employee handbook from policy documents.

### Scenario
HR has policy documents in markdown that need to be distributed as an ebook.

### File Organization
```bash
# Create organized structure
mkdir employee-handbook
cd employee-handbook

# Create chapter files
cat > 01-welcome.md << EOF
# Welcome to ACME Corporation

Welcome to our team! This handbook contains everything you need to know about working at ACME Corporation.

## Our Mission
To innovate and excel in everything we do.

## Our Values
- Integrity
- Excellence
- Collaboration
- Innovation
EOF

cat > 02-policies.md << EOF
# Company Policies

## Work Hours
Standard work hours are 9 AM to 5 PM, Monday through Friday.

## Remote Work
Remote work is available with manager approval.

## Benefits
- Health insurance
- Retirement plan
- Paid time off
EOF
```

### Generation with Validation
```bash
# Generate with full validation
bookforge generate ./employee-handbook \
  --title "ACME Corporation Employee Handbook" \
  --author "ACME HR Department" \
  --theme classic \
  --publisher "ACME Corporation" \
  --validate

# Check the results
echo "EPUB generated successfully!"
ls -la *.epub
```

---

## 🔬 Example 5: Research Paper Collection

Compile research papers into a single volume.

### Scenario
Combine multiple research papers into one comprehensive ebook.

### Python Script for Batch Processing
```python
#!/usr/bin/env python3
"""
Batch process research papers into EPUBs
"""
import subprocess
import os
from pathlib import Path

def generate_research_collection():
    papers_dir = Path("research-papers")
    output_dir = Path("generated-books")
    output_dir.mkdir(exist_ok=True)
    
    # Process each paper collection
    collections = [
        {
            "path": papers_dir / "machine-learning",
            "title": "Machine Learning Research Collection",
            "author": "Research Team",
            "theme": "modern"
        },
        {
            "path": papers_dir / "quantum-computing", 
            "title": "Quantum Computing Papers",
            "author": "Physics Department",
            "theme": "classic"
        }
    ]
    
    for collection in collections:
        if collection["path"].exists():
            output_file = output_dir / f"{collection['title'].replace(' ', '_')}.epub"
            
            cmd = [
                "bookforge", "generate", str(collection["path"]),
                "--title", collection["title"],
                "--author", collection["author"],
                "--theme", collection["theme"],
                "--output", str(output_file)
            ]
            
            print(f"Generating: {collection['title']}")
            subprocess.run(cmd, check=True)
            print(f"✅ Complete: {output_file}")

if __name__ == "__main__":
    generate_research_collection()
```

---

## 🌐 Example 6: Multi-language Documentation

Generate documentation in multiple languages.

### File Structure
```
docs/
├── en/
│   ├── 01-introduction.md
│   ├── 02-usage.md
│   └── 03-advanced.md
├── es/
│   ├── 01-introduccion.md
│   ├── 02-uso.md
│   └── 03-avanzado.md
└── fr/
    ├── 01-introduction.md
    ├── 02-utilisation.md
    └── 03-avance.md
```

### Bash Script for Multiple Languages
```bash
#!/bin/bash
# Generate documentation in multiple languages

LANGUAGES=("en:English" "es:Spanish" "fr:French")
BASE_TITLE="Product Documentation"
AUTHOR="Documentation Team"

for lang_pair in "${LANGUAGES[@]}"; do
    IFS=':' read -r lang_code lang_name <<< "$lang_pair"
    
    echo "Generating $lang_name documentation..."
    
    bookforge generate "docs/$lang_code" \
        --title "$BASE_TITLE ($lang_name)" \
        --author "$AUTHOR" \
        --language "$lang_code" \
        --theme minimal \
        --output "${BASE_TITLE}_${lang_code}.epub"
        
    echo "✅ Generated: ${BASE_TITLE}_${lang_code}.epub"
done

echo "🎉 All language versions generated!"
```

---

## 📊 Tips for Each Use Case

### Technical Documentation
- Use **Modern** theme for clean code display
- Include lots of headings for navigation
- Test code examples before publishing
- Add troubleshooting section at the end

### Fiction
- Use **Classic** theme for traditional feel
- Start chapters with engaging openings
- Use blockquotes for emphasis or thoughts
- Consider chapter length (2000-5000 words ideal)

### Educational Content
- Use **Modern** or **Minimal** theme
- Include exercises and examples
- Add clear learning objectives
- Structure content progressively

### Corporate Documents
- Use **Classic** theme for formal appearance
- Include proper legal disclaimers
- Use consistent formatting
- Add contact information

### Research Papers
- Use **Modern** theme for technical content
- Include proper citations
- Add table of contents
- Consider adding index

### Multi-language
- Test character encoding for all languages
- Use appropriate fonts for language
- Consider reading direction (RTL languages)
- Validate with native speakers

Each example demonstrates different aspects of BookForge's flexibility and power. Choose the approach that best fits your workflow and requirements!