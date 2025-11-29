from fastapi import FastAPI
from api.routes import router as api_router
from scheduler.jobs import start_scheduler
from db.mongo import ensure_indexes
from utils.logger import get_logger
from api.auth import init_redis, close_redis

logger = get_logger("api")

app = FastAPI(title="Books Crawler API")
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    await ensure_indexes()
    start_scheduler()
    await init_redis()

    logger.info("App startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()