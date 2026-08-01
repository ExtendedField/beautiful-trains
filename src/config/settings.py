from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_PASSWORD: str = "default"
    CACHE_LOCATION: Path = Path("./network_cache/")


settings = Settings()
