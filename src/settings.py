from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PASSWORD: str = 'conductor'
    CACHE_LOCATION: str = f"./network_cache/"


settings = Settings()