from fastapi import APIRouter, Depends, Query
from api.auth import check_api_key
from db.mongo import books_col, changes_col
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from scheduler.jobs import run_crawl_job

router = APIRouter(dependencies=[Depends(check_api_key)])

class BookOut(BaseModel):
    id: str
    name: str
    category: Optional[str]
    price_excl_vat: Optional[float]
    price_incl_vat: Optional[float]
    rating: Optional[int]

@router.get("/books", response_model=List[BookOut])
async def get_books(
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    rating: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    query = {}
    if category:
        query["category"] = category
    if rating:
        query["rating"] = rating
    if min_price is not None or max_price is not None:
        query["price_excl_vat"] = {}
        if min_price is not None:
            query["price_excl_vat"]["$gte"] = min_price
        if max_price is not None:
            query["price_excl_vat"]["$lte"] = max_price
    skip = (page - 1) * page_size
    sort_field = sort_by if sort_by in ("rating","price_excl_vat","num_reviews","name") else "name"
    cursor = books_col.find(query).sort(sort_field, -1 if sort_field != "name" else 1).skip(skip).limit(page_size)
    docs = []
    async for d in cursor:
        docs.append(BookOut(
            id=str(d["_id"]),
            name=d["name"],
            category=d.get("category"),
            price_excl_vat=d.get("price_excl_vat"),
            price_incl_vat=d.get("price_incl_vat"),
            rating=d.get("rating"),
            # availability=d.get("availability"),
            # reviews=d.get("num_reviews"),

        ))
    return docs

@router.get("/books/{book_id}")
async def get_book(book_id: str):
    doc = await books_col.find_one({"_id": ObjectId(book_id)})
    if not doc:
        return {"error": "not found"}
    doc["_id"] = str(doc["_id"])  # Convert _id to string directly
    doc["crawl_timestamp"] = doc["crawl_timestamp"].isoformat()
    return doc

@router.get("/changes")
async def get_changes(limit: int = 50):
    cur = changes_col.find().sort("when", -1).limit(limit)
    out = []
    async for c in cur:
        c["_id"] = str(c["_id"])  # Convert the document's _id
        c["book_id"] = str(c["book_id"])  # Convert the book_id reference
        c["when"] = c["when"].isoformat()
        out.append(c)
    return out

@router.post("/run-crawl-sync")
async def run_crawl_sync():
    await run_crawl_job()   # awaits until crawler finishes
    return {"message": "Crawl finished"}
