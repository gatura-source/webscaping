from selectolax.parser import HTMLParser
from urllib.parse import urljoin
from typing import Tuple, Optional
import re
from utils.logger import get_logger


def parse_page(html: str, base_url: str) -> Tuple[list[str], Optional[str]]:
    logger = get_logger("parse_page")
    try:
        tree = HTMLParser(html)
        links = []
        for node in tree.css('article.product_pod h3 a'):
            href = node.attributes.get("href")
            if href:
                links.append(urljoin(base_url, href))
        # Next page (PAGINATION)
        next_node = tree.css_first("li.next a")
        next_url = urljoin(base_url, next_node.attributes.get("href")) if next_node else None
        return links, next_url
    except Exception as th:
        logger.warning(f"parse_page encountered an error while processing "
                        f"{html}: {th}")


def parse_book(book_html: str, base_url: str) -> dict:
    book_tree = HTMLParser(book_html)
    book_title = book_tree.css_first("div.product_main h1").text()
    # some books missing desc
    desc_node = book_tree.css_first("#product_description ~ p")
    book_desc = desc_node.text().strip() if desc_node else None
    # category
    categ_crumbs = book_tree.css("ul.breadcrumb li a")
    book_categ = categ_crumbs[-1].text() if categ_crumbs and len(categ_crumbs) >= 3 else None
    # price
    
    # def find_text(selector):
    #     n.text().strip() if (n := book_tree.css_first(selector)) else None
    # price_excl = find_text("th:contains('Price (excl. tax)') + td")

    # this is much safer
    bk_table = {book_row.css_first("th").text(): book_row.css_first("td") for book_row in book_tree.css("table.table tr")}
    price_excl = float(bk_table.get("Price (excl. tax)", "").lstrip("£") or 0)
    price_incl = float(bk_table.get("Price (incl. tax)", "").lstrip("£") or 0)
    # availability
    book_availability = bk_table.get("Availability")
    # num_reviews
    book_num_reviews = int(bk_table.get("Number of reviews", "0"))
    # image
    book_img = book_tree.css_first("div.carousel-inner img") or book_tree.css_first("div.item img") or book_tree.css_first("img")
    book_img_url = urljoin(base_url, book_img.attributes.get("src")) if book_img else None
    # rating
    rating_node = book_tree.css_first("p.star_rating")
    rating = 0
    if rating_node:
        classes = rating_node.attributes.get("class", "")
        m = re.search(r"star-rating\s+(\w+)", classes)
        mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = mapping.get(m.group(1), 0) if m else 0
    
    # dict
    return {
        "name": book_title,
        "description": book_desc,
        "category": book_categ,
        "price_incl_vat": price_incl,
        "price_excl_vat": price_excl,
        "availability": book_availability,
        "num_reviews": book_num_reviews,
        "image_url": book_img_url,
        "rating": rating
    }