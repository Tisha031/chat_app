from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ChatApp"
    DEBUG: bool = True
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

settings = Settings()