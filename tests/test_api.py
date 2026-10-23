import re
import zipfile

import pytest
from fastapi.testclient import TestClient

from bookforge.main import app


@pytest.fixture
def client():
    return TestClient(app)


def generate(client, files, **fields):
    data = {"title": "Test Book", "author": "A. Writer", **fields}
    upload = [("files", (name, text.encode("utf-8"), "text/markdown")) for name, text in files]
    response = client.post("/api/v1/generate/files", data=data, files=upload)
    assert response.status_code == 200, response.text
    # TestClient runs background tasks before returning, so the job is finished
    status = client.get(response.json()["status_url"]).json()
    assert status["status"] == "completed", status
    epub = client.get(status["download_url"])
    assert epub.status_code == 200
    return zipfile.ZipFile(__import__("io").BytesIO(epub.content))


def spine(book):
    opf = book.read("OEBPS/content.opf").decode("utf-8")
    return re.findall(r'<itemref idref="([^"]+)"', opf)


def test_chapters_sort_by_file_name_by_default(client):
    book = generate(client, [("02_b.md", "# B\n"), ("01_a.md", "# A\n")])
    nav = book.read("OEBPS/nav.xhtml").decode("utf-8")
    assert nav.index(">A<") < nav.index(">B<")


def test_keep_order_uses_upload_order(client):
    book = generate(client, [("zeta.md", "# Zeta\n"), ("alpha.md", "# Alpha\n")], keep_order="true")
    nav = book.read("OEBPS/nav.xhtml").decode("utf-8")
    assert nav.index(">Zeta<") < nav.index(">Alpha<")


def test_links_to_uploaded_chapters_point_at_their_xhtml(client):
    book = generate(client, [
        ("01_one.md", "# One\n\nGo to [two](02_two.md#scene) or [away](https://example.com/x.md).\n"),
        ("02_two.md", "# Two\n\nBack to [one](./01_one.md) and [missing](notes.md).\n"),
    ])
    one = book.read("OEBPS/Text/01_one.xhtml").decode("utf-8")
    two = book.read("OEBPS/Text/02_two.xhtml").decode("utf-8")
    assert 'href="02_two.xhtml#scene"' in one
    assert 'href="https://example.com/x.md"' in one
    assert 'href="01_one.xhtml"' in two
    assert 'href="notes.md"' in two


def test_title_with_unsafe_characters_still_makes_a_book(client):
    book = generate(client, [("01_a.md", "# A\n")], title="Part 1: Fire/Ice?")
    assert "mimetype" in book.namelist()
