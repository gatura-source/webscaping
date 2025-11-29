import pytest
from crawler.parser import parse_page, parse_book

def test_parse_listing_sample():
    sample_html = open("tests/fixtures/listing_sample.html").read()
    links, next_url = parse_page(sample_html, "https://books.toscrape.com/")
    assert isinstance(links, list)
    assert next_url is not None

def test_parse_book_sample():
    sample_html = open("tests/fixtures/book_sample.html").read()
    data = parse_book(sample_html, "https://books.toscrape.com/")
    assert data["name"] != ""
    assert "price_excl_vat" in data
