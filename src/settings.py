from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PASSWORD: str = 'conductor'

settings = Settings()