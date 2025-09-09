# Web Interface Guide

BookForge provides a beautiful, user-friendly web interface that makes EPUB generation as simple as uploading files and filling in a form. No technical knowledge required!

## 🌐 Accessing the Interface

1. **Start the server**:
   ```bash
   bookforge serve
   # or
   python -m bookforge.main
   ```

2. **Open your browser** to: http://localhost:8000

## 📖 Using the Interface

### Upload Files Method

1. **Select Files**
   - Drag and drop your markdown files onto the upload area
   - Or click to browse and select files
   - Only `.md` and `.markdown` files are accepted

2. **Fill Book Details**
   - **Title** (required): Your book's title
   - **Author** (required): Your name or pen name
   - **Description**: Brief summary of your book
   - **Language**: Select from supported languages
   - **Publisher**: Optional publisher name

3. **Choose Theme**
   - **Modern**: Clean, contemporary design
   - **Classic**: Traditional book styling
   - **Minimal**: Ultra-clean layout

4. **Generate**
   - Click "Generate EPUB" and wait for processing
   - Progress will be shown in real-time
   - Download button appears when complete

### GitHub Integration Method

1. **Enter Repository URL**
   - Paste your GitHub repository URL
   - Example: `https://github.com/username/my-book`

2. **Specify Folder** (optional)
   - Enter folder path if markdown files are in a subdirectory
   - Example: `docs` or `chapters`

3. **Book Details**
   - Title and author are auto-detected from repository
   - Override if needed

4. **Generate**
   - System fetches files from GitHub automatically
   - Same generation process as file upload

## 🎨 Theme Previews

The interface shows live previews of each theme:

### Modern Theme
- Sans-serif fonts (System UI, Segoe UI, Roboto)
- Clean, spacious layout
- Blue accent colors
- Perfect for: Technical documentation, business books

### Classic Theme  
- Serif fonts (Times New Roman)
- Traditional typography
- Centered chapter titles
- Perfect for: Fiction, academic works, formal publications

### Minimal Theme
- Charter/Georgia serif fonts
- Ultra-clean layout
- Generous whitespace
- Perfect for: Essays, contemplative works, focused reading

## 📊 Real-Time Status

The interface provides live updates during generation:

- **⏳ Pending**: Job queued for processing
- **⚙️ Processing**: EPUB being generated
- **✅ Completed**: Ready for download
- **❌ Failed**: Error occurred

## 📥 Download and Validation

Once generation completes:

1. **Download Button**: Instantly download your EPUB
2. **Validation Results**: See if your EPUB passes quality checks
3. **File Info**: View file size and generation details

## 🔧 Advanced Features

### Recent Jobs
- View your last 10 generation jobs
- Re-download completed EPUBs
- Track job history

### File Management
- Preview selected files before upload
- Remove files from selection
- See file sizes and counts

### Error Handling
- Clear error messages if generation fails
- Helpful suggestions for common issues
- Retry functionality

## 📱 Mobile Friendly

The interface is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🚀 Tips for Best Results

1. **File Organization**
   - Use numbered prefixes: `01_intro.md`, `02_chapter1.md`
   - Keep consistent naming
   - Organize chapters logically

2. **Markdown Quality**
   - Start chapters with H1 headings (`# Chapter Title`)
   - Use proper markdown syntax
   - Test in a markdown previewer first

3. **Images and Links**
   - Use relative paths for images
   - Ensure all links are valid
   - Optimize image sizes

4. **GitHub Repositories**
   - Use clear folder structure
   - Include README with book info
   - Keep markdown files organized

## 🆘 Troubleshooting

### Common Issues

**Files not uploading**
- Check file extensions (.md, .markdown only)
- Ensure files aren't too large
- Try refreshing the page

**Generation fails**
- Check markdown syntax
- Ensure all required fields are filled
- Try with fewer files first

**GitHub connection fails**
- Verify repository URL is correct
- Check if repository is public
- Try without folder path first

### Getting Help

- Check validation results for specific errors
- Try the preview feature to check structure
- Use the CLI for more detailed error messages
- Visit the API documentation for technical details

## 🔗 Integration with Other Tools

### Save Settings
Bookmark URLs with your preferred settings:
- Theme selection
- Default author/publisher
- Language preferences

### Download Management
- EPUBs are ready immediately
- Files are automatically named
- Standard EPUB format works everywhere

### Sharing
- Share generated EPUBs instantly
- Works with all e-reader apps
- Upload to any ebook platform

The web interface makes professional EPUB generation accessible to everyone, from authors to technical writers to educators. No command line knowledge needed!