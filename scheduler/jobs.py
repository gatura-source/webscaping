from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawler.crawl_manager import Crawler
from utils.config import settings
from utils.logger import get_logger
from db.mongo import ensure_indexes

logger = get_logger("scheduler")

scheduler = AsyncIOScheduler()


async def run_crawl_job():
    logger.info("Starting scheduled crawl job")
    await ensure_indexes()
    crawler = Crawler(settings.BASE_URL)
    await crawler.crawl(f"{settings.BASE_URL}/catalogue/page-1.html")  # books.toscrape specific start
    logger.info("Crawl job finished")


def start_scheduler():
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler disabled")
        return scheduler
    scheduler.add_job(run_crawl_job, "cron", hour=0, minute=30, id="daily_crawl")
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
