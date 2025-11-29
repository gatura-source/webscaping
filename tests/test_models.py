import pytest
from datetime import datetime, timezone
from crawler.models import BookDocument

def test_book_document_valid():
    doc = BookDocument(
        name="Test Book",
        description="A description",
        category="Fiction",
        price_excl_vat="10.5",
        price_incl_vat="12.5",
        availability="In stock",
        num_reviews=5,
        image_url="https://example.com/image.jpg",
        rating=4,
        source_url="https://example.com/book1",
        crawl_timestamp=datetime.now(timezone.utc),
        content_hash="abc123",
        raw_html="<html></html>",
        status="ok"
    )

    assert doc.name == "Test Book"
    assert doc.price_excl_vat == str(10.5)
    assert doc.rating == 4


def test_book_document_missing_required_fields():
    with pytest.raises(Exception):
        BookDocument(
            name="Missing Source URL",
            crawl_timestamp=datetime.now(timezone.utc),
            content_hash="hash",
        )
