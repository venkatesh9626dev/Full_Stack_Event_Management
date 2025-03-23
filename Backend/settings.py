from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str 
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    DATABASE_URL: str
    ALGORITHM : str
    GEOCODING_API_KEY : str

    class Config:
        env_file = ".env"  # Load from .env file

# Create a settings instance
settings = Settings()

__all__ = ["settings"]