import asyncio
import httpx
from utils.config import appsettings
from utils.logger import get_logger


logger = get_logger("client")


async def fetch_html(url: str, client: httpx.AsyncClient,  retries: int = None) -> str:
    retries = retries or appsettings.CRAWL_RETRY
    for attempt in range(1, retries + 1):
        try:
            response = await client.get(url, timeout=appsettings.CRAWL_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as th:
            logger.warning(f"fetch_html failed {url} attempt {attempt}: {th}")
            await asyncio.sleep(1 * attempt)
    raise RuntimeError(f"Failed to getch {url} after {retries} attempts")
