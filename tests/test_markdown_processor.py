from bookforge.core.markdown_processor import MarkdownProcessor, strip_frontmatter


def test_strip_frontmatter_removes_leading_block():
    assert strip_frontmatter("---\ntitle: One\n---\n# One\n") == "# One\n"
    assert strip_frontmatter("---\ntitle: One\n...\n\n# One\n") == "# One\n"


def test_strip_frontmatter_leaves_other_text_alone():
    assert strip_frontmatter("# One\n---\nmore\n") == "# One\n---\nmore\n"
    # An unclosed block is body text, as Veneer's editor treats it
    assert strip_frontmatter("---\ntitle: One\n# One\n") == "---\ntitle: One\n# One\n"


def test_frontmatter_is_not_printed():
    chapter = MarkdownProcessor().process_markdown_file("---\ntitle: X\n---\n# Intro\n\nText\n", "01_a.md")
    assert "title: X" not in chapter.content
    assert chapter.title == "Intro"


def test_footnotes_do_not_carry_into_the_next_chapter():
    chapters = MarkdownProcessor().extract_chapters_from_directory([
        ("01_a.md", "# A\n\nHi[^1]\n\n[^1]: a note\n"),
        ("02_b.md", "# B\n\nNo notes here.\n"),
    ])
    assert "a note" in chapters[0].content
    assert "a note" not in chapters[1].content
    assert "footnote" not in chapters[1].content


def test_a_chapter_without_a_heading_is_named_after_its_file_without_the_number():
    processor = MarkdownProcessor()
    assert processor.process_markdown_file("Text only.\n", "03_the_storm.md").title == "The Storm"
    assert processor.process_markdown_file("Text only.\n", "harbor-lights.md").title == "Harbor Lights"
    assert processor.process_markdown_file("Text only.\n", "07.md").title == "07"
