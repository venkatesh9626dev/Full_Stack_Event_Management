from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet


class Settings(BaseSettings):
    APP_NAME: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    ALGORITHM: str
    GEOCODING_API_KEY: str
    RAZORPAY_MERCHANT_ID: str
    RAZORPAY_SECRET_KEY: str
    CLOUDINARY_SECRET_KEY: str
    CLOUDINARY_API_KEY: str
    CIPHER_KEY : str

    class Config:
        env_file = ".env"  # Load from .env file




# Create a settings instance
settings = Settings()


cipher = Fernet((settings.CIPHER_KEY).encode())

__all__ = ["settings", "cipher"]
