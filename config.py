import cloudinary
from decouple import config as de_conf


CLOUDINARY_STORAGE = cloudinary.config(
  cloud_name=de_conf("CLOUD_NAME"),
  api_key=de_conf("API_KEY"),
  api_secret=de_conf("API_SECRET"),
)
