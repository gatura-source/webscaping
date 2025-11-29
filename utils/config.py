#from pydantic import BaseSettings
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "scrappedbooksdb"
    BASE_URL: str = "https://books.toscrape.com/catalogue"
    API_KEYS: list[str] = ["devkey123"]  # production: load from secure store
    RATE_LIMIT_PER_HOUR: int = 100
    CRAWL_CONCURRENCY: int = 10
    CRAWL_RETRY: int = 3
    CRAWL_TIMEOUT: int = 20
    SCHEDULER_ENABLED: bool = True

    # Redis Configuration
    REDIS_HOST: str = "localhost"  # or "127.0.0.1" or your Redis server IP
    REDIS_PORT: int = 6379  # default Redis port
    REDIS_PASSWORD: Optional[str] = None  # or "your_password" if Redis requires auth
    REDIS_DB: int = 0  # default database (0-15)
    
    class Config:
        env_file = ".env"


appsettings = Settings()