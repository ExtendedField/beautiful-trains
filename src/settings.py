from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_PASSWORD: str = "default"
    CACHE_LOCATION: str = f"./network_cache/"


settings = Settings()