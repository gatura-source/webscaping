import pytest
import mongomock_motor
from datetime import datetime, timezone
from crawler.models import BookDocument
from db import mongo

@pytest.fixture
def mock_motor_client(monkeypatch):
    """
    Patch motor client in mongo.py with an in-memory mongomock client.
    """
    mock_client = mongomock_motor.AsyncMongoMockClient()

    monkeypatch.setattr(mongo, "client", mock_client)
    monkeypatch.setattr(mongo, "db", mock_client["testdb"])
    monkeypatch.setattr(mongo, "books_col", mock_client["testdb"]["books"])
    monkeypatch.setattr(mongo, "changes_col", mock_client["testdb"]["changes"])

    return mock_client


@pytest.mark.asyncio
async def test_index_creation(mock_motor_client):
    await mongo.ensure_indexes()

    index_info = await mongo.books_col.index_information()

    assert "source_url_1" in index_info
    assert "category_1_price_excl_vat_1" in index_info


@pytest.mark.asyncio
async def test_book_insert_and_find(mock_motor_client):
    book = BookDocument(
        name="Test Book",
        description="Nice book",
        category="Poetry",
        price_excl_vat="10.0",
        price_incl_vat="12.0",
        availability="In stock",
        num_reviews=0,
        image_url="https://example.com/img.jpg",
        rating=5,
        source_url="https://example.com/book1",
        crawl_timestamp=datetime.now(timezone.utc),
        content_hash="xyz",
        raw_html="<html></html>",
    )

    await mongo.books_col.insert_one(book.model_dump(mode='json'))

    result = await mongo.books_col.find_one({"source_url": "https://example.com/book1"})

    assert result["name"] == "Test Book"
    assert result["price_excl_vat"] == str(10.0)
    assert result["rating"] == 5
