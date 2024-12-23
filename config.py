# config.py
from decouple import config

MONGODB_URL = config("MONGODB_URL", default="mongodb://mongodb:27017")
WAREHOUSE_API_URL = config("WAREHOUSE_API_URL")
CLIENT_API_URL = config("CLIENT_API_URL")
WKHTMLTOIMAGE_PATH = config("WKHTMLTOIMAGE_PATH", default="/usr/local/bin/wkhtmltoimage")

