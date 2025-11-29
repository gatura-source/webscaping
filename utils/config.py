from pydantic import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "scrappedbooksdb"
    BASE_URL: str = "https://books.toscrape.com"
    API_KEYS: list[str] = ["devkey123"]  # production: load from secure store
    RATE_LIMIT_PER_HOUR: int = 100
    CRAWL_CONCURRENCY: int = 10
    CRAWL_RETRY: int = 3
    CRAWL_TIMEOUT: int = 20
    SCHEDULER_ENABLED: bool = True
    
    class Config:
        env_file = ".env"


appsettings = Settings()