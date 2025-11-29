import asyncio
import httpx
from typing import Set
from utils.config import appsettings
from crawler.client import fetch_html
from crawler.parser import parse_page, parse_book
from db.mongo import books_col, changes_col
from utils.hashing import sha256_text
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger("crawl_manager")


class Crawler:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(appsettings.CRAWL_CONCURRENCY)
        self.visited: Set[str] = set()

    async def _fetch_parse_book(self, client: httpx.AsyncClient, url: str):
        async with self.semaphore:
            markup_text = await fetch_html(url, client)
        parsed = parse_book(markup_text, self.base_url)
        content_hash = sha256_text(markup_text)
        now = datetime.now(timezone.utc)
        # check if existing
        existing = await books_col.find_one({"source_url": url})
        doc = {
            **parsed,
            "source_url": url,
            "crawl_timestamp": now,
            "content_hash": content_hash,
            "raw_html": markup_text,
            "status": "ok"
        }
        if not existing:
            response = await books_col.insert_one(doc)
            await changes_col.insert_one({
                "book_id": response.inserted_id,
                "source_url": url,
                "change_type": "new",
                "when": now,
                "details": {"name": parsed['name']}
            })
            logger.info(f"inserted new book: {parsed['name']}")
        else:
            if existing.get("content_hash") != content_hash:
                # check diff
                diffs = {}
                important_keys = [
                    "price_incl_vat",
                    "price_excl_vat",
                    "availability",
                    "nuw_reviews",
                    "name"
                ]
                for key in important_keys:
                    if existing.get(key) != parsed.get(key):
                        diffs[key] = {"old": existing.get(key),
                                      "new": parsed.get(key)}
                        await books_col.update_one({"_id": existing['_id']}, {'$set': doc})
                        await changes_col.insert_one({
                            "book_id": existing["_id"],
                            "source_url": url,
                            "change_type": "updated",
                            "when": now,
                            "details": diffs
                        })
                        logger.info(f"Updated book {parsed["name"]} diffs={diffs}")
    
    async def crawl(self, start_url: str):
        async with httpx.AsyncClient() as client:
            to_visit = [start_url]
            while to_visit:
                url = to_visit.pop(0)
                if url in self.visited: 
                    continue
                self.visited.add(url)
                try:
                    html = await fetch_html(url, client)
                except Exception as e:
                    logger.warning("Failed to fetch listing %s: %s", url, e)
                    continue
                links, next_url = parse_page(html, self.base_url)
                # normalize book urls (some are relative)
                tasks = []
                for link in links:
                    if link not in self.visited:
                        tasks.append(self._fetch_parse_book(client, link))
                # run tasks concurrently
                await asyncio.gather(*tasks)
                if next_url:
                    to_visit.append(next_url)