from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class BookBase(BaseModel):
    name: str
    description: Optional[str]
    category: Optional[str]
    price_excl_vat: Optional[str]
    price_incl_vat: Optional[str]
    availability: Optional[str]
    num_reviews: Optional[int]
    image_url: Optional[HttpUrl]
    rating: Optional[int]


class BookDocument(BookBase):
    source_url: str
    crawl_timestamp: datetime
    status: str = Field(default="Ok")
    content_hash: str
    raw_html: Optional[str]
