import cloudinary

from settings import settings

cloudinary.config(
    cloud_name="do3rfgh8n",
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET_KEY,
)
