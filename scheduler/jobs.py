from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawler.crawler_manager import Crawler
from utils.config import appsettings
from utils.logger import get_logger
from db.mongo import ensure_indexes

logger = get_logger("scheduler")

scheduler = AsyncIOScheduler()


async def run_crawl_job():
    logger.info("Starting scheduled crawl job")
    await ensure_indexes()
    crawler = Crawler(appsettings.BASE_URL)
    await crawler.crawl(f"{appsettings.BASE_URL}/page-1.html")  # books.toscrape specific start
    logger.info("Crawl job finished")


def start_scheduler():
    if not appsettings.SCHEDULER_ENABLED:
        logger.info("Scheduler disabled")
        return scheduler
    scheduler.add_job(run_crawl_job, "cron", hour=0, minute=30, id="daily_crawl")
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
