from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import appsettings

client = AsyncIOMotorClient(appsettings.MONGO_URI)
db = client[appsettings.MONGO_DB]

books_col = db["books"]
changes_col = db["changes"]


async def ensure_indexes():
    await books_col.create_index("source_url", unique=True)
    await books_col.create_index([("category", 1) ("price_excl_vat", 1)])
    await changes_col.create_index("books_id")