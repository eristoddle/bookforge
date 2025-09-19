# Themes and Styling

## Built-in Themes

BookForge comes with several professional themes:

### Default Theme
Clean, readable design suitable for most books.
```yaml
theme:
  name: "default"
```

### Academic Theme
Formal styling for academic papers and textbooks.
```yaml
theme:
  name: "academic"
```

### Fiction Theme
Optimized for novels and creative writing.
```yaml
theme:
  name: "fiction"
```

### Technical Theme
Perfect for programming books and technical documentation.
```yaml
theme:
  name: "technical"
```

### Minimal Theme
Clean, distraction-free reading experience.
```yaml
theme:
  name: "minimal"
```

## Theme Configuration

### Basic Theme Setup

```yaml
theme:
  name: "academic"
  options:
    serif_font: true
    chapter_breaks: true
    drop_caps: true
```

### Typography Settings

```yaml
theme:
  name: "default"
  typography:
    body_font: "Georgia, serif"
    heading_font: "Arial, sans-serif"
    code_font: "Courier New, monospace"
    base_font_size: "16px"
    line_height: "1.6"
    paragraph_spacing: "1.2em"
```

### Color Scheme

```yaml
theme:
  name: "custom"
  colors:
    text: "#2c3e50"
    background: "#ffffff"
    accent: "#3498db"
    code_background: "#f8f9fa"
    blockquote: "#6c757d"
```

## Custom CSS

### Adding Custom Styles

Create a custom CSS file and reference it:

```yaml
theme:
  name: "default"
  custom_css: "assets/custom-styles.css"
```

Example `custom-styles.css`:

```css
/* Custom chapter headings */
h1 {
  color: #2c3e50;
  border-bottom: 3px solid #3498db;
  padding-bottom: 0.5em;
}

/* Custom blockquotes */
blockquote {
  border-left: 4px solid #3498db;
  background-color: #f8f9fa;
  padding: 1em;
  font-style: italic;
}

/* Custom code blocks */
pre {
  background-color: #2d3748;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 1.5em;
}
```

## Advanced Theme Customization

### Creating a Custom Theme

1. Create a theme directory structure:
```
themes/
└── my-theme/
    ├── theme.yaml
    ├── styles.css
    └── templates/
        ├── chapter.html
        └── toc.html
```

2. Define theme metadata in `theme.yaml`:
```yaml
name: "My Custom Theme"
version: "1.0.0"
author: "Your Name"
description: "A custom theme for my books"

base_theme: "default"

settings:
  chapter_numbering: true
  toc_depth: 3
  image_captions: true
```

3. Use the custom theme:
```yaml
theme:
  name: "my-theme"
  path: "./themes/my-theme"
```

### Theme Templates

Override default templates by creating HTML files in your theme's `templates/` directory:

#### Chapter Template (`chapter.html`)
```html
<div class="chapter">
  <h1 class="chapter-title">{{ chapter.title }}</h1>
  <div class="chapter-content">
    {{ chapter.content }}
  </div>
</div>
```

#### Table of Contents Template (`toc.html`)
```html
<nav class="toc">
  <h2>Table of Contents</h2>
  <ul>
    {% for chapter in chapters %}
    <li><a href="#{{ chapter.id }}">{{ chapter.title }}</a></li>
    {% endfor %}
  </ul>
</nav>
```

## Responsive Design

Themes automatically adapt to different screen sizes and reading devices:

```yaml
theme:
  responsive:
    mobile_breakpoint: "768px"
    tablet_breakpoint: "1024px"
    adjust_font_size: true
    optimize_images: true
```

## Theme Examples

### Business Book Theme
```yaml
theme:
  name: "custom"
  base_theme: "academic"
  colors:
    primary: "#1f2937"
    accent: "#3b82f6"
  typography:
    heading_font: "Inter, sans-serif"
    body_font: "Source Serif Pro, serif"
  options:
    chapter_numbers: true
    fancy_quotes: true
```

### Poetry Collection Theme
```yaml
theme:
  name: "custom"
  base_theme: "minimal"
  typography:
    body_font: "Crimson Text, serif"
    line_height: "1.8"
    text_align: "center"
  spacing:
    verse_spacing: "2em"
    stanza_spacing: "1.5em"
```